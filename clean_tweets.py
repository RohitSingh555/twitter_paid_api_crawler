import json
import datetime
from datetime import timezone
import os

def parse_twitter_date(date_string):
    """Parse Twitter date format: 'Mon Jul 28 02:04:40 +0000 2025'"""
    try:
        # Parse the Twitter date format
        dt = datetime.datetime.strptime(date_string, '%a %b %d %H:%M:%S %z %Y')
        return dt
    except ValueError as e:
        print(f"Error parsing date: {date_string} - {e}")
        return None

def is_within_hours(tweet_date, hours=74):
    """Check if tweet is within the specified hours from now"""
    if tweet_date is None:
        return False
    
    now = datetime.datetime.now(timezone.utc)
    time_diff = now - tweet_date
    return time_diff.total_seconds() <= (hours * 3600)

def clean_tweet(tweet):
    """Extract only essential fields from a tweet"""
    cleaned = {
        'id': tweet.get('id'),
        'text': tweet.get('text'),
        'createdAt': tweet.get('createdAt'),
        'url': tweet.get('url'),
        'likeCount': tweet.get('likeCount', 0),
        'retweetCount': tweet.get('retweetCount', 0),
        'replyCount': tweet.get('replyCount', 0),
        'viewCount': tweet.get('viewCount', 0),
        'lang': tweet.get('lang'),
        'isReply': tweet.get('isReply', False),
        'inReplyToId': tweet.get('inReplyToId'),
        'conversationId': tweet.get('conversationId')
    }
    
    # Add author information if available
    if 'author' in tweet and tweet['author']:
        author = tweet['author']
        cleaned['author'] = {
            'id': author.get('id'),
            'userName': author.get('userName'),
            'name': author.get('name'),
            'isVerified': author.get('isVerified', False),
            'followers': author.get('followers', 0),
            'following': author.get('following', 0),
            'profilePicture': author.get('profilePicture')
        }
    
    return cleaned

def process_tweets(input_file, output_file, hours=74):
    """Process tweets and filter by creation date"""
    print(f"Reading tweets from {input_file}...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            tweets = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return
    
    print(f"Total tweets found: {len(tweets)}")
    
    # Filter tweets by date
    filtered_tweets = []
    cutoff_time = datetime.datetime.now(timezone.utc) - datetime.timedelta(hours=hours)
    
    for tweet in tweets:
        if tweet.get('type') == 'tweet':
            tweet_date = parse_twitter_date(tweet.get('createdAt', ''))
            if tweet_date and tweet_date >= cutoff_time:
                cleaned_tweet = clean_tweet(tweet)
                filtered_tweets.append(cleaned_tweet)
    
    print(f"Tweets within past {hours} hours: {len(filtered_tweets)}")
    
    # Save filtered tweets
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_tweets, f, indent=2, ensure_ascii=False)
        print(f"Filtered tweets saved to {output_file}")
    except Exception as e:
        print(f"Error saving filtered tweets: {e}")
    
    return filtered_tweets

def main():
    input_file = 'fire_tweets.json'
    output_file = 'cleaned_fire_tweets.json'
    hours = 74
    
    if not os.path.exists(input_file):
        print(f"Input file {input_file} not found!")
        return
    
    print(f"Processing tweets from the past {hours} hours...")
    filtered_tweets = process_tweets(input_file, output_file, hours)
    
    if filtered_tweets:
        print(f"\nSample of filtered tweets:")
        for i, tweet in enumerate(filtered_tweets[:3]):
            print(f"\nTweet {i+1}:")
            print(f"  ID: {tweet['id']}")
            print(f"  Text: {tweet['text'][:100]}...")
            print(f"  Created: {tweet['createdAt']}")
            print(f"  Author: {tweet.get('author', {}).get('userName', 'Unknown')}")

if __name__ == "__main__":
    main() 