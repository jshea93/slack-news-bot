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
    ],
    'Investment Commentary': [
        'https://www.investopedia.com/feedbuilder/feed/getfeed?feedName=rss_headline',
        'https://feeds.marketwatch.com/marketwatch/topstories/', 
        'https://www.noahpinion.blog/feed',
        'https://www.fortmoney.com/feed', 
        'https://www.investing1031.com/feed', 
    ]
}

def fetch_news(feed_urls, max_articles=3):
    """Fetch recent articles from RSS feeds"""
    articles = []
    
    for feed_url in feed_urls:
        try:
            print(f"Fetching: {feed_url}")
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
                print(f"  Found: {article['title'][:50]}...")
                
        except Exception as e:
            print(f"Error fetching {feed_url}: {e}")
            continue
    
    return articles

def format_briefing():
    """Format all articles into a nice Slack message"""
    
    message = f"*Morning Briefing - {datetime.now().strftime('%B %d, %Y')}*\n\n"
    
    total_articles = 0
    
    for category, feeds in RSS_FEEDS.items():
        print(f"\nProcessing category: {category}")
        
        # Get articles for this category
        category_articles = fetch_news(feeds, max_articles=3)
        
        if category_articles:
            message += f"*{category.upper()}*\n"
            
            for article in category_articles:
                # Format: bullet point, title, link, source
                message += f"• *{article['title']}*\n"
                message += f"  <{article['link']}|Read more> · _{article['source']}_\n\n"
                total_articles += 1
            
            message += "\n"
    
    # Add footer
    message += f"Total articles: {total_articles} | Generated at {datetime.now().strftime('%I:%M %p EST')}"
    
    print(f"\nFormatted {total_articles} total articles")
    
    return message

def send_to_slack(message):
    """Send formatted message to Slack"""
    
    if not SLACK_WEBHOOK_URL:
        print("Error: SLACK_WEBHOOK_URL environment variable not set!")
        sys.exit(1)
    slack_data = {
    'text': message,
    'username': 'News Bot',
    'icon_emoji': ':newspaper:',
    'unfurl_links': False,
    'unfurl_media': False
    
    }
    
    try:
        print("\nSending to Slack...")
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=slack_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("Successfully sent to Slack!")
            return True
        else:
            print(f"Slack Error: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error sending to Slack: {e}")
        return False

def main():
    """Main function to run the bot"""
    print("=" * 50)
    print("SLACK NEWS BOT STARTING")
    print("=" * 50)
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Format the briefing
    briefing = format_briefing()
    
    # Send to Slack
    success = send_to_slack(briefing)
    
    print("\n" + "=" * 50)
    if success:
        print("BOT COMPLETED SUCCESSFULLY")
    else:
        print("BOT COMPLETED WITH ERRORS")
    print("=" * 50)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
