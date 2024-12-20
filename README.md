```
# Instagram Scraper 🚀📸

Welcome to the **Instagram Scraper**! ✨ The ultimate tool to extract Instagram data, from profiles to posts, comments, likes, and more. Perfect for data analysis, marketing research, or just diving deeper into Instagram data!

## 📌 Key Features

- **Profile Data Extraction**: Get detailed insights about any Instagram profile - number of posts, followers, and following. 
- **Post Details**: Extract caption, likes, comments, post date, and even download images/videos!
- **Comments Scraping**: Pull all comments on posts with usernames and profile links.
- **Likes Extraction**: Retrieve users who liked a post, including usernames and profile links (note the current limitation below).
- **Error Logging**: Automatically save all failed attempts in `failed_accounts.json` and `failed_users.json` for easy troubleshooting.

## ⚠️ Known Issue - Likers Data

There's a small glitch with extracting the full list of people who liked a post. Sometimes, not all likers are extracted, and the number varies with each scrape. This will be addressed in upcoming updates. Stay tuned! 🚧

## 🚀 How It Works

1. **Login**: Logs into Instagram using your credentials stored in a `login_info.json` file.
2. **Scraping**: Gathers profile data, posts, comments, and likes using **Instaloader** and **Selenium**.
3. **Data Export**: All data is neatly organized and saved in JSON files for further analysis.
4. **Error Handling**: Any login or scraping issues are logged in the `failed_accounts.json` and `failed_users.json` files, making it easy to keep track of errors.

## 💡 Setup & Installation

### Requirements:
- Python 3.x
- Instaloader
- Selenium
- Pydantic
- Requests
- Colorama
- ChromeDriver (or GeckoDriver)

### Step 1: Install Dependencies
Run this in your terminal to install the required packages:
```bash
pip install instaloader selenium pydantic requests colorama

### Step 2: Set Up Your WebDriver
Make sure **ChromeDriver** or **GeckoDriver** is installed and added to your system’s PATH.

## 📋 How To Use

1. **Add Your Login Details**: Open the `login_info.json` file and insert your Instagram username and password.
2. **Add Usernames to Scrape**: In `usernames.json`, add a list of Instagram profiles you want to scrape data from.
3. **Run the Script**: 
```bash
python instagram_scraper.py

This will start scraping data from the listed profiles. You will get the following outputs:

- **Profile Data**: Saved as `<username>_profile_data.json`
- **Post Details**: Saved as `<username>_posts_details.json`
- **Comments**: Saved as `<username>_comments.json`
- **Likers Data**: Saved as `<username>_likers_data.json` (note the issue mentioned above)

### ⚠️ Failed Accounts and Users:
If any account or user fails during the scraping process, their details will be saved in:
- **`failed_accounts.json`**: Contains accounts with login or access issues.
- **`failed_users.json`**: Contains users with issues during scraping (e.g., missing posts or comments).

### Example Output:

- **Profile Data**:
  ```json
  {
    "username": "john_doe",
    "total_posts": 150,
    "followers": 1200,
    "following": 350
  }
  

- **Post Details**:
  ```json
  {
    "link": "https://www.instagram.com/p/abc123/",
    "caption": "Amazing day at the beach! 🏖️",
    "likes": 1500,
    "comments": 50,
    "date": "2024-12-20 14:30:00"
  }
  

- **Likers Data** (Limited due to current issue):
  ```json
  {
    "post_url": "https://www.instagram.com/p/abc123/",
    "username": "john_doe",
    "likers": [
      {"username": "alice", "profile_link": "https://www.instagram.com/alice/"},
      {"username": "bob", "profile_link": "https://www.instagram.com/bob/"}
    ]
  }
  

## 🛠️ Contributing

Want to make it even better? 🤩 Feel free to:
- Fork the repo
- Add features or fix bugs
- Submit a pull request

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for more details.

---

🚨 **Important**: Be aware of Instagram’s terms of service when using this tool. Avoid scraping in ways that violate their policies or disrupt their platform.

### 🔔 **Disclaimer**:
Since Instagram may temporarily ban accounts for excessive scraping, it's highly recommended to use a **disposable account** for this purpose, one that doesn’t affect your personal Instagram experience. Use it carefully to avoid any disruptions in service. ⚠️

---

Ready to dive in? Let's get scraping and have some fun with Instagram data! 😎🎉
```
