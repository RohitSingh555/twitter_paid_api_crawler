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

def send_to_api(json_data_path, verified_count):
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
        
        # Prepare JSON data for bulk upload
        bulk_data = {
            "items": []
        }
        
        for item in verified_incidents:
            # Create item structure matching the API requirements
            print(item)
            
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
        
        # Send the request with JSON data
        headers = {
            'Content-Type': 'application/json'
        }
        
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

def create_test_data():
    """
    Create sample test data for testing the send_to_api function.
    """
    # Create sample JSON data based on the actual structure from live_verified_fires_20250729_010631.json
    test_json_data = [
        {
            "tweet_id": "1949880559427342845",
            "title": "NEWS RELEASE\n \nArizona House of Representatives\nRepresentative David Marshall (R-7). \n\nHouse Fire Pr...",
            "content": "NEWS RELEASE\n \nArizona House of Representatives\nRepresentative David Marshall (R-7). \n\nHouse Fire Preparedness Committee to Hold Public Meeting in Payson to Address Wildfire Readiness, Challenges in Arizona Communities. https://t.co/61rPGChCRB",
            "published_date": "Mon Jul 28 17:12:07 +0000 2025",
            "url": "https://x.com/GeorgeNemeh/status/1949880559427342845",
            "source": "GeorgeNemeh",
            "fire_related_score": 8,
            "verification_result": "yes",
            "verified_at": "2025-07-29T01:06:36.584596"
        },
        {
            "tweet_id": "1949871803339554886",
            "title": "🔥House Fire Preparedness Committee to Hold Public Meeting in Payson to Address Wildfire Readiness, C...",
            "content": "🔥House Fire Preparedness Committee to Hold Public Meeting in Payson to Address Wildfire Readiness, Challenges in Arizona Communities\n\nThe Arizona House Fire Preparedness Ad Hoc Committee will hold a public meeting on Tuesday, July 29, 2025, at 10:00 a.m. in Payson at Gila Community College, located at 201 North Mud Springs Road.\n\n\"The recent fires in California have shown how fast these disasters can escalate and how devastating they are when systems fail. We can't afford to wait and hope Arizona doesn't face the same. This committee is focused on identifying the problems now—so our firefighters, utilities, and communities have the tools they need to be ready.\" -@AZHouseGOP Rep. @DaveMarshallAZ, Chairman of the Fire Preparedness Committee.\n\nThe meeting is open to the public and will be livestreamed at📺\nhttps://t.co/Mrnbo4tm7G\n\nMORE INFO👇\nhttps://t.co/TF4J2uKHpy\n\n@BlackmanForAZ @SelinaBliss @AzRepGillette #AZHouseGOP #AZLeg",
            "published_date": "Mon Jul 28 16:37:19 +0000 2025",
            "url": "https://x.com/AZHouseGOP/status/1949871803339554886",
            "source": "AZHouseGOP",
            "fire_related_score": 10,
            "verification_result": "yes",
            "verified_at": "2025-07-29T01:06:45.155547"
        },
        {
            "tweet_id": "1949843538046603655",
            "title": "Two Sun City firefighters were evaluated for injuries in a house fire on Sunday, authorities said. \n...",
            "content": "Two Sun City firefighters were evaluated for injuries in a house fire on Sunday, authorities said. \n\nhttps://t.co/pesYAtWVIV",
            "published_date": "Mon Jul 28 14:45:00 +0000 2025",
            "url": "https://x.com/KTAR923/status/1949843538046603655",
            "source": "KTAR923",
            "fire_related_score": 9,
            "verification_result": "yes",
            "verified_at": "2025-07-29T01:06:47.045133"
        }
    ]
    
    # Save test JSON data
    test_json_path = "test_verified_incidents.json"
    with open(test_json_path, 'w', encoding='utf-8') as f:
        json.dump(test_json_data, f, indent=2, ensure_ascii=False)
    
    print(f"[TEST] Created test JSON file: {test_json_path}")
    return test_json_path

if __name__ == "__main__":
    print("=== Testing utils.py ===")
    
    # Create test data
    print("\n1. Creating test data...")
    test_json_path = create_test_data()
    
    # Test the send_to_api function
    print("\n2. Testing send_to_api function...")
    verified_count = 3  # Number of test incidents
    
    print(f"[TEST] Testing with:")
    print(f"  - JSON file: {test_json_path}")
    print(f"  - Verified count: {verified_count}")
    
    # Show what the items would look like
    print("\n3. Preview of items that would be processed:")
    with open(test_json_path, 'r', encoding='utf-8') as f:
        test_items = json.load(f)
    
    for i, item in enumerate(test_items, 1):
        print(f"\n[TEST] Item {i}:")
        print(f"  Tweet ID: {item.get('tweet_id', 'N/A')}")
        print(f"  Title: {item.get('title', 'N/A')}")
        print(f"  Content: {item.get('content', 'N/A')[:100]}...")
        print(f"  Published Date (raw): {item.get('published_date', 'N/A')}")
        print(f"  Published Date (parsed): {parse_twitter_date(item.get('published_date', ''))}")
        print(f"  URL: {item.get('url', 'N/A')}")
        print(f"  Source: {item.get('source', 'N/A')}")
        print(f"  Fire Score: {item.get('fire_related_score', 'N/A')}")
        print(f"  Verification: {item.get('verification_result', 'N/A')}")
        print(f"  Verified At: {item.get('verified_at', 'N/A')}")
    
    # Uncomment the line below to actually test the API call
    # result = send_to_api(test_json_path, verified_count)
    
    # For safety, we'll just print what would happen without making the actual API call
    print("\n[TEST] API call is commented out for safety.")
    print("[TEST] To test the actual API call, uncomment the line:")
    print("      result = send_to_api(test_json_path, verified_count)")
    
    print("\n=== Test completed ===")
    print(f"[TEST] Test files created:")
    print(f"  - {test_json_path}") 