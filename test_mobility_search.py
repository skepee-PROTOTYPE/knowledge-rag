#!/usr/bin/env python3

import requests
import logging

def test_enhanced_search():
    """Test enhanced Wikipedia search with mobility transport."""
    
    url = "https://en.wikipedia.org/w/api.php"
    headers = {"User-Agent": "KnowledgeRAG/1.0 (educational project)"}
    
    query = "mobility transport"
    results = []
    max_results = 5
    
    print(f"Testing search for: '{query}'")
    print("=" * 50)
    
    # Strategy 1: Exact query
    params = {"action": "opensearch", "search": query, "limit": max_results, "format": "json"}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        exact_results = data[1] if len(data) > 1 else []
        print(f"Strategy 1 (exact): {exact_results}")
        results.extend(exact_results)
        
        # Strategy 2: Individual words
        words = query.split()
        for word in words:
            if len(word) > 3:
                params["search"] = word
                response = requests.get(url, params=params, headers=headers, timeout=10)
                data = response.json()
                word_results = data[1] if len(data) > 1 else []
                print(f"Strategy 2 ('{word}'): {word_results}")
                
                for result in word_results:
                    if result not in results and len(results) < max_results:
                        results.append(result)
        
        # Strategy 3: Semantic variations
        variations = ['transport', 'transportation', 'public transport', 'sustainable transport']
        print(f"Strategy 3 (variations): {variations}")
        
        for variation in variations:
            if len(results) >= max_results:
                break
            params["search"] = variation
            response = requests.get(url, params=params, headers=headers, timeout=10)
            data = response.json()
            var_results = data[1] if len(data) > 1 else []
            print(f"  '{variation}': {var_results}")
            
            for result in var_results:
                if result not in results and len(results) < max_results:
                    results.append(result)
        
        print("\n" + "=" * 50)
        print(f"FINAL RESULTS ({len(results)}): {results}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_enhanced_search()