import instaloader
import requests
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import csv
import re
from colorama import Fore, Style

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

        # Saving the post details and comments in a CSV file
        with open(f"{scrape_user}_posts_details.csv", "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(["Post Link", "Caption", "Likes", "Comments", "Date"])
            for post in post_details:
                writer.writerow([post['link'], post['caption'], post['likes'], post['comments'], post['date']])
        # Success message for saving post details and comments
        print(Fore.YELLOW + f"📝 Post details and comments saved in file: {scrape_user}_posts_details.csv 📝" + Style.RESET_ALL)

        # Now extracting comments using Selenium
        driver = webdriver.Chrome()
        driver.get("https://www.instagram.com/")
        time.sleep(2)
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(5)

        # Extracting comments from all posts
        for post in post_details:
            post_url = post["link"]
            driver.get(post_url)
            time.sleep(5)

            # Scrolling down to load more comments
            for _ in range(50):
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
                time.sleep(2)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            comments = soup.find_all('div', {'class': '_a9zr'})

            if comments:
                comments = comments[1:]  # Skip the first one as it's not a comment

            decoded_comments = []

            # Extracting and cleaning up the comments
            for comment in comments:
                raw_text = comment.text.strip()
                clean_text = raw_text.encode("utf-8", "ignore").decode("utf-8")

                match = re.match(r"^(\w+)(.+)$", clean_text)
                if match:
                    username = match.group(1)  # Extracting the username
                    comment_text = match.group(2)  # Extracting the comment text

                    comment_text = re.sub(r"\d+[a-zA-Z]+.*", "", comment_text).strip()

                    decoded_comments.append([username, comment_text])

            # Saving comments in the post details file
            with open(f"{scrape_user}_posts_details.csv", "a", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                for comment in decoded_comments:
                    writer.writerow([post["link"], post["caption"], post["likes"], post["comments"], post["date"], comment[0], comment[1]])

        # Success message for extracting comments
        print(Fore.GREEN + f"💬 Comments extracted and saved in file: {scrape_user}_posts_details.csv 💬" + Style.RESET_ALL)

        driver.quit()

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
print(Fore.GREEN + "🎉 Script completed successfully. Press any key to exit. 🎉" + Style.RESET_ALL)
input("Press Enter to exit...")