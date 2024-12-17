---

# 🚀 **Instagram Data Scraper** 📊  

A powerful Python script to scrape Instagram profiles, posts, comments, and post likers. This script automates Instagram data collection and saves it into well-organized CSV files for analysis.  

> **Note:** Instagram login credentials and target usernames are read from text files for better reusability.  

---

## 🎯 **Features**  

- **Account Information**: Extract details like followers, following, and total posts.  
- **Media Downloading**: Download all posts (photos & videos) and save locally.  
- **Post Insights**: Collect post links, captions, likes, comments, and post dates.  
- **Comments Scraping**: Extract comments along with commenter usernames and profile links.  
- **Post Likers Extraction** (with Selenium): Retrieve usernames and links of users who liked a post.  

---

## 🛠️ **Tech Stack**  

- **Python Libraries**:  
  - [Instaloader](https://github.com/instaloader/instaloader) - Instagram scraping.  
  - `requests` - Download media files.  
  - `csv` - Save extracted data.  
  - [Selenium](https://www.selenium.dev/) - Automate browser tasks to collect "likes" data.  
  - `colorama` - Add colorful output messages.  

---

## ⚙️ **How It Works**  

1. **Login Credentials**: Add your Instagram credentials in `login_info.txt` (`username:password`).  
2. **Target Usernames**: Add target usernames to `usernames.txt`, one per line.  
3. **Script Workflow**:  
   - Log in to Instagram.  
   - Extract profile data, posts, and comments.  
   - Download photos and videos locally.  
   - Collect likers using Selenium and save everything into CSV files.  
4. **Data Storage**:  
   - Profile details: `username_account_data.csv`  
   - Posts info: `username_posts_details.csv`  
   - Comments: `username_comments.csv`  
   - Likers info: `username_likers_data.csv`  

---

## 🔍 **Known Limitation**  

The current version of the script has a minor issue in **extracting post likers**:  

- Sometimes, **not all likers are retrieved**.  
- The number of extracted likers may vary for each execution.  

> This issue will be addressed in future updates.  

---

## 🚀 **Setup & Run**  

1. **Install Dependencies**:  
   ```bash
   pip install instaloader requests selenium colorama
   ```  

2. **Download WebDriver**:  
   Ensure you have the correct WebDriver for your browser (e.g., ChromeDriver). Place it in your PATH.  

3. **Run the Script**:  
   ```bash
   python instagram_scraper.py
   ```  

4. **Check Outputs**:  
   - Media files saved in folders: `username_posts/`.  
   - CSV files generated with organized data.  

---

## 📂 **File Structure**  

```
📁 Instagram Scraper  
│  
├── instagram_scraper.py      # Main script  
├── login_info.txt            # Your Instagram credentials  
├── usernames.txt             # Target usernames  
├── failed_users.txt          # Failed attempts log  
├── 📂 username_posts         # Folder for media files  
├── username_account_data.csv # Account details  
├── username_posts_details.csv# Post data  
└── username_comments.csv     # Extracted comments  
```

---

## 🤝 **Contributing**  

Feel free to submit issues or pull requests to improve the script. Suggestions for solving the likers extraction issue are highly appreciated!  

---
