import instaloader
import requests
import os
import time
from colorama import Fore, Style
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import re
from pydantic import BaseModel, ValidationError
from typing import List
import json

# Define Pydantic models
class LoginInfo(BaseModel):
    username: str
    password: str

class Usernames(BaseModel):
    usernames: List[str]

# Define Pydantic models for scraping results
class ProfileData(BaseModel):
    username: str
    total_posts: int
    followers: int
    following: int

class PostDetail(BaseModel):
    link: str
    caption: str
    likes: int
    comments: int
    date: str

class CommentDetail(BaseModel):
    post_link: str
    username: str
    comment: str
    profile_link: str

class FailedUser(BaseModel):
    username: str
    error_message: str

# Read login credentials from JSON file
with open("login_info.json", "r") as file:
    login_info_data = json.load(file)
    login_info = LoginInfo(**login_info_data)
    username = login_info.username
    password = login_info.password

# Read usernames to scrape from JSON file
with open("usernames.json", "r") as file:
    usernames_data = json.load(file)
    usernames = Usernames(**usernames_data).usernames

failed_users: List[FailedUser] = []

# Starting the scraping process
def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def save_failed_users(failed_users: List[FailedUser], filename="failed_users.json"):
    try:
        # Convert failed users list to JSON using Pydantic
        failed_users_data = [user.model_dump() for user in failed_users]
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(failed_users_data, file, indent=4, ensure_ascii=False)
        print(Fore.YELLOW + f"📄 Failed users saved to {filename} 📄" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"❌ Error saving failed users: {e} ❌" + Style.RESET_ALL)

