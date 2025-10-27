"""
Interactive Local Testing - Real API Integration
Run this to test the course generator interactively
"""

import os
from openai import OpenAI
from enhanced_course_generator import EnhancedCourseGenerator
from educational_apis import EducationalAPIs
from dotenv import load_dotenv
import json

load_dotenv()

def print_separator():
    print("=" * 70)

def test_educational_apis():
    """Test the educational APIs module"""
    print_separator()
    print("🧪 TEST 1: Educational APIs Module")
    print_separator()
    
    api_client = EducationalAPIs()
    
    test_topics = [
        "machine learning",
        "quantum computing",
        "data science"
    ]
    
    print("\n🔍 Testing API sources with sample topics...\n")
    
    for topic in test_topics:
        print(f"\n📚 Topic: {topic}")
        print("-" * 70)
        
        # Test each source
        sources = {
            'MIT OCW': api_client.search_mit_ocw(topic, 2),
            'arXiv': api_client.search_arxiv(topic, 2),
            'Khan Academy': api_client.search_khan_academy(topic, 2),
            'Coursera': api_client.search_coursera(topic, 2),
        }
        
        for source_name, results in sources.items():
            if results:
                print(f"\n  ✅ {source_name}: {len(results)} results")
                for r in results[:1]:  # Show first result
                    print(f"     • {r['title'][:50]}...")
                    print(f"       {r['url'][:60]}...")
            else:
                print(f"\n  ⚠️  {source_name}: No results")
    
    print_separator()
    print("✅ Educational APIs Test Complete\n")

def test_course_generator():
    """Test the enhanced course generator"""
    print_separator()
    print("🧪 TEST 2: Enhanced Course Generator")
    print_separator()
    
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("❌ Error: GITHUB_TOKEN not found")
        return
    
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=github_token,
    )
    
    print("\n✅ OpenAI client initialized")
    
    # Test with Quick Mode
    generator = EnhancedCourseGenerator(client, quick_mode=True)
    print("✅ Course generator created (Quick Mode)\n")
    
    # Test source search
    topic = "artificial intelligence"
    print(f"🔍 Searching sources for: '{topic}'")
    
    sources = generator.search_multiple_sources(topic, max_per_source=2)
    
    print(f"\n✅ Found {len(sources)} sources:\n")
    
    for i, source in enumerate(sources, 1):
        print(f"{i}. {source.title}")
        print(f"   Type: {source.source_type}")
        print(f"   Credibility: {source.credibility_score}")
        print(f"   URL: {source.url}")
        print()
    
    # Calculate stats
    avg_cred = sum(s.credibility_score for s in sources) / len(sources)
    print(f"📊 Statistics:")
    print(f"   Total sources: {len(sources)}")
    print(f"   Average credibility: {avg_cred:.2f}/1.0")
    print(f"   Source types: {set(s.source_type for s in sources)}")
    
    print_separator()
    print("✅ Course Generator Test Complete\n")

def test_api_status():
    """Test all API endpoints"""
    print_separator()
    print("🧪 TEST 3: API Status Check")
    print_separator()
    
    api_client = EducationalAPIs()
    status = api_client.test_apis()
    
    print("\n🔍 Testing all API endpoints:\n")
    
    for api_name, is_working in status.items():
        status_icon = "✅" if is_working else "❌"
        print(f"  {status_icon} {api_name.replace('_', ' ').title()}: {'Working' if is_working else 'Failed'}")
    
    all_working = all(status.values())
    
    print()
    if all_working:
        print("🎉 All APIs are working correctly!")
    else:
        print("⚠️  Some APIs failed - check configuration")
    
    print_separator()
    print("✅ API Status Test Complete\n")

def main_menu():
    """Interactive menu"""
    print("\n" + "=" * 70)
    print("🎓 KNOWLEDGE RAG - Real API Integration Test Suite")
    print("=" * 70)
    print("\nChoose a test to run:\n")
    print("  1. Test Educational APIs Module")
    print("  2. Test Enhanced Course Generator")
    print("  3. Test All API Status")
    print("  4. Run All Tests")
    print("  5. Exit")
    print()
    
    choice = input("Enter your choice (1-5): ").strip()
    
    if choice == "1":
        test_educational_apis()
    elif choice == "2":
        test_course_generator()
    elif choice == "3":
        test_api_status()
    elif choice == "4":
        print("\n🚀 Running all tests...\n")
        test_api_status()
        test_educational_apis()
        test_course_generator()
        print("\n🎉 All tests complete!")
    elif choice == "5":
        print("\n👋 Goodbye!\n")
        return False
    else:
        print("\n⚠️  Invalid choice. Please try again.\n")
    
    return True

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎓 Welcome to Knowledge RAG Interactive Test Suite!")
    print("=" * 70)
    print("\nThis will test the real API integrations locally.")
    print("Press Ctrl+C to exit at any time.\n")
    
    try:
        # Run quick status check first
        print("🔍 Quick Status Check...")
        api_client = EducationalAPIs()
        status = api_client.test_apis()
        working_count = sum(1 for v in status.values() if v)
        print(f"✅ {working_count}/{len(status)} APIs working\n")
        
        # Show menu
        while main_menu():
            pass
            
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted. Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
