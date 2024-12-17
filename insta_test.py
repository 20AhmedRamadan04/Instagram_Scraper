import instaloader
import requests
import os
import time
import csv
from colorama import Fore, Style
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import re

# Reading login credentials from login_info.txt
with open("login_info.txt", "r") as file:
    login_data = file.read().strip().split(":")
    username = login_data[0]
    password = login_data[1]

# Reading usernames to scrape from usernames.txt
with open("usernames.txt", "r") as file:
    usernames = file.read().splitlines()

# Opening the failed users file to store any failed scraping attempts
failed_users = open("failed_users.txt", "w")

# Starting the scraping process
for scrape_user in usernames:
    try:
        # Logging into Instagram using Instaloader
        loader = instaloader.Instaloader()
        loader.login(username, password)
        # Success message for login with a special character
        print(Fore.GREEN + f"✨✨ Logged in successfully as {username} ✨✨" + Style.RESET_ALL)

        # Accessing the profile of the user to scrape
        try:
            profile = instaloader.Profile.from_username(loader.context, scrape_user)
            Posts_Number = profile.mediacount
            Followers = profile.followers
            Following = profile.followees
            # Success message for accessing profile
            print(Fore.BLUE + f"🌟 Successfully accessed the account {scrape_user} 🌟" + Style.RESET_ALL)
        except instaloader.exceptions.ProfileNotExistsException:
            print(Fore.RED + f"❌ Error: The username {scrape_user} does not exist or cannot be accessed ❌" + Style.RESET_ALL)
            failed_users.write(f"{scrape_user} - Username does not exist\n")
            continue

        # Saving the account details in a CSV file
        account_data = [
            ["Username", scrape_user],
            ["Total Posts", Posts_Number],
            ["Followers", Followers],
            ["Following", Following]
        ]
        with open(f"{scrape_user}_account_data.csv", "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerows(account_data)
        # Success message for saving account data
        print(Fore.YELLOW + f"📊 Account data saved in file: {scrape_user}_account_data.csv 📊" + Style.RESET_ALL)

        # Creating a folder to save the posts
        save_directory = f"{scrape_user}_posts"
        os.makedirs(save_directory, exist_ok=True)
        # Success message for folder creation
        print(Fore.CYAN + f"📂 Post folder created: {save_directory} 📂" + Style.RESET_ALL)

        post_details = []
        
        # Downloading all posts and saving details
        for post in profile.get_posts():
            post_link = f"https://www.instagram.com/p/{post.shortcode}/"
            caption = post.caption if post.caption else "No caption"
            likes = post.likes
            comments = post.comments
            post_date = post.date_utc.strftime("%Y-%m-%d %H:%M:%S")

            post_details.append({
                "link": post_link,
                "caption": caption,
                "likes": likes,
                "comments": comments,
                "date": post_date
            })

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

        # Success message for downloading posts
        print(Fore.GREEN + f"🎥 Downloaded {len(post_details)} posts from {scrape_user} 🎥" + Style.RESET_ALL)

        # Saving the post details in a CSV file
        with open(f"{scrape_user}_posts_details.csv", "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(["Post Link", "Caption", "Likes", "Comments", "Date"])
            for post in post_details:
                writer.writerow([post['link'], post['caption'], post['likes'], post['comments'], post['date']])
        # Success message for saving post details
        print(Fore.YELLOW + f"📝 Post details saved in file: {scrape_user}_posts_details.csv 📝" + Style.RESET_ALL)

        # A. Extract comments from Instagram posts
        comments_data = []
        for post in profile.get_posts():
            try:
                post_link = f"https://www.instagram.com/p/{post.shortcode}/"  # Full post link
                for comment in post.get_comments():
                    comment_owner = comment.owner.username  # Comment owner's username
                    commenter_profile_link = f"https://www.instagram.com/{comment_owner}/"  # Commenter's profile link
                    comments_data.append([post_link, comment_owner, comment.text, commenter_profile_link])  # Add post link and comment details
            except Exception as e:
                print(Fore.RED + f"❌ Error retrieving comments for post {post.shortcode}: {e} ❌" + Style.RESET_ALL)
                time.sleep(10)  # Wait to avoid getting blocked
                continue

        # Save comments along with the commenter's profile link to the same CSV file
        with open(f"{scrape_user}_comments.csv", "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(["Post Link", "Username", "Comment", "Profile Link"])  # Change column to post link
            writer.writerows(comments_data)

        print(Fore.CYAN + f"💬 Comments extracted and saved for {scrape_user}" + Style.RESET_ALL)

        # ================================ Selenium Part ================================

        # Extract post links from CSV file
        def extract_post_links(csv_filename):
            post_links = []
            with open(csv_filename, mode="r", newline='', encoding="utf-8-sig") as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    post_links.append(row[0])  # Links in the first column
            return post_links

        # Load accounts from file
        def load_accounts(file_path):
            with open(file_path, 'r') as file:
                accounts = [line.strip().split(':') for line in file.readlines()]
            return accounts

        # Instagram login
        def login(driver, username, password):
            driver.get("https://www.instagram.com/accounts/login/")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))

            # Enter login data
            driver.find_element(By.NAME, "username").send_keys(username)
            driver.find_element(By.NAME, "password").send_keys(password)
            driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)

            # Wait for login
            time.sleep(5)

        # Extract username from the link
        def extract_username(link):
            match = re.search(r"https://www\.instagram\.com/([^/]+)/", link)
            if match:
                return match.group(1)
            return None

        # Get likers of a post
        def get_likers(driver, post_url):
            driver.get(post_url)

            try:
                # Try to find the like button
                like_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "liked_by")]'))
                )
                like_button.click()

                # Wait for likes dialog to appear
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@role="dialog"]'))
                )
                time.sleep(3)  # Wait for initial loading of the dialog

                # Extract user links from the dialog
                elements = driver.find_elements(By.XPATH, '//div[@role="dialog"]//a[contains(@href, "/") and not(contains(@href, "/p/"))]')
                likers_links = {elem.get_attribute("href") for elem in elements}

                # Extract usernames from links
                likers_usernames = [extract_username(link) for link in likers_links]

                # Start scrolling and retry loading if needed
                max_scroll_retries = 5
                for retry in range(max_scroll_retries):
                    print(f"🔄 Attempt {retry + 1}/{max_scroll_retries} to scroll and load more likers...")
                    time.sleep(2)  # Add waiting time before scrolling
                    
                    # Scroll to the bottom of the dialog
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", driver.find_element(By.XPATH, '//div[@role="dialog"]'))
                    time.sleep(3)  # Wait for new data to load
                    
                    # Extract links again after scrolling
                    elements = driver.find_elements(By.XPATH, '//div[@role="dialog"]//a[contains(@href, "/") and not(contains(@href, "/p/"))]')
                    new_links = {elem.get_attribute("href") for elem in elements}
                    likers_links.update(new_links)

                    # Update usernames
                    likers_usernames = [extract_username(link) for link in likers_links]

                    # Stop if no new links are loaded
                    if len(new_links) == len(likers_links):
                        print("✅ No more new likers found. Exiting scroll loop.")
                        break

            except NoSuchElementException:
                print(Fore.YELLOW + f"⚠️ Warning: This post has no likes or the like button is not found. Skipping... ⚠️" + Style.RESET_ALL)
                likers_usernames = []
                likers_links = []

            except Exception as e:
                print(Fore.RED + f"❌ Error during extracting likers for {post_url}: {e} ❌" + Style.RESET_ALL)
                likers_usernames = []
                likers_links = []

            return likers_usernames, likers_links



        # Save likers data to CSV file
        def save_to_csv(username, post_url, usernames, links):
            filename = f"{scrape_user}_likers_data.csv"
            with open(filename, mode="a", newline='', encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                for username, link in zip(usernames, links):
                    writer.writerow(["Post Link", "Liker Username", "Profile Link"])
                    writer.writerow([post_url, username, link])

        # Main function
        if __name__ == "__main__":
            accounts = load_accounts("Login_info.txt")
            driver = webdriver.Chrome()

            try:
                for username, password in accounts:
                    print(Fore.GREEN + f"✔️ Logging in with account: {username}..." + Style.RESET_ALL)
                    login(driver, username, password)
                    time.sleep(3)

                    # Extract post links from the CSV file created by Instaloader
                    post_links = extract_post_links(f"{scrape_user}_posts_details.csv")
                    if not post_links:
                        print(Fore.YELLOW + "⚠️ No posts found to extract data from. Skipping... ⚠️" + Style.RESET_ALL)

                    for post_url in post_links:
                        print(Fore.CYAN + f"🔍 Extracting likers' data from: {post_url}..." + Style.RESET_ALL)
                        likers_usernames, likers_links = get_likers(driver, post_url)  # Number of likers to extract

                        if likers_usernames:
                            print(Fore.GREEN + f"🎉 Likers and links extracted successfully 🎉" + Style.RESET_ALL)
                        else:
                            print(Fore.RED + f"❌ No likers data found for post: {post_url} ❌" + Style.RESET_ALL)

                        # Save the results to a separate CSV file for each user
                        save_to_csv(username, post_url, likers_usernames, likers_links)

                    break  # Stop after processing the first account (you can modify this as needed)

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
        # In case of an error, write the failed user to the failed users file and continue with the next account
        print(Fore.RED + f"❌ Error scraping data from {scrape_user}: {e} ❌" + Style.RESET_ALL)
        failed_users.write(f"{scrape_user}\n")
        continue  # Skip the failed user and continue with the next

# Closing the failed users file after processing all accounts
failed_users.close()

# Final message indicating the script finished successfully
print(Fore.GREEN + "🎉 Script completed successfully. 🎉" + Style.RESET_ALL)
input("Press Enter to exit...")
