#!/usr/bin/env python3

import os
from course_generator import WikipediaCourseSystem

def test_detailed_course():
    """Test the enhanced detailed course generation."""
    
    print("Testing Enhanced Course Generation")
    print("=" * 50)
    
    # Initialize course system
    course_system = WikipediaCourseSystem()
    
    # Test with a focused topic
    topic = "Machine Learning"
    level = "beginner"
    
    print(f"Generating course: {topic} ({level})")
    
    try:
        # Generate full course
        course = course_system.create_course(topic, level)
        
        print("\n✅ Course Generation Successful!")
        print(f"📚 Course Title: {course.get('course_title', 'N/A')}")
        print(f"📊 Level: {course.get('level', 'N/A')}")
        print(f"🎯 Learning Objectives: {len(course.get('learning_objectives', []))}")
        print(f"📖 Modules: {len(course.get('modules', []))}")
        print(f"📝 Module Content Generated: {len(course.get('modules_content', []))}")
        
        # Check course summary
        if 'course_summary' in course:
            summary = course['course_summary']
            print(f"⏱️  Total Duration: {summary.get('estimated_total_duration', 'N/A')}")
            print(f"🎓 Total Lessons: {summary.get('total_lessons', 'N/A')}")
        
        # Check first module content
        if course.get('modules_content'):
            first_module = course['modules_content'][0]
            print(f"\n📖 First Module: {first_module.get('title', 'N/A')}")
            print(f"   📝 Lessons: {len(first_module.get('lessons', []))}")
            print(f"   🎯 Learning Objectives: {len(first_module.get('learning_objectives', []))}")
            print(f"   📋 Has Assessment: {'assessments' in first_module}")
            print(f"   📚 Has Resources: {'additional_resources' in first_module}")
            
            # Check first lesson
            if first_module.get('lessons'):
                first_lesson = first_module['lessons'][0]
                print(f"   📄 First Lesson: {first_lesson.get('title', 'N/A')}")
                print(f"      ⏱️  Duration: {first_lesson.get('duration', 'N/A')}")
                print(f"      🔗 Sources: {len(first_lesson.get('sources', []))}")
                print(f"      💡 Has Exercises: {'exercises' in first_lesson}")
        
        print(f"\n🎉 Enhanced course generation working!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Set environment variable (token should be set externally)
    if not os.environ.get('GITHUB_TOKEN'):
        print("⚠️  GITHUB_TOKEN environment variable not set")
        print("Please set the token before running this test")
        exit(1)
    test_detailed_course()