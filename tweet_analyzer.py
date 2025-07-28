import json
import datetime
from datetime import timezone
import os

def parse_twitter_date(date_string):
    """Parse Twitter date format: 'Mon Jul 28 02:04:40 +0000 2025'"""
    try:
        dt = datetime.datetime.strptime(date_string, '%a %b %d %H:%M:%S %z %Y')
        return dt
    except ValueError as e:
        print(f"Error parsing date: {date_string} - {e}")
        return None

def analyze_tweets(input_file):
    """Analyze tweet dates and provide statistics"""
    print(f"Analyzing tweets from {input_file}...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            tweets = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return
    
    print(f"Total tweets found: {len(tweets)}")
    
    # Collect all valid tweet dates
    tweet_dates = []
    now = datetime.datetime.now(timezone.utc)
    
    for tweet in tweets:
        if tweet.get('type') == 'tweet':
            tweet_date = parse_twitter_date(tweet.get('createdAt', ''))
            if tweet_date:
                tweet_dates.append(tweet_date)
    
    if not tweet_dates:
        print("No valid tweet dates found!")
        return
    
    # Sort dates
    tweet_dates.sort()
    
    # Calculate statistics
    oldest_tweet = tweet_dates[0]
    newest_tweet = tweet_dates[-1]
    
    print(f"\nDate Range:")
    print(f"  Oldest tweet: {oldest_tweet}")
    print(f"  Newest tweet: {newest_tweet}")
    print(f"  Time span: {newest_tweet - oldest_tweet}")
    
    # Count tweets by hour ranges
    print(f"\nTweets by time ranges:")
    for hours in [1, 6, 12, 24, 48, 72, 168]:  # 1h, 6h, 12h, 1d, 2d, 3d, 1w
        cutoff_time = now - datetime.timedelta(hours=hours)
        count = sum(1 for date in tweet_dates if date >= cutoff_time)
        print(f"  Past {hours} hours: {count} tweets")
    
    # Show recent tweets
    print(f"\nMost recent tweets:")
    recent_tweets = []
    for tweet in tweets:
        if tweet.get('type') == 'tweet':
            tweet_date = parse_twitter_date(tweet.get('createdAt', ''))
            if tweet_date:
                recent_tweets.append((tweet_date, tweet))
    
    recent_tweets.sort(key=lambda x: x[0], reverse=True)
    
    for i, (date, tweet) in enumerate(recent_tweets[:5]):
        print(f"\n  {i+1}. {date}")
        print(f"     ID: {tweet.get('id')}")
        print(f"     Text: {tweet.get('text', '')[:80]}...")
        print(f"     Author: {tweet.get('author', {}).get('userName', 'Unknown')}")

def filter_tweets_by_hours(input_file, output_file, hours):
    """Filter tweets by hours and save to new file"""
    print(f"Filtering tweets from past {hours} hours...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            tweets = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return
    
    cutoff_time = datetime.datetime.now(timezone.utc) - datetime.timedelta(hours=hours)
    filtered_tweets = []
    
    for tweet in tweets:
        if tweet.get('type') == 'tweet':
            tweet_date = parse_twitter_date(tweet.get('createdAt', ''))
            if tweet_date and tweet_date >= cutoff_time:
                filtered_tweets.append(tweet)
    
    print(f"Found {len(filtered_tweets)} tweets within past {hours} hours")
    
    # Save filtered tweets
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_tweets, f, indent=2, ensure_ascii=False)
        print(f"Filtered tweets saved to {output_file}")
    except Exception as e:
        print(f"Error saving filtered tweets: {e}")

def main():
    input_file = 'fire_tweets.json'
    
    if not os.path.exists(input_file):
        print(f"Input file {input_file} not found!")
        return
    
    # First analyze the tweets
    analyze_tweets(input_file)
    
    # Ask user for filtering
    print(f"\n" + "="*50)
    print("Options:")
    print("1. Filter tweets from past 74 hours")
    print("2. Filter tweets from past 24 hours")
    print("3. Filter tweets from past 7 days")
    print("4. Custom hours")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        hours = 74
        output_file = 'cleaned_fire_tweets_74h.json'
    elif choice == "2":
        hours = 24
        output_file = 'cleaned_fire_tweets_24h.json'
    elif choice == "3":
        hours = 168  # 7 days
        output_file = 'cleaned_fire_tweets_7d.json'
    elif choice == "4":
        try:
            hours = int(input("Enter number of hours: "))
            output_file = f'cleaned_fire_tweets_{hours}h.json'
        except ValueError:
            print("Invalid input. Using 74 hours as default.")
            hours = 74
            output_file = 'cleaned_fire_tweets_74h.json'
    else:
        print("Invalid choice. Using 74 hours as default.")
        hours = 74
        output_file = 'cleaned_fire_tweets_74h.json'
    
    filter_tweets_by_hours(input_file, output_file, hours)

if __name__ == "__main__":
    main() 