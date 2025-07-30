import requests
import json
import os
from datetime import datetime
import re

def parse_twitter_date(date_string):
    """
    Parse Twitter date format 'Mon Jul 28 17:12:07 +0000 2025' to ISO format.
    
    Args:
        date_string (str): Twitter date string
        
    Returns:
        str: ISO formatted date string or None if parsing fails
    """
    try:
        # Parse the Twitter date format
        # Example: "Mon Jul 28 17:12:07 +0000 2025"
        parsed_date = datetime.strptime(date_string, "%a %b %d %H:%M:%S %z %Y")
        # Convert to ISO format for database
        return parsed_date.isoformat()
    except (ValueError, AttributeError) as e:
        print(f"[API] Warning: Could not parse date '{date_string}': {e}")
        return None

def send_bulk_upload(json_data_path, verified_count):
    """
    Send fire incident data to the bulk-upload API endpoint.
    
    Args:
        json_data_path (str): Path to the JSON file with verified incidents
        verified_count (int): Number of verified fire incidents
    """
    try:
        url = 'http://195.250.31.177:9500/api/fire-news/bulk-upload'
        
        # Load the verified incidents from JSON file
        if not os.path.exists(json_data_path):
            print(f"[API] JSON file not found: {json_data_path}")
            return False
            
        with open(json_data_path, 'r', encoding='utf-8') as f:
            verified_incidents = json.load(f)
        
        print(f"[API] Loaded {len(verified_incidents)} incidents from {json_data_path}")
        
        # Prepare JSON data for bulk upload
        bulk_data = {
            "items": []
        }
        
        processed_count = 0
        for item in verified_incidents:
            # Create item structure matching the API requirements
            print(f"[API] Processing item {processed_count + 1}: {item.get('title', 'No title')[:50]}...")
            
            # Parse the published_date from Twitter format to ISO format
            raw_published_date = item.get("published_date", "")
            parsed_published_date = parse_twitter_date(raw_published_date) if raw_published_date else None
            
            # Parse the verified_at date (should already be in ISO format)
            raw_verified_at = item.get("verified_at", "")
            parsed_verified_at = raw_verified_at if raw_verified_at else datetime.now().isoformat()
            
            json_item = {
                "title": item.get("title", ""),
                "content": item.get("content", ""),
                "published_date": parsed_published_date,
                "url": item.get("url", ""),
                "source": item.get("source", ""),
                "fire_related_score": float(item.get("fire_related_score", 0.8)),
                "verification_result": item.get("verification_result", "yes"),
                "verified_at": parsed_verified_at,
                "state": "",  # Could be extracted from content if needed
                "county": "",  # Could be extracted from content if needed
                "city": "",  # Could be extracted from content if needed
                "province": "",  # Could be extracted from content if needed
                "country": "USA",  # Default country
                "latitude": None,  # Could be extracted from content if needed
                "longitude": None,  # Could be extracted from content if needed
                "image_url": "",  # Could be extracted from content if needed
                "tags": "fire,emergency,news,twitter",  # Default tags
                "reporter_name": "Twitter Fire Detection Bot"  # Could be extracted from content if needed
            }
            bulk_data["items"].append(json_item)
            processed_count += 1
        
        print(f"[API] Prepared {len(bulk_data['items'])} items for bulk upload")
        
        # Send the request with JSON data
        headers = {
            'Content-Type': 'application/json'
        }
        
        print(f"[API] Sending bulk upload request to {url}")
        response = requests.post(url, json=bulk_data, headers=headers)
        print(f"[API] POST request sent. Status code: {response.status_code}")
        print(f"[API] Response: {response.text}")
        print(f"[API] Sent {len(bulk_data['items'])} items in bulk upload")
        
        if response.status_code == 200:
            result = response.json()
            print(f"[API] Successfully sent data to bulk-upload endpoint")
            print(f"[API] Inserted: {result.get('inserted', 0)}")
            print(f"[API] Skipped: {result.get('skipped', 0)}")
            print(f"[API] Total processed: {result.get('total_processed', 0)}")
            return True
        else:
            print(f"[API] Failed to send data. Status code: {response.status_code}")
            return False
                
    except Exception as e:
        print(f"[API] Failed to send POST request: {e}")
        return False

def preview_data(json_data_path, max_items=5):
    """
    Preview the data that will be sent to the API.
    
    Args:
        json_data_path (str): Path to the JSON file
        max_items (int): Maximum number of items to preview
    """
    try:
        with open(json_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n=== DATA PREVIEW ===")
        print(f"Total items in file: {len(data)}")
        print(f"Previewing first {min(max_items, len(data))} items:")
        
        for i, item in enumerate(data[:max_items], 1):
            print(f"\n--- Item {i} ---")
            print(f"Tweet ID: {item.get('tweet_id', 'N/A')}")
            print(f"Title: {item.get('title', 'N/A')[:100]}...")
            print(f"Content: {item.get('content', 'N/A')[:100]}...")
            print(f"Published Date (raw): {item.get('published_date', 'N/A')}")
            print(f"Published Date (parsed): {parse_twitter_date(item.get('published_date', ''))}")
            print(f"URL: {item.get('url', 'N/A')}")
            print(f"Source: {item.get('source', 'N/A')}")
            print(f"Fire Score: {item.get('fire_related_score', 'N/A')}")
            print(f"Verification: {item.get('verification_result', 'N/A')}")
            print(f"Verified At: {item.get('verified_at', 'N/A')}")
            
    except Exception as e:
        print(f"[PREVIEW] Error previewing data: {e}")

def test_with_sample_data():
    """
    Test with a small sample of the actual data.
    """
    json_file = "output/live_verified_fires_20250729_010631.json"
    
    if not os.path.exists(json_file):
        print(f"[TEST] File not found: {json_file}")
        print("[TEST] Please make sure the JSON file exists in the output directory.")
        return
    
    print("=== TESTING BULK UPLOAD WITH REAL DATA ===")
    
    # Preview the data first
    preview_data(json_file, max_items=3)
    
    # Ask user if they want to proceed
    print(f"\n[TEST] Ready to send data to API.")
    print(f"[TEST] File: {json_file}")
    
    # For safety, we'll just show what would happen
    print("\n[TEST] API call is commented out for safety.")
    print("[TEST] To test the actual API call, uncomment the line:")
    print("      result = send_bulk_upload(json_file, len(data))")
    
    # Uncomment the following lines to actually test:
    # with open(json_file, 'r', encoding='utf-8') as f:
    #     data = json.load(f)
    # result = send_bulk_upload(json_file, len(data))
    
    print("\n=== TEST COMPLETED ===")

if __name__ == "__main__":
    test_with_sample_data() 