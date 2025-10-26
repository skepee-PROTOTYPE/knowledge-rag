#!/usr/bin/env python3

import requests
import json

def test_mobility_transport_search():
    """Test the enhanced search with the live API."""
    
    # Test with the local server
    url = "http://localhost:5000/api/ask"
    
    payload = {
        "question": "What is mobility transport?"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("Testing 'mobility transport' search with live API...")
        print("=" * 60)
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ SUCCESS! API Response:")
            print(f"Answer: {data.get('answer', 'No answer')}")
            
            if 'sources' in data:
                print(f"\nSources found: {len(data['sources'])}")
                for i, source in enumerate(data['sources'], 1):
                    print(f"  {i}. {source.get('title', 'Unknown')} - {source.get('url', 'No URL')}")
            else:
                print("\n⚠️  No sources found")
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_mobility_transport_search()