# Starting the scraping process
for scrape_user in usernames:
    try:
        # Logging into Instagram using Instaloader
        loader = instaloader.Instaloader()
        loader.login(username, password)
        print(Fore.GREEN + f"✨✨ Logged in successfully as {username} ✨✨" + Style.RESET_ALL)

        # Accessing the profile of the user to scrape
        try:
            profile = instaloader.Profile.from_username(loader.context, scrape_user)
            profile_data = ProfileData(
                username=scrape_user,
                total_posts=profile.mediacount,
                followers=profile.followers,
                following=profile.followees
            )
            print(Fore.BLUE + f"🌟 Successfully accessed the account {scrape_user} 🌟" + Style.RESET_ALL)
        except instaloader.exceptions.ProfileNotExistsException:
            print(Fore.RED + f"❌ Error: The username {scrape_user} does not exist or cannot be accessed ❌" + Style.RESET_ALL)
            continue

        # Save profile data as JSON
        save_to_json(profile_data.model_dump(), f"{scrape_user}_profile_data.json")
        print(Fore.YELLOW + f"📊 Account data saved in file: {scrape_user}_profile_data.json 📊" + Style.RESET_ALL)

        # Collecting post details
        post_details = []
        for post in profile.get_posts():
            post_details.append(PostDetail(
                link=f"https://www.instagram.com/p/{post.shortcode}/",
                caption=post.caption if post.caption else "No caption",
                likes=post.likes,
                comments=post.comments,
                date=post.date_utc.strftime("%Y-%m-%d %H:%M:%S")
            ).model_dump())

            # Downloading post media (image or video)
            save_directory = f"{scrape_user}_posts"
            os.makedirs(save_directory, exist_ok=True)
            if post.is_video:
                video_url = post.video_url
                response = requests.get(video_url, stream=True)
                video_path = os.path.join(save_directory, f"{scrape_user}_post_{post.shortcode}_video.mp4")
                with open(video_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
            else:
                image_url = post.url
                response = requests.get(image_url, stream=True)
                image_path = os.path.join(save_directory, f"{scrape_user}_post_{post.shortcode}_image.jpg")
                with open(image_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)

            time.sleep(5)

        # Save post details as JSON
        save_to_json(post_details, f"{scrape_user}_posts_details.json")
        print(Fore.GREEN + f"🎥 Post details saved in file: {scrape_user}_posts_details.json 🎥" + Style.RESET_ALL)

        # Extract comments from posts
        comments_data = []
        for post in profile.get_posts():
            try:
                post_link = f"https://www.instagram.com/p/{post.shortcode}/"
                for comment in post.get_comments():
                    comments_data.append(CommentDetail(
                        post_link=post_link,
                        username=comment.owner.username,
                        comment=comment.text,
                        profile_link=f"https://www.instagram.com/{comment.owner.username}/"
                    ).model_dump())
            except Exception as e:
                print(Fore.RED + f"❌ Error retrieving comments for post {post.shortcode}: {e} ❌" + Style.RESET_ALL)
                time.sleep(10)
                continue

        # Save comments as JSON
        save_to_json(comments_data, f"{scrape_user}_comments.json")
        print(Fore.CYAN + f"💬 Comments extracted and saved for {scrape_user}" + Style.RESET_ALL)

        # ================================ Selenium Part ================================

        # Define Pydantic model for Post
        class Post(BaseModel):
            link: str
            caption: str
            likes: int
            comments: int
            date: str

        # Define Pydantic model for Account
        class Account(BaseModel):
            username: str
            password: str

        # Extract post links from JSON file
        def extract_post_links(json_filename):
            try:
                with open(json_filename, mode="r", encoding="utf-8") as file:
                    posts = json.load(file)
                    return [Post(**post).link for post in posts]  # Validate data with Pydantic and extract links
            except (json.JSONDecodeError, ValidationError) as e:
                print(Fore.RED + f"❌ Error reading JSON file: {e} ❌" + Style.RESET_ALL)
                return []

        # Load accounts from JSON file
        def load_accounts(file_path):
            with open(file_path, "r") as json_file:
                account_data = json.load(json_file)  # Load data
                # If the file contains only one account
                if isinstance(account_data, dict):
                    return [Account(**account_data)]
                # If the file contains a list of accounts
                elif isinstance(account_data, list):
                    return [Account(**data) for data in account_data]
                else:
                    raise ValueError("Invalid JSON format for accounts")

        # Instagram login
        def login(driver, username, password):
            driver.get("https://www.instagram.com/accounts/login/")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))

            driver.find_element(By.NAME, "username").send_keys(username)
            driver.find_element(By.NAME, "password").send_keys(password)
            driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
            time.sleep(5)

        # Extract username from the link
        def extract_username(link):
            match = re.search(r"https://www\.instagram\.com/([^/]+)/", link)
            return match.group(1) if match else None

        # Get likers of a post
        def get_likers(driver, post_url):
            driver.get(post_url)
            try:
                like_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "liked_by")]'))
                )
                like_button.click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@role="dialog"]'))
                )
                time.sleep(3)

                elements = driver.find_elements(By.XPATH, '//div[@role="dialog"]//a[contains(@href, "/") and not(contains(@href, "/p/"))]')
                likers_links = {elem.get_attribute("href") for elem in elements}
                likers_usernames = [extract_username(link) for link in likers_links]

                max_scroll_retries = 5
                for retry in range(max_scroll_retries):
                    time.sleep(2)
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", driver.find_element(By.XPATH, '//div[@role="dialog"]'))
                    time.sleep(3)
                    elements = driver.find_elements(By.XPATH, '//div[@role="dialog"]//a[contains(@href, "/") and not(contains(@href, "/p/"))]')
                    new_links = {elem.get_attribute("href") for elem in elements}
                    likers_links.update(new_links)
                    likers_usernames = [extract_username(link) for link in likers_links]
                    if len(new_links) == len(likers_links):
                        break
            except NoSuchElementException:
                likers_usernames, likers_links = [], []
            except Exception as e:
                print(Fore.RED + f"❌ Error during extracting likers for {post_url}: {e} ❌" + Style.RESET_ALL)
                likers_usernames, likers_links = [], []

            return likers_usernames, list(likers_links)

        # Save likers data to JSON file
        def save_to_json(scrape_user, post_url, usernames, links, output_file):
            try:
                data = {
                    "post_url": post_url,
                    "username": scrape_user,
                    "likers": [{"username": uname, "profile_link": link} for uname, link in zip(usernames, links)]
                }
                with open(output_file, mode="a", encoding="utf-8") as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
            except Exception as e:
                print(Fore.RED + f"❌ Error saving to JSON: {e} ❌" + Style.RESET_ALL)

        # Main function
        if __name__ == "__main__":
            accounts = load_accounts("Login_info.json")
            driver = webdriver.Chrome()

            try:
                for account in accounts:
                    print(Fore.GREEN + f"✔️ Logging in with account: {account.username}..." + Style.RESET_ALL)
                    login(driver, account.username, account.password)
                    time.sleep(3)

                    post_links = extract_post_links(f"{scrape_user}_posts_details.json")
                    if not post_links:
                        print(Fore.YELLOW + "⚠️ No posts found to extract data from. Skipping... ⚠️" + Style.RESET_ALL)
                        continue

                    for post_url in post_links:
                        print(Fore.CYAN + f"🔍 Extracting likers' data from: {post_url}..." + Style.RESET_ALL)
                        likers_usernames, likers_links = get_likers(driver, post_url)

                        if likers_usernames:
                            print(Fore.GREEN + f"🎉 Likers and links extracted successfully 🎉" + Style.RESET_ALL)
                        else:
                            print(Fore.RED + f"❌ No likers data found for post: {post_url} ❌" + Style.RESET_ALL)

                        save_to_json(scrape_user, post_url, likers_usernames, likers_links, f"{scrape_user}likers_data.json")
                    break

            except Exception as e:
                print(Fore.RED + f"❌ An error occurred: {e} ❌" + Style.RESET_ALL)

            finally:
                driver.quit()
                print(Fore.MAGENTA + "🛑 Process completed, browser closed. 🛑" + Style.RESET_ALL)
                # Success message after completing the account scraping
                print(Fore.MAGENTA + f"✅ Successfully scraped data from {scrape_user} ✅" + Style.RESET_ALL)

                # Message indicating the script is moving to the next account
                if usernames.index(scrape_user) < len(usernames) - 1:
                    print(Fore.CYAN + f"🌟 Now moving to the next account... 🌟" + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + f"❌ Error processing {scrape_user}: {e} ❌" + Style.RESET_ALL)
        # Add the failed user with the error message to the list.
        failed_users.append(FailedUser(username=scrape_user, error_message=str(e)))
        
        # Save failed users immediately to file
        save_failed_users(failed_users)
        continue

    except Exception as e:
        # In case of an error, write the failed user to the failed users file and continue with the next account
        print(Fore.RED + f"❌ Error scraping data from {scrape_user}: {e} ❌" + Style.RESET_ALL)
        continue  # Skip the failed user and continue with the next

# Final message indicating the script finished successfully
print(Fore.GREEN + "🎉 Script completed successfully. 🎉" + Style.RESET_ALL)
if failed_users:
    save_failed_users(failed_users)
    print(Fore.MAGENTA + "🔔 All failed users have been logged. 🔔" + Style.RESET_ALL)

input("Press Enter to exit...")
