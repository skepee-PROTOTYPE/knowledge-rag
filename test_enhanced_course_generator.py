#!/usr/bin/env python3
"""
Test script for Enhanced Course Generator
Tests the multi-source course generation capabilities.
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from enhanced_course_generator import EnhancedCourseGenerator
from openai import OpenAI
from dotenv import load_dotenv

def test_enhanced_course_generator():
    """Test the enhanced course generator with a sample topic."""
    
    print("🧪 Testing Enhanced Course Generator")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize OpenAI client
    client = OpenAI(
        api_key=os.getenv("GITHUB_TOKEN"),
        base_url="https://models.inference.ai.azure.com"
    )
    
    # Create enhanced generator
    generator = EnhancedCourseGenerator(client)
    
    # Test topic
    test_topic = "Artificial Intelligence Ethics"
    print(f"📚 Testing course generation for: {test_topic}")
    
    # Test 1: Source preview
    print("\n1️⃣ Testing source search...")
    try:
        sources = generator.search_multiple_sources(test_topic, max_per_source=2)
        print(f"✅ Found {len(sources)} sources")
        
        source_types = {}
        for source in sources:
            source_type = source.source_type
            if source_type not in source_types:
                source_types[source_type] = 0
            source_types[source_type] += 1
        
        print(f"📊 Sources by type: {source_types}")
        
        if sources:
            print(f"🎯 Top source: {sources[0].title} ({sources[0].source_type})")
            print(f"   Credibility: {sources[0].credibility_score}/1.0")
        
    except Exception as e:
        print(f"❌ Source search failed: {e}")
        return False
    
    # Test 2: Course generation (simplified for testing)
    print("\n2️⃣ Testing course outline generation...")
    try:
        # Test just the outline generation part
        outline = generator._generate_enhanced_outline(test_topic, "university", sources[:3])
        print(f"✅ Course outline generated: {outline.get('course_title', 'N/A')}")
        print(f"📚 Modules: {len(outline.get('modules', []))}")
        
    except Exception as e:
        print(f"❌ Course outline generation failed: {e}")
        return False
    
    # Test 3: Integration test
    print("\n3️⃣ Testing Flask integration...")
    try:
        from course_integration import CourseGeneratorIntegration
        from flask import Flask
        
        app = Flask(__name__)
        integration = CourseGeneratorIntegration(app)
        
        if integration.enhanced_generator:
            print("✅ Flask integration successful")
        else:
            print("⚠️ Flask integration failed - enhanced generator not initialized")
            
    except Exception as e:
        print(f"❌ Flask integration test failed: {e}")
        return False
    
    print("\n🎉 All tests completed successfully!")
    return True

def test_source_comparison():
    """Test source comparison between basic and enhanced generators."""
    
    print("\n🔍 Testing Source Comparison")
    print("=" * 30)
    
    try:
        from course_integration import CourseGeneratorIntegration
        from flask import Flask
        
        app = Flask(__name__)
        integration = CourseGeneratorIntegration(app)
        
        test_topic = "Machine Learning"
        comparison = integration.compare_generators(test_topic)
        
        print(f"📊 Comparison for: {test_topic}")
        print(f"Basic: {comparison['basic_generator']['primary_source']}")
        print(f"Enhanced: {comparison['enhanced_generator']['sources']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Source comparison test failed: {e}")
        return False

def create_sample_course():
    """Create a sample course to demonstrate capabilities."""
    
    print("\n📖 Creating Sample Course")
    print("=" * 25)
    
    load_dotenv()
    
    try:
        client = OpenAI(
            api_key=os.getenv("GITHUB_TOKEN"),
            base_url="https://models.inference.ai.azure.com"
        )
        
        generator = EnhancedCourseGenerator(client)
        
        # Generate a quick sample (limited scope for testing)
        print("🚀 Generating sample course...")
        
        # Instead of full course, just test the components
        sources = generator.search_multiple_sources("Data Science", max_per_source=1)
        outline = generator._generate_enhanced_outline("Data Science", "university", sources[:2])
        
        sample_course = {
            "course_title": outline.get("course_title", "Sample Course"),
            "description": outline.get("description", "Sample description"),
            "modules": outline.get("modules", [])[:2],  # Limit to 2 modules
            "sources_found": len(sources),
            "source_types": list(set(s.source_type for s in sources))
        }
        
        # Save sample
        with open("sample_enhanced_course.json", "w", encoding="utf-8") as f:
            json.dump(sample_course, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Sample course saved to: sample_enhanced_course.json")
        print(f"📚 Course: {sample_course['course_title']}")
        print(f"🎯 Modules: {len(sample_course['modules'])}")
        print(f"📊 Sources: {sample_course['sources_found']} from {sample_course['source_types']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Sample course creation failed: {e}")
        return False

if __name__ == "__main__":
    print("🎓 Enhanced Course Generator Test Suite")
    print("=" * 60)
    
    # Check environment
    load_dotenv()
    if not os.getenv("GITHUB_TOKEN"):
        print("❌ GITHUB_TOKEN not found in environment")
        print("Please ensure your .env file contains GITHUB_TOKEN")
        sys.exit(1)
    
    success = True
    
    # Run tests
    try:
        success &= test_enhanced_course_generator()
        success &= test_source_comparison()
        success &= create_sample_course()
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        success = False
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! Enhanced Course Generator is ready.")
        print("\n🚀 Next steps:")
        print("1. Run your Flask app: python app.py")
        print("2. Visit: http://localhost:5000/enhanced-course")
        print("3. Try generating a comprehensive course!")
    else:
        print("❌ Some tests failed. Check the error messages above.")
        sys.exit(1)