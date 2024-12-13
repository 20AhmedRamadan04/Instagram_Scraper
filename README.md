---

# Instagram Data Scraper ✨

Welcome to the **Instagram Data Scraper**! This Python-based script helps you gather valuable data from Instagram accounts, including profile details, posts, and comments. Whether you're conducting research or simply curious about the content of Instagram profiles, this tool is designed to make the process easier and more efficient.

## Features 🔥
- **Login to Instagram**: Securely log into Instagram using your credentials.
- **Scrape Profile Data**: Collect basic profile information like total posts, followers, and following.
- **Download Posts**: Automatically download images and videos from user profiles.
- **Extract Comments**: Use Selenium to extract and save comments from posts.
- **Error Handling**: If a profile can't be accessed, the username is logged for future review.

## Prerequisites ⚙️
Before using this script, ensure you have the following Python packages installed:

```bash
pip install instaloader requests selenium beautifulsoup4 colorama
```

Additionally, ensure you have a compatible browser driver installed (e.g., ChromeDriver) to use with **Selenium**.

## Setup Instructions 📝

1. **Login Information**:
   - Create a `login_info.txt` file and store your Instagram login credentials in the following format:
     ```
     username:password
     ```

2. **Usernames to Scrape**:
   - Create a `usernames.txt` file and list the Instagram usernames you want to scrape, one per line.

3. **Log Failed Scraping Attempts**:
   - If the script encounters errors while scraping a username, it will log the failed users into `failed_users.txt`.

4. **Script Output**:
   - The script will create the following output files for each user:
     - `username_account_data.csv`: Contains the user's profile information (posts, followers, following).
     - `username_posts_details.csv`: Contains details of all posts including captions, likes, comments, and dates.

## How It Works 🚀

1. **Login**:
   The script starts by logging into Instagram using the credentials provided in `login_info.txt`.

2. **Scraping Profile**:
   For each username in `usernames.txt`, the script:
   - Collects profile information like total posts, followers, and following.
   - Downloads all media (images/videos) from the user's profile into a folder named after the username.

3. **Downloading Posts**:
   The script downloads images and videos from the posts and saves them to a directory called `username_posts`.

4. **Extracting Comments**:
   Using **Selenium**, the script automatically scrolls through posts and extracts the comments, saving them in the CSV file.

5. **Error Handling**:
   If an error occurs, such as an invalid username or inaccessible profile, the username is logged in the `failed_users.txt` file for later review.

## Example Output 💾

The script prints color-coded messages to indicate the progress and any errors encountered during the scraping process:
- **Green**: Success (e.g., logged in, post downloaded).
- **Red**: Error (e.g., profile not found).
- **Blue**: Progress updates (e.g., starting scraping for a user).

## Files Created 📂
- **`username_account_data.csv`**: Contains account data such as total posts, followers, and following.
- **`username_posts_details.csv`**: Contains post details (link, caption, likes, comments, and date).
- **`failed_users.txt`**: Logs usernames that failed to scrape.

## Important Notes ⚠️

- **Login Security**: Always ensure you are using secure login credentials.
- **Instagram's Terms of Service**: Please ensure you are following Instagram's Terms of Service when using this tool.
- **Selenium WebDriver**: Make sure to install and configure a compatible WebDriver (like ChromeDriver) for Selenium.

## Final Words 🌟
This script is designed to simplify Instagram data scraping for analysis and research purposes. It automates the process of logging in, downloading posts, and extracting comments with ease.

Happy scraping! 🎉

---
