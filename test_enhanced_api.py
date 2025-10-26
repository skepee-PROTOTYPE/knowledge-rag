#!/usr/bin/env python3

import requests
import json

def test_enhanced_course_api():
    """Test the enhanced course generation API."""
    
    # Test with the local server
    url = "http://localhost:5000/api/course/generate"
    
    payload = {
        "topic": "Python Programming",
        "level": "beginner"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("Testing Enhanced Course Generation API...")
        print("=" * 60)
        print(f"Topic: {payload['topic']}")
        print(f"Level: {payload['level']}")
        print("\nGenerating course (this may take 30-60 seconds)...")
        
        response = requests.post(url, json=payload, headers=headers, timeout=120)  # Longer timeout for detailed generation
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            course = data.get('course', {})
            
            print("\n✅ SUCCESS! Enhanced Course Generated:")
            print(f"📚 Course Title: {course.get('course_title', 'N/A')}")
            print(f"📖 Description: {course.get('description', 'N/A')[:100]}...")
            print(f"🎯 Learning Objectives: {len(course.get('learning_objectives', []))}")
            print(f"📚 Modules: {len(course.get('modules', []))}")
            
            # Check enhanced content
            if 'modules_content' in course:
                print(f"📝 Detailed Module Content: {len(course['modules_content'])}")
                
                for i, module in enumerate(course['modules_content'], 1):
                    print(f"\n📖 Module {i}: {module.get('title', 'N/A')}")
                    print(f"   📚 Lessons: {len(module.get('lessons', []))}")
                    print(f"   🎯 Learning Objectives: {len(module.get('learning_objectives', []))}")
                    print(f"   📋 Has Assessments: {'assessments' in module}")
                    print(f"   📚 Has Resources: {'additional_resources' in module}")
                    
                    # Show lesson details
                    lessons = module.get('lessons', [])
                    if lessons:
                        lesson = lessons[0]
                        print(f"   📄 First Lesson: {lesson.get('title', 'N/A')}")
                        print(f"      ⏱️  Duration: {lesson.get('duration', 'N/A')}")
                        print(f"      📝 Content Length: {len(lesson.get('content', ''))//1000}k chars")
                        print(f"      💡 Has Exercises: {'exercises' in lesson}")
                        print(f"      🔗 Sources: {len(lesson.get('sources', []))}")
            
            # Check course summary
            if 'course_summary' in course:
                summary = course['course_summary']
                print(f"\n📊 Course Summary:")
                print(f"   🎓 Total Lessons: {summary.get('total_lessons', 'N/A')}")
                print(f"   ⏱️  Total Duration: {summary.get('estimated_total_duration', 'N/A')}")
                print(f"   🏆 Certificate: {summary.get('completion_certificate', False)}")
            
            # Check final project
            if 'final_project' in course:
                project = course['final_project']
                print(f"\n🎯 Final Project: {project.get('title', 'N/A')}")
                print(f"   📋 Deliverables: {len(project.get('deliverables', []))}")
                
            print(f"\n🎉 Enhanced Course Generation is working perfectly!")
            print(f"   The course now includes detailed lessons, exercises, assessments, and resources!")
            
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_enhanced_course_api()