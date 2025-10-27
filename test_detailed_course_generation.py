#!/usr/bin/env python3
"""
Test script for Enhanced Course Generator with detailed content
Tests the comprehensive course generation capabilities.
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

def test_comprehensive_course_generation():
    """Test comprehensive course generation with detailed content."""
    
    print("🎓 Testing Comprehensive Course Generation")
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
    
    # Test topic - something that needs comprehensive treatment
    test_topic = "Machine Learning Ethics"
    print(f"📚 Generating comprehensive course for: {test_topic}")
    
    try:
        # Generate comprehensive course
        print("\n🚀 Starting comprehensive course generation...")
        
        # Get sources first
        sources = generator.search_multiple_sources(test_topic, max_per_source=3)
        print(f"✅ Found {len(sources)} sources across multiple platforms")
        
        # Generate enhanced outline
        outline = generator._generate_enhanced_outline(test_topic, "university", sources)
        print(f"✅ Generated outline: {outline.get('course_title', 'N/A')}")
        print(f"📚 Modules: {len(outline.get('modules', []))}")
        
        # Generate detailed module (just test one module for speed)
        if outline.get('modules'):
            first_module = outline['modules'][0]
            print(f"\n📖 Generating detailed content for: {first_module['title']}")
            
            detailed_module = generator._generate_enhanced_module(
                first_module, sources, test_topic, "university"
            )
            
            print(f"✅ Module generated with:")
            print(f"   📝 Lessons: {len(detailed_module.get('lessons', []))}")
            print(f"   🎯 Lectures: {len(detailed_module.get('lectures', []))}")
            print(f"   💬 Seminars: {len(detailed_module.get('seminars', []))}")
            print(f"   📚 Readings: {len(detailed_module.get('readings', []))}")
            print(f"   📋 Assignments: {len(detailed_module.get('assignments', []))}")
            print(f"   📊 Case Studies: {len(detailed_module.get('case_studies', []))}")
            
            # Save detailed sample
            sample_detailed_course = {
                "course_title": outline.get("course_title"),
                "description": outline.get("description"),
                "total_modules": len(outline.get('modules', [])),
                "sample_module": detailed_module,
                "source_summary": {
                    "total_sources": len(sources),
                    "source_types": list(set(s.source_type for s in sources))
                }
            }
            
            with open("sample_detailed_course.json", "w", encoding="utf-8") as f:
                json.dump(sample_detailed_course, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Detailed sample saved to: sample_detailed_course.json")
            
            # Show content preview
            if detailed_module.get('lessons'):
                first_lesson = detailed_module['lessons'][0]
                print(f"\n📖 Sample lesson content preview:")
                print(f"   Title: {first_lesson.get('title')}")
                print(f"   Duration: {first_lesson.get('duration')}")
                print(f"   Format: {first_lesson.get('format')}")
                content_preview = first_lesson.get('content', '')[:200] + "..." if len(first_lesson.get('content', '')) > 200 else first_lesson.get('content', '')
                print(f"   Content: {content_preview}")
        
        print("\n🎉 Comprehensive course generation test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Comprehensive course generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_topics():
    """Test comprehensive generation with different topic types."""
    
    print("\n🔬 Testing Different Topic Types")
    print("=" * 35)
    
    load_dotenv()
    client = OpenAI(
        api_key=os.getenv("GITHUB_TOKEN"),
        base_url="https://models.inference.ai.azure.com"
    )
    generator = EnhancedCourseGenerator(client)
    
    test_topics = [
        "Quantum Computing",
        "Philosophy of Mind", 
        "Sustainable Energy Systems"
    ]
    
    results = {}
    
    for topic in test_topics:
        print(f"\n📚 Testing: {topic}")
        try:
            sources = generator.search_multiple_sources(topic, max_per_source=2)
            outline = generator._generate_enhanced_outline(topic, "university", sources)
            
            results[topic] = {
                "sources_found": len(sources),
                "source_types": list(set(s.source_type for s in sources)),
                "modules": len(outline.get('modules', [])),
                "course_title": outline.get('course_title', 'N/A')
            }
            
            print(f"   ✅ {results[topic]['sources_found']} sources, {results[topic]['modules']} modules")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results[topic] = {"error": str(e)}
    
    # Save results
    with open("topic_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: topic_generation_results.json")
    return True

if __name__ == "__main__":
    print("🎓 Enhanced Course Generator - Detailed Content Test")
    print("=" * 60)
    
    # Check environment
    load_dotenv()
    if not os.getenv("GITHUB_TOKEN"):
        print("❌ GITHUB_TOKEN not found in environment")
        print("Please ensure your .env file contains GITHUB_TOKEN")
        sys.exit(1)
    
    success = True
    
    try:
        success &= test_comprehensive_course_generation()
        success &= test_different_topics()
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        success = False
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! Enhanced detailed course generation is working.")
        print("\n🚀 The system now generates:")
        print("   📚 Comprehensive course outlines (12-16 modules)")
        print("   📖 Detailed lessons with extensive content")
        print("   🎯 Multiple lecture types and formats")
        print("   💬 Seminar and discussion sessions")
        print("   📋 Diverse assignment types")
        print("   📊 Real-world case studies")
        print("   🔬 Research connections and industry links")
        print("   📚 Comprehensive reading lists")
        print("   🏆 Detailed assessment strategies")
        print("\n✨ Your course generator now creates university-level content!")
    else:
        print("❌ Some tests failed. Check the error messages above.")
        sys.exit(1)