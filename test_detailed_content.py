#!/usr/bin/env python3
"""
Quick test to demonstrate enhanced detailed course content.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent))

from enhanced_course_generator import EnhancedCourseGenerator
from openai import OpenAI

load_dotenv()

print("🎓 Testing Enhanced Detailed Course Generation")
print("=" * 60)

# Initialize
client = OpenAI(
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url="https://models.inference.ai.azure.com"
)

generator = EnhancedCourseGenerator(client)

# Test topic
topic = "Machine Learning"
print(f"\n📚 Generating detailed course for: {topic}")

# Get sources
print("\n1️⃣ Searching sources...")
sources = generator.search_multiple_sources(topic, max_per_source=2)
print(f"   ✅ Found {len(sources)} sources")

# Generate comprehensive course with detailed content
print("\n2️⃣ Generating comprehensive course with detailed content...")
print("   (This will take 1-2 minutes...)")

course = generator.generate_comprehensive_course(topic, "university")

# Display results
print(f"\n✅ Course Generated: {course.get('course_title', 'N/A')}")
print(f"📊 Modules: {len(course.get('modules', []))}")
print(f"📚 Sources: {course.get('source_summary', {}).get('total_sources', 0)}")

# Show first module details
if course.get('modules'):
    module = course['modules'][0]
    print(f"\n📖 First Module: {module.get('title', 'N/A')}")
    print(f"   Lessons: {len(module.get('lessons', []))}")
    print(f"   Readings: {len(module.get('readings', []))}")
    print(f"   Assignments: {len(module.get('assignments', []))}")
    
    # Show first lesson preview
    if module.get('lessons'):
        lesson = module['lessons'][0]
        content_preview = lesson.get('content', '')[:300]
        print(f"\n📝 First Lesson Preview:")
        print(f"   Title: {lesson.get('title', 'N/A')}")
        print(f"   Content: {content_preview}...")

# Save detailed course
output_file = "detailed_machine_learning_course.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(course, f, indent=2, ensure_ascii=False)

print(f"\n💾 Full course saved to: {output_file}")
print("\n🎉 Done! Check the JSON file for complete detailed content.")
