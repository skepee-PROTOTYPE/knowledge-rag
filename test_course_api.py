#!/usr/bin/env python3
"""
Test script for course generation API endpoints
"""
import requests
import json

def test_course_outline():
    """Test the course outline endpoint."""
    url = "http://localhost:5000/api/course/outline"
    data = {
        "topic": "Python Programming",
        "level": "beginner"
    }
    
    try:
        print("Testing course outline generation...")
        response = requests.post(url, json=data, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Success! Course outline generated:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

def test_quiz_generation():
    """Test the quiz generation endpoint."""
    url = "http://localhost:5000/api/quiz/generate"
    data = {
        "topic": "Solar System",
        "num_questions": 3
    }
    
    try:
        print("\nTesting quiz generation...")
        response = requests.post(url, json=data, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Success! Quiz generated:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

def test_course_generation():
    """Test the full course generation endpoint."""
    url = "http://localhost:5000/api/course/generate"
    data = {
        "topic": "Machine Learning Basics",
        "level": "beginner"
    }
    
    try:
        print("\nTesting full course generation...")
        response = requests.post(url, json=data, timeout=60)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Success! Full course generated:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_course_outline()
    test_quiz_generation()
    test_course_generation()