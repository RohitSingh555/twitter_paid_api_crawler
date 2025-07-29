"""
tweet_fire_search.py
--------------------
Fetches the latest fire‑related tweets across U.S. states and core EMS accounts.

Usage:
    export TWITTER_API_KEY="YOUR_API_KEY"
    python tweet_fire_search.py
"""

import os
import json
import time
import requests
from typing import List, Dict, Any
from datetime import datetime

# Configuration
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
if not TWITTER_API_KEY:
    print("Error: TWITTER_API_KEY environment variable is required")
    print("Please set your Twitter API key in a .env file or environment variable.")
    exit(1)

# Get hours from environment variable, default to 72 if not set
SEARCH_HOURS = os.getenv('SEARCH_HOURS', '72')
try:
    SEARCH_HOURS = int(SEARCH_HOURS)
except ValueError:
    print(f"Warning: Invalid SEARCH_HOURS value '{SEARCH_HOURS}', using default 72 hours")
    SEARCH_HOURS = 72

# Constants
US_STATES = [
    "Arizona", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia",
    # "Idaho", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
    # "Maryland", "Michigan", "Minnesota", "Mississippi", "Montana", "Nebraska",
    # "Nevada", "New Hampshire", "New Jersey", "New Mexico", "North Carolina",
    # "North Dakota", "Ohio", "Oklahoma", "Oregon", "South Carolina", "Tennessee",
    # "Texas", "US Virgin Islands", "Utah", "Vermont", "Virginia", "Washington",
    # "West Virginia", "Wisconsin", "Wyoming", "DC"
]

FIRE_KEYWORDS = [
    "house fire", "apartment complex", "store fire", "commercial fire",
    # "restaurant fire", "warehouse fire", "business fire", "pipe burst",
    # "building fire", "structure fire", "residential fire", "industrial fire"
    # "factory fire", "office fire", "school fire", "church fire", "hospital fire",
    # "hotel fire", "motel fire", "barn fire", "garage fire", "condo fire",
    # "duplex fire", "mobile home fire", "trailer fire", "fire destroys",
    # "fire damages", "fire guts", "fire ravages", "fire breaks out",
    # "fire incident", "fire reported", "fire leaves", "fire causes damage",
    # "fire evacuation", "firefighters battle blaze", "fire under investigation",
    # "arson fire", "wildfire damages", "fire displaces", "fire ruins",
    # "fire engulfs", "fire consumes building", "fire tears through",
    # "fire rips through"
]

FIRE_ACCOUNTS = [
    "@DFWscanner", "@DallasTexasTV", "@NWSSanAntonio", "@FriscoFFD", "@RedCrossTXGC",
    "@whatsupTucson", "@WacoTXFire", "@SouthMetroPIO", "@NWSBoulder", "@SeattleFire",
    "@CityofMiamiFire", "@PeterNewcomb41", "@ffxfirerescue", "@ScannerRadioDFW",
    "@sfgafirerescue", "@THEJFRD", "@ChicagoMWeather", "@ToledoFire", "@AustinFireInfo"
]

FIRE_SEARCH_COMBINATIONS = [f"{state} {kw}" for state in US_STATES for kw in FIRE_KEYWORDS]

def get_all_fire_accounts() -> List[str]:
    """Returns fire account handles without '@' prefix."""
    return [account[1:] for account in FIRE_ACCOUNTS]

def get_all_fire_search_combinations() -> List[str]:
    """Returns all fire search combinations."""
    return FIRE_SEARCH_COMBINATIONS

def handle_rate_limit(response: requests.Response) -> None:
    """Handle rate limiting by sleeping for a fixed time."""
    if response.status_code == 429:
        print("Rate limited. Sleeping for 60 seconds...")
        time.sleep(60)

