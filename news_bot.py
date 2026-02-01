#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Slack Daily News Bot
Fetches news from RSS feeds and sends a formatted briefing to Slack
"""

import feedparser
import requests
from datetime import datetime
import os
import sys

# Get Slack webhook from environment variable
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')

# RSS Feeds organized by category
RSS_FEEDS = {
    'Banking & Lending': [
        'https://www.americanbanker.com/feed',
        'https://www.housingwire.com/feed/',
    ],
    'Salesforce': [
        'https://www.salesforceben.com/feed/',
    ],
    'Python & Tech': [
        'https://realpython.com/atom.xml',
    ]
}

def fetch_news(feed_urls, max_articles=3):
    """Fetch recent articles from RSS feeds"""
    articles = []
    
    for feed_url in feed_urls:
        try:
            print(f"📡 Fetching: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            # Get source name
            source_name = feed.feed.get('title', 'Unknown Source')
            
            # Get articles
            for entry in feed.entries[:max_articles]:
                article = {
                    'title': entry.get('title', 'No title'),
                    'link': entry.get('link', ''),
                    'source': source_name,
                    'published': entry.get('published', 'Unknown date')
                }
                articles.append(article)
                print(f"  ✓ Found: {article['title'][:50]}...")
                
        except Exception as e:
            print(f"❌ Error fetching {feed_url}: {e}")
            continue
    
    return articles

def format_briefing():
    """Format all articles into a nice Slack message"""
    
    message = f"📰 *Morning Briefing - {datetime.now().strftime('%B %d, %Y')}*\n\n"
    
    total_articles = 0
    
    for category, feeds in RSS_FEEDS.items():
        print(f"\n📂 Processing category: {category}")
        
        # Get articles for this category
        category_articles = fetch_news(feeds, max_articles=3)
        
        if category_articles:
            message += f"*━━━ {category.upper()} ━━━*\n"
            
            for article in category_articles:
                # Format: bullet point, title, link, source
                message += f"• *{article['title']}*\n"
                message += f"  <{article['link']}|Read more> · _{article['source']}_\n\n"
                total_articles += 1
            
            message += "\n"
    
    # Add footer
    message += f"─────────────────────\n"
    message += f"📊 Total articles: {total_articles} | ⏰ Generated at {datetime.now().strftime('%I:%M %p EST')}"
    
    print(f"\n✅ Formatted {total_articles} total articles")
    
    return message

def send_to_slack(message):
    """Send formatted message to Slack"""
    
    if not SLACK_WEBHOOK_URL:
        print("❌ Error: SLACK_WEBHOOK_URL environment variable not set!")
        sys.exit(1)
    
    slack_data = {
        'text': message,
        'unfurl_links': False,
        'unfurl_media': False
    }
    
    try:
        print("\n📤 Sending to Slack...")
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=slack_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Successfully sent to Slack!")
            return True
        else:
            print(f"❌ Slack Error: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending to Slack: {e}")
        return False

def main():
    """Main function to run the bot"""
    print("=" * 50)
    print("🤖 SLACK NEWS BOT STARTING")
    print("=" * 50)
    print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Format the briefing
    briefing = format_briefing()
    
    # Send to Slack
    success = send_to_slack(briefing)
    
    print("\n" + "=" * 50)
    if success:
        print("✅ BOT COMPLETED SUCCESSFULLY")
    else:
        print("❌ BOT COMPLETED WITH ERRORS")
    print("=" * 50)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

4. Scroll down and click **"Commit new file"**
   - In the commit message box, you can leave the default or write: "Add main news bot script"
   - Click **"Commit new file"**

---

### **Step 4: Create Requirements File**

This tells GitHub what Python packages to install.

1. Click **"Add file"** → **"Create new file"**
2. Name: `requirements.txt`
3. Paste this:
```
feedparser==6.0.10
requests==2.31.0

Click "Commit new file"


Part 3: Set Up GitHub Actions Workflow
Step 5: Create Workflow Directory

Click "Add file" → "Create new file"
In the filename box, type: .github/workflows/daily-news.yml

This will automatically create the folders


Paste this workflow configuration:

yamlname: Daily News Briefing

on:
  schedule:
    # Run at 11:00 AM UTC (6:00 AM EST) every day
    # Adjust time as needed for your timezone
    - cron: '0 11 * * *'
  
  # Allow manual triggering for testing
  workflow_dispatch:

jobs:
  send-briefing:
    runs-on: ubuntu-latest
    
    steps:
      # Step 1: Get the code
      - name: Checkout repository
        uses: actions/checkout@v3
      
      # Step 2: Set up Python
      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      # Step 3: Install dependencies
      - name: Install Python packages
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      # Step 4: Run the bot
      - name: Run news bot
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: |
          python news_bot.py
```

4. Click **"Commit new file"**

**Note on timing:** The cron schedule `'0 11 * * *'` means:
- 11:00 AM UTC = 6:00 AM EST
- If you want a different time:
  - 7 AM EST = `'0 12 * * *'`
  - 8 AM EST = `'0 13 * * *'`
  - Use this tool to help: https://crontab.guru

---

## **Part 4: Add Your Slack Webhook Securely**

### **Step 6: Add Secret to Repository**

GitHub Secrets keep your webhook URL safe and hidden.

1. In your repository, click **"Settings"** tab (top of page)
2. In the left sidebar, click **"Secrets and variables"** → **"Actions"**
3. Click **"New repository secret"**
4. Fill in:
   - **Name:** `SLACK_WEBHOOK_URL`
   - **Secret:** Paste your Slack webhook URL (the one that starts with `https://hooks.slack.com/services/...`)
5. Click **"Add secret"**

✅ Your webhook is now securely stored!

---

## **Part 5: Test Your Bot!**

### **Step 7: Manual Test Run**

Before waiting for the scheduled time, let's test it now:

1. Click the **"Actions"** tab (top of your repository)
2. You should see "Daily News Briefing" in the left sidebar
3. Click on it
4. Click the **"Run workflow"** button (on the right)
5. Click the green **"Run workflow"** button in the dropdown
6. Wait about 30-60 seconds
7. Refresh the page

You should see a workflow run appear. Click on it to see the details.

---

### **Step 8: Check the Results**

1. Click on the workflow run
2. Click on **"send-briefing"** to see the job details
3. Click on each step to expand and see the logs
4. You should see output like:
```
   🤖 SLACK NEWS BOT STARTING
   📡 Fetching: https://www.americanbanker.com/feed
   ✓ Found: [article title]
   ...
   ✅ Successfully sent to Slack!
