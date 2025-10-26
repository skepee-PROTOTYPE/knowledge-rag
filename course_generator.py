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
    
    def generate_module_content(self, module_title: str, topics: List[str]) -> Dict[str, Any]:
        """Generate detailed content for a specific module."""
        
        # Use the existing RAG system to gather relevant content
        module_content = {
            "title": module_title,
            "sections": []
        }
        
        for topic in topics:
            # Get relevant content from Wikipedia via RAG
            retrieved_chunks = self.wiki_rag.search_and_retrieve(topic, top_k=3)
            
            # Generate structured content
            content_prompt = f"""Create educational content for the topic "{topic}" as part of a module on "{module_title}".
            
            Use this Wikipedia content as reference:
            {self._format_chunks(retrieved_chunks)}
            
            Structure the content with:
            1. Introduction (2-3 sentences)
            2. Key concepts (3-5 main points)
            3. Detailed explanation
            4. Real-world examples
            5. Practice questions (3 questions)
            
            Make it educational, engaging, and appropriate for learners.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert educator creating course content."},
                    {"role": "user", "content": content_prompt}
                ],
                temperature=0.6
            )
            
            module_content["sections"].append({
                "topic": topic,
                "content": response.choices[0].message.content,
                "sources": [chunk.get("url", "") for chunk in retrieved_chunks]
            })
        
        return module_content
    
    def create_full_course(self, topic: str, level: str = "beginner") -> Dict[str, Any]:
        """Create a complete course with outline and content."""
        
        print(f"🎓 Generating course: {topic} ({level} level)")
        
        # Step 1: Generate course outline
        print("📋 Creating course outline...")
        outline = self.generate_course_outline(topic, level)
        
        # Step 2: Generate content for each module
        print("📚 Generating module content...")
        full_course = outline.copy()
        full_course["modules_content"] = []
        
        for i, module in enumerate(outline.get("modules", []), 1):
            print(f"   📖 Module {i}: {module['title']}")
            
            module_content = self.generate_module_content(
                module["title"], 
                module.get("topics", [])
            )
            
            full_course["modules_content"].append(module_content)
        
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
        """Enhanced Wikipedia search with fallback strategies."""
        try:
            import requests
            
            # Use Wikipedia API to search for articles
            search_url = "https://en.wikipedia.org/api/rest_v1/page/search"
            
            # Strategy 1: Try exact query
            params = {
                'q': query,
                'limit': max_results
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            search_data = response.json()
            results = [page['title'] for page in search_data.get('pages', [])]
            
            # If we got good results, return them
            if len(results) >= max_results // 2:
                return results[:max_results]
            
            # Strategy 2: Try individual words
            words = query.lower().split()
            for word in words:
                if len(word) > 3 and len(results) < max_results:  # Skip short words
                    params['q'] = word
                    response = requests.get(search_url, params=params, timeout=10)
                    response.raise_for_status()
                    search_data = response.json()
                    
                    for page in search_data.get('pages', []):
                        if page['title'] not in results and len(results) < max_results:
                            results.append(page['title'])
            
            # Strategy 3: Semantic variations for common topics
            semantic_map = {
                'mobility': ['transport', 'transportation', 'public transport', 'sustainable transport'],
                'transport': ['mobility', 'transportation', 'public transport', 'traffic'],
                'ai': ['artificial intelligence', 'machine learning', 'deep learning'],
                'ml': ['machine learning', 'artificial intelligence', 'data science'],
                'climate': ['climate change', 'global warming', 'environment'],
                'space': ['space exploration', 'astronomy', 'spaceflight', 'NASA']
            }
            
            query_words = query.lower().split()
            for word in query_words:
                if word in semantic_map and len(results) < max_results:
                    for variation in semantic_map[word]:
                        if len(results) >= max_results:
                            break
                        params['q'] = variation
                        response = requests.get(search_url, params=params, timeout=10)
                        response.raise_for_status()
                        search_data = response.json()
                        
                        for page in search_data.get('pages', []):
                            if page['title'] not in results and len(results) < max_results:
                                results.append(page['title'])
            
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