def fetch_tweets(query: str, max_results: int = 20) -> List[Dict[str, Any]]:
    """Fetch tweets from Kaito Twitter API for a given query."""
    url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
    headers = {
        "X-API-Key": TWITTER_API_KEY
    }
    params = {
        "query": f"{query} within_time:{SEARCH_HOURS}h",
        "queryType": "Latest"
    }
    print(SEARCH_HOURS)
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 429:
            handle_rate_limit(response)
            # Retry the request after rate limit handling
            response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            tweets = data.get('tweets', [])
            # Limit to max_results
            return tweets[:max_results]
        else:
            print(f"Error fetching tweets for query '{query}': {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"Exception while fetching tweets for query '{query}': {str(e)}")
        return []

def fetch_user_tweets(username: str, max_results: int = 20) -> List[Dict[str, Any]]:
    """Fetch latest tweets from a specific user using Kaito Twitter API."""
    url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
    headers = {
        "X-API-Key": TWITTER_API_KEY
    }
    params = {
        "query": f"from:{username} within_time:{SEARCH_HOURS}h",
        "queryType": "Latest"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 429:
            handle_rate_limit(response)
            # Retry the request after rate limit handling
            response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            tweets = data.get('tweets', [])
            # Limit to max_results
            return tweets[:max_results]
        else:
            print(f"Error fetching tweets for user '{username}': {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"Exception while fetching tweets for user '{username}': {str(e)}")
        return []

def deduplicate_tweets(tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate tweets based on tweet ID."""
    seen_ids = set()
    unique_tweets = []
    
    for tweet in tweets:
        tweet_id = tweet.get('id')
        if tweet_id and tweet_id not in seen_ids:
            seen_ids.add(tweet_id)
            unique_tweets.append(tweet)
    
    return unique_tweets

def save_tweets_to_file(tweets: List[Dict[str, Any]], filename: str = "fire_tweets.json") -> None:
    """Save tweets to JSON file with deduplication."""
    # Load existing tweets if file exists
    existing_tweets = []
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                existing_tweets = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            existing_tweets = []
    
    # Combine existing and new tweets
    all_tweets = existing_tweets + tweets
    
    # Deduplicate by tweet ID
    unique_tweets = deduplicate_tweets(all_tweets)
    
    # Save to file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(unique_tweets, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(unique_tweets)} unique tweets to {filename}")

def main():
    """Main routine to fetch and save fire-related tweets."""
    print("Starting fire tweet search...")
    
    # Generate unique timestamped filename
    dt_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"fire_tweets_72h_{dt_str}.json"
    
    total_queries = 0
    total_tweets_fetched = 0
    
    # Fetch tweets for search combinations
    search_combinations = get_all_fire_search_combinations()
    print(f"Fetching tweets for {len(search_combinations)} search combinations...")
    
    for i, query in enumerate(search_combinations, 1):
        print(f"Query {i}/{len(search_combinations)}: {query}")
        tweets = fetch_tweets(query)
        
        if tweets:
            total_tweets_fetched += len(tweets)
            # Save immediately after each successful query
            save_tweets_to_file(tweets, output_file)
            print(f"  -> Fetched {len(tweets)} tweets")
        
        total_queries += 1
        
        # Small delay to be respectful to the API
        time.sleep(0.1)
    
    # Fetch tweets from fire accounts
    fire_accounts = get_all_fire_accounts()
    print(f"\nFetching tweets from {len(fire_accounts)} fire accounts...")
    
    for i, username in enumerate(fire_accounts, 1):
        print(f"Account {i}/{len(fire_accounts)}: {username}")
        tweets = fetch_user_tweets(username)
        
        if tweets:
            total_tweets_fetched += len(tweets)
            # Save immediately after each successful query
            save_tweets_to_file(tweets, output_file)
            print(f"  -> Fetched {len(tweets)} tweets")
        
        total_queries += 1
        
        # Small delay to be respectful to the API
        time.sleep(0.1)
    
    # Print final summary
    print(f"\n=== Final Summary ===")
    print(f"Total queries run: {total_queries}")
    print(f"Total tweets fetched: {total_tweets_fetched}")
    print(f"Output file: {os.path.abspath(output_file)}")
    
    # Show final count of unique tweets
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            final_tweets = json.load(f)
        print(f"Final unique tweets in file: {len(final_tweets)}")
    except Exception as e:
        print(f"Error reading final file: {e}")

if __name__ == "__main__":
    main() 