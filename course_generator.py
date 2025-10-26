"""
Course Generation Module
Automatically creates structured courses from Wikipedia content.
"""

import json
from typing import List, Dict, Any
from openai import OpenAI
import os
from pathlib import Path


class CourseGenerator:
    """Generate structured courses from Wikipedia content."""
    
    def __init__(self, client: OpenAI, wiki_rag_system):
        self.client = client
        self.wiki_rag = wiki_rag_system
    
    def generate_course_outline(self, topic: str, level: str = "beginner") -> Dict[str, Any]:
        """Generate a comprehensive course outline for a given topic."""
        
        prompt = f"""Create a comprehensive {level}-level course outline for "{topic}".
        
        Structure the course with:
        1. Course title and description
        2. Learning objectives (3-5 key goals)
        3. Prerequisites (if any)
        4. Course modules (5-8 modules)
        5. For each module:
           - Module title
           - Learning objectives
           - Key topics to cover
           - Estimated duration
           - Assessment type
        
        Format as JSON with this structure:
        {{
            "course_title": "...",
            "description": "...",
            "level": "{level}",
            "total_duration": "...",
            "learning_objectives": [...],
            "prerequisites": [...],
            "modules": [
                {{
                    "module_number": 1,
                    "title": "...",
                    "duration": "...",
                    "objectives": [...],
                    "topics": [...],
                    "assessment": "..."
                }}
            ]
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert course designer. Create well-structured, engaging courses."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return self._parse_outline_text(response.choices[0].message.content, topic, level)
    
    def generate_module_content(self, module_title: str, topics: List[str], level: str = "beginner") -> Dict[str, Any]:
        """Generate comprehensive detailed content for a specific module."""
        
        print(f"   📖 Generating content for: {module_title}")
        
        # Use the existing RAG system to gather relevant content
        module_content = {
            "title": module_title,
            "overview": "",
            "learning_objectives": [],
            "lessons": [],
            "assessments": [],
            "additional_resources": []
        }
        
        # Generate module overview and objectives
        overview_chunks = self.wiki_rag.search_and_retrieve(module_title, top_k=5)
        
        overview_prompt = f"""Create a comprehensive module overview for "{module_title}" at {level} level.
        
        Use this Wikipedia content as reference:
        {self._format_chunks(overview_chunks)}
        
        Provide:
        1. Module Overview (3-4 sentences explaining what students will learn)
        2. Learning Objectives (5-7 specific, measurable objectives)
        3. Prerequisites (if any)
        4. Estimated Duration
        
        Format as JSON:
        {{
            "overview": "...",
            "learning_objectives": ["objective1", "objective2", ...],
            "prerequisites": ["prerequisite1", ...],
            "duration": "X hours"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert curriculum designer creating detailed educational content."},
                    {"role": "user", "content": overview_prompt}
                ],
                temperature=0.6
            )
            
            overview_data = json.loads(response.choices[0].message.content)
            module_content.update(overview_data)
        except:
            module_content["overview"] = f"This module covers {module_title} concepts and applications."
            module_content["learning_objectives"] = [f"Understand {topic}" for topic in topics]
        
        # Generate detailed lessons for each topic
        for i, topic in enumerate(topics, 1):
            print(f"      📝 Lesson {i}: {topic}")
            
            # Get relevant content from Wikipedia via RAG
            retrieved_chunks = self.wiki_rag.search_and_retrieve(topic, top_k=5)
            
            # Generate comprehensive lesson content
            lesson_prompt = f"""Create a comprehensive lesson plan for "{topic}" as Lesson {i} in the module "{module_title}".
            This is for {level} level learners.
            
            Use this Wikipedia content as reference:
            {self._format_chunks(retrieved_chunks)}
            
            Create a detailed lesson with:
            
            1. **Lesson Introduction** (2-3 sentences)
            2. **Key Learning Points** (5-7 main concepts students should understand)
            3. **Detailed Content Sections** (3-4 sections with in-depth explanations, examples, and applications)
            4. **Real-World Applications** (3-4 specific examples showing practical use)
            5. **Interactive Activities** (2-3 hands-on activities or discussions)
            6. **Knowledge Check Questions** (5 questions to test understanding)
            7. **Further Reading** (3-4 recommended resources or Wikipedia links)
            
            Make the content:
            - Educational and engaging
            - Appropriate for {level} level
            - Rich with examples and applications
            - Interactive and practical
            
            Use markdown formatting for structure and readability.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert educator creating comprehensive lesson content. Use clear structure and engaging educational techniques."},
                    {"role": "user", "content": lesson_prompt}
                ],
                temperature=0.6,
                max_tokens=3000
            )
            
            # Generate practice exercises for this lesson
            exercises_prompt = f"""Create 3 practical exercises for the lesson on "{topic}" in {module_title}.
            
            For {level} level learners, create:
            1. A hands-on activity or simulation
            2. A problem-solving exercise with step-by-step solution
            3. A creative project or real-world application task
            
            Each exercise should include:
            - Clear instructions
            - Expected outcomes
            - Time estimate
            - Difficulty level
            
            Format as structured text with clear sections.
            """
            
            exercises_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an educational designer creating practical learning exercises."},
                    {"role": "user", "content": exercises_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            lesson_data = {
                "lesson_number": i,
                "title": topic,
                "duration": "45-60 minutes",
                "content": response.choices[0].message.content,
                "exercises": exercises_response.choices[0].message.content,
                "sources": [
                    {
                        "title": chunk.get("title", "Wikipedia Article"),
                        "url": chunk.get("url", ""),
                        "type": "reference"
                    } for chunk in retrieved_chunks
                ]
            }
            
            module_content["lessons"].append(lesson_data)
        
        # Generate module assessment
        assessment_prompt = f"""Create a comprehensive assessment for the module "{module_title}" covering topics: {', '.join(topics)}.
        
        For {level} level learners, create:
        1. **Quiz Questions** (10 multiple choice questions)
        2. **Short Answer Questions** (5 questions requiring 2-3 sentence responses)
        3. **Project Assignment** (A practical project that applies the module concepts)
        4. **Rubric** (Scoring criteria for the project)
        
        Make assessments challenging but appropriate for the level.
        
        Format as structured JSON:
        {{
            "quiz": [
                {{
                    "question": "...",
                    "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
                    "correct_answer": "A",
                    "explanation": "..."
                }}
            ],
            "short_answer": [
                {{
                    "question": "...",
                    "sample_answer": "...",
                    "points": 5
                }}
            ],
            "project": {{
                "title": "...",
                "description": "...",
                "deliverables": ["...", "..."],
                "timeline": "...",
                "rubric": {{
                    "criteria1": "description",
                    "criteria2": "description"
                }}
            }}
        }}
        """
        
        try:
            assessment_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert assessment designer creating fair and comprehensive evaluations."},
                    {"role": "user", "content": assessment_prompt}
                ],
                temperature=0.5,
                max_tokens=2000
            )
            
            assessment_data = json.loads(assessment_response.choices[0].message.content)
            module_content["assessments"] = assessment_data
            
        except Exception as e:
            print(f"      ⚠️  Assessment generation failed: {e}")
            module_content["assessments"] = {
                "quiz": [],
                "short_answer": [],
                "project": {"title": f"Module Project: {module_title}", "description": "Apply the concepts learned in this module."}
            }
        
        # Generate additional resources
        resources_prompt = f"""Suggest additional learning resources for the module "{module_title}" covering {', '.join(topics)}.
        
        Provide:
        1. **Recommended Wikipedia Articles** (5 relevant articles with brief descriptions)
        2. **Interactive Simulations** (3 suggested interactive tools or simulations)
        3. **Video Resources** (3 educational video topics that would complement the learning)
        4. **Books/Papers** (3 academic or educational texts)
        5. **Online Tools** (3 online tools, calculators, or platforms students could use)
        
        Format as structured text with clear categories.
        """
        
        try:
            resources_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an educational resource curator recommending high-quality learning materials."},
                    {"role": "user", "content": resources_prompt}
                ],
                temperature=0.6,
                max_tokens=1200
            )
            
            module_content["additional_resources"] = resources_response.choices[0].message.content
            
        except Exception as e:
            print(f"      ⚠️  Resources generation failed: {e}")
            module_content["additional_resources"] = f"Explore related topics on Wikipedia and educational platforms."
        
        return module_content
    
    def create_full_course(self, topic: str, level: str = "beginner") -> Dict[str, Any]:
        """Create a comprehensive course with detailed outline and rich content."""
        
        print(f"🎓 Generating comprehensive course: {topic} ({level} level)")
        
        # Step 1: Generate enhanced course outline
        print("📋 Creating detailed course outline...")
        outline = self.generate_course_outline(topic, level)
        
        # Step 2: Generate comprehensive content for each module
        print("📚 Generating detailed module content...")
        full_course = outline.copy()
        full_course["modules_content"] = []
        full_course["course_summary"] = {}
        
        total_lessons = 0
        total_duration = 0
        
        for i, module in enumerate(outline.get("modules", []), 1):
            print(f"   📖 Module {i}: {module['title']}")
            
            module_content = self.generate_module_content(
                module["title"], 
                module.get("topics", []),
                level
            )
            
            full_course["modules_content"].append(module_content)
            
            # Track course statistics
            total_lessons += len(module_content.get("lessons", []))
            try:
                duration_str = module_content.get("duration", "2 hours")
                hours = int(''.join(filter(str.isdigit, duration_str.split()[0])) or "2")
                total_duration += hours
            except:
                total_duration += 2
        
        # Add course summary with statistics
        full_course["course_summary"] = {
            "total_modules": len(outline.get("modules", [])),
            "total_lessons": total_lessons,
            "estimated_total_duration": f"{total_duration} hours",
            "level": level,
            "completion_certificate": True,
            "course_type": "Comprehensive Wikipedia-based Course"
        }
        
        # Generate course completion project
        print("🎯 Creating final course project...")
        final_project_prompt = f"""Create a comprehensive final project for the course "{outline.get('course_title', topic)}" at {level} level.
        
        This project should:
        1. Integrate concepts from all modules
        2. Be practical and applicable to real-world scenarios
        3. Be challenging but achievable for {level} learners
        4. Include clear deliverables and timeline
        
        Course modules covered:
        {[module['title'] for module in outline.get('modules', [])]}
        
        Format as JSON:
        {{
            "title": "...",
            "description": "...",
            "objectives": ["...", "..."],
            "deliverables": ["...", "..."],
            "timeline": "...",
            "assessment_criteria": {{
                "technical_accuracy": "...",
                "creativity": "...",
                "practical_application": "..."
            }},
            "bonus_challenges": ["...", "..."]
        }}
        """
        
        try:
            project_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert educational designer creating capstone projects that integrate learning."},
                    {"role": "user", "content": final_project_prompt}
                ],
                temperature=0.6,
                max_tokens=1500
            )
            
            final_project = json.loads(project_response.choices[0].message.content)
            full_course["final_project"] = final_project
            
        except Exception as e:
            print(f"   ⚠️  Final project generation failed: {e}")
            full_course["final_project"] = {
                "title": f"Capstone Project: {topic}",
                "description": f"Apply all concepts learned in this {topic} course to create a comprehensive project."
            }
        
        print(f"✅ Course generation complete!")
        print(f"   📊 {total_lessons} lessons across {len(outline.get('modules', []))} modules")
        print(f"   ⏱️  Estimated duration: {total_duration} hours")
        
        return full_course
    
    def save_course(self, course_data: Dict[str, Any], filename: str = None) -> str:
        """Save course to JSON file."""
        
        if not filename:
            safe_title = "".join(c for c in course_data.get("course_title", "course") 
                               if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"course_{safe_title.replace(' ', '_').lower()}.json"
        
        course_dir = Path("courses")
        course_dir.mkdir(exist_ok=True)
        
        filepath = course_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(course_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Course saved to: {filepath}")
        return str(filepath)
    
    def generate_quiz(self, topic: str, num_questions: int = 10) -> List[Dict[str, Any]]:
        """Generate quiz questions for a topic."""
        
        # Get relevant content
        retrieved_chunks = self.wiki_rag.search_and_retrieve(topic, top_k=5)
        
        quiz_prompt = f"""Create {num_questions} multiple-choice quiz questions about "{topic}".
        
        Based on this content:
        {self._format_chunks(retrieved_chunks)}
        
        For each question, provide:
        1. Question text
        2. 4 answer options (A, B, C, D)
        3. Correct answer
        4. Brief explanation
        
        Format as JSON array:
        [
            {{
                "question": "...",
                "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
                "correct_answer": "A",
                "explanation": "..."
            }}
        ]
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert quiz creator. Create challenging but fair questions."},
                {"role": "user", "content": quiz_prompt}
            ],
            temperature=0.5
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return self._parse_quiz_text(response.choices[0].message.content)
    
    def _format_chunks(self, chunks: List[Dict]) -> str:
        """Format retrieved chunks for prompts."""
        formatted = []
        for i, chunk in enumerate(chunks, 1):
            formatted.append(f"[{i}] {chunk.get('text', '')}")
        return "\n\n".join(formatted)
    
    def _parse_outline_text(self, text: str, topic: str, level: str) -> Dict[str, Any]:
        """Fallback parser for course outline if JSON fails."""
        return {
            "course_title": f"{topic} Course",
            "description": f"A comprehensive {level} course on {topic}",
            "level": level,
            "learning_objectives": ["Learn fundamental concepts", "Apply knowledge practically"],
            "modules": [
                {
                    "module_number": 1,
                    "title": f"Introduction to {topic}",
                    "topics": [topic],
                    "duration": "2 hours"
                }
            ]
        }
    
    def _parse_quiz_text(self, text: str) -> List[Dict[str, Any]]:
        """Fallback parser for quiz if JSON fails."""
        return [
            {
                "question": "Sample question about the topic",
                "options": {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
                "correct_answer": "A",
                "explanation": "This is the correct answer because..."
            }
        ]


# Integration class to connect with existing app
class WikipediaCourseSystem:
    """Main interface for course generation using Wikipedia RAG."""
    
    def __init__(self, openai_client=None, chroma_client=None):
        """Initialize with OpenAI and ChromaDB clients."""
        import os
        from openai import OpenAI
        
        if openai_client is None:
            self.client = OpenAI(
                base_url="https://models.inference.ai.azure.com",
                api_key=os.environ.get("GITHUB_TOKEN", "").strip()
            )
        else:
            self.client = openai_client
            
        self.chroma_client = chroma_client
        self.course_generator = CourseGenerator(self.client, self)
    
    def search_and_retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Use Wikipedia API to search and retrieve content."""
        try:
            import wikipediaapi
            
            # Initialize Wikipedia API
            wiki = wikipediaapi.Wikipedia(
                language='en',
                extract_format=wikipediaapi.ExtractFormat.WIKI,
                user_agent='KnowledgeRAG/1.0 (https://github.com/skepee-PROTOTYPE/knowledge-rag)'
            )
            
            # Search for articles
            search_results = self._search_wikipedia(query, max_results=3)
            chunks = []
            
            for title in search_results:
                try:
                    # Get Wikipedia page
                    page = wiki.page(title)
                    if page.exists():
                        # Split content into chunks
                        content = page.text[:2000]  # Limit content length
                        chunks.append({
                            'text': content,
                            'title': title,
                            'url': page.fullurl
                        })
                except Exception as e:
                    print(f"Error retrieving page {title}: {e}")
                    continue
            
            return chunks[:top_k]
            
        except Exception as e:
            print(f"Error in search_and_retrieve: {e}")
            return []
    
    def _search_wikipedia(self, query: str, max_results: int = 5) -> List[str]:
        """Enhanced Wikipedia search using opensearch API (same as main app)."""
        try:
            import requests
            
            # Use the same API as the main app (opensearch)
            url = "https://en.wikipedia.org/w/api.php"
            headers = {
                "User-Agent": "KnowledgeRAG/1.0 (educational project)"
            }
            
            # Strategy 1: Try exact query
            params = {
                "action": "opensearch",
                "search": query,
                "limit": max_results,
                "format": "json"
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            results = data[1] if len(data) > 1 else []
            
            # If we got good results, return them
            if len(results) >= max_results // 2:
                return results[:max_results]
            
            # Strategy 2: Try individual words
            words = query.lower().split()
            for word in words:
                if len(word) > 3 and len(results) < max_results:  # Skip short words
                    params['search'] = word
                    response = requests.get(url, params=params, headers=headers, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    word_results = data[1] if len(data) > 1 else []
                    
                    for result in word_results:
                        if result not in results and len(results) < max_results:
                            results.append(result)
            
            # Strategy 3: Semantic variations for common topics
            semantic_map = {
                'mobility': ['transport', 'transportation', 'public transport', 'sustainable transport'],
                'transport': ['mobility', 'transportation', 'public transport', 'traffic'],
                'ai': ['artificial intelligence', 'machine learning', 'deep learning'],
                'ml': ['machine learning', 'artificial intelligence', 'data science'],
                'machine': ['machine learning', 'artificial intelligence', 'automation'],
                'learning': ['machine learning', 'education', 'training'],
                'climate': ['climate change', 'global warming', 'environment'],
                'space': ['space exploration', 'astronomy', 'spaceflight', 'NASA']
            }
            
            query_words = query.lower().split()
            for word in query_words:
                if word in semantic_map and len(results) < max_results:
                    for variation in semantic_map[word]:
                        if len(results) >= max_results:
                            break
                        params['search'] = variation
                        response = requests.get(url, params=params, headers=headers, timeout=10)
                        response.raise_for_status()
                        data = response.json()
                        var_results = data[1] if len(data) > 1 else []
                        
                        for result in var_results:
                            if result not in results and len(results) < max_results:
                                results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            print(f"Error searching Wikipedia: {e}")
            return []
    
    def create_course(self, topic: str, level: str = "beginner") -> Dict[str, Any]:
        """Create a complete course on the given topic."""
        return self.course_generator.create_full_course(topic, level)
    
    def create_quiz(self, topic: str, num_questions: int = 10) -> List[Dict[str, Any]]:
        """Create a quiz on the given topic."""
        return self.course_generator.generate_quiz(topic, num_questions)
    
    def save_course(self, course_data: Dict[str, Any], filename: str = None) -> str:
        """Save course to file."""
        return self.course_generator.save_course(course_data, filename)