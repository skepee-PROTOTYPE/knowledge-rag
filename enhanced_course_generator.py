"""
Enhanced Course Generation Module
Integrates multiple authoritative sources for comprehensive university-level courses.
"""

import json
import requests
import time
from typing import List, Dict, Any, Optional
from openai import OpenAI
import os
from pathlib import Path
from dataclasses import dataclass
import logging
from educational_apis import EducationalAPIs

logger = logging.getLogger(__name__)

@dataclass
class ContentSource:
    """Represents a content source with metadata."""
    title: str
    url: str
    content: str
    source_type: str  # 'academic', 'textbook', 'research', 'reference'
    credibility_score: float  # 0.0 to 1.0
    date_published: Optional[str] = None

class EnhancedCourseGenerator:
    """Generate comprehensive university-level courses from multiple authoritative sources."""
    
    def __init__(self, client: OpenAI, quick_mode: bool = False):
        self.client = client
        self.content_sources = []
        self.quick_mode = quick_mode  # Quick mode reduces API calls for faster generation
        self.edu_apis = EducationalAPIs()  # Real API client for educational sources
        
    def search_multiple_sources(self, query: str, max_per_source: int = 3) -> List[ContentSource]:
        """Search across multiple academic and educational sources."""
        all_sources = []
        
        # 1. Wikipedia (baseline reference)
        wiki_sources = self._search_wikipedia_enhanced(query, max_per_source)
        all_sources.extend(wiki_sources)
        
        # 2. MIT OpenCourseWare
        mit_sources = self._search_mit_ocw(query, max_per_source)
        all_sources.extend(mit_sources)
        
        # 3. Khan Academy
        khan_sources = self._search_khan_academy(query, max_per_source)
        all_sources.extend(khan_sources)
        
        # 4. Coursera (public content)
        coursera_sources = self._search_coursera_public(query, max_per_source)
        all_sources.extend(coursera_sources)
        
        # 5. Academic papers (arXiv for STEM topics)
        if self._is_stem_topic(query):
            arxiv_sources = self._search_arxiv(query, max_per_source)
            all_sources.extend(arxiv_sources)
        
        # 6. Stanford Encyclopedia of Philosophy (for philosophy/humanities)
        if self._is_humanities_topic(query):
            sep_sources = self._search_stanford_encyclopedia(query, max_per_source)
            all_sources.extend(sep_sources)
        
        # Sort by credibility score and relevance
        return sorted(all_sources, key=lambda x: x.credibility_score, reverse=True)
    
    def _search_wikipedia_enhanced(self, query: str, max_results: int) -> List[ContentSource]:
        """Enhanced Wikipedia search with better content extraction."""
        sources = []
        try:
            import wikipediaapi
            
            wiki = wikipediaapi.Wikipedia(
                language='en',
                user_agent='EnhancedKnowledgeRAG/2.0 (educational)'
            )
            
            # Search for pages
            search_url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "opensearch",
                "search": query,
                "limit": max_results * 2,  # Get more to filter
                "format": "json"
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                titles = data[1] if len(data) > 1 else []
                
                for title in titles[:max_results]:
                    try:
                        page = wiki.page(title)
                        if page.exists():
                            # Extract structured content
                            content = self._extract_structured_content(page.text)
                            
                            sources.append(ContentSource(
                                title=title,
                                url=page.fullurl,
                                content=content,
                                source_type='reference',
                                credibility_score=0.7  # Wikipedia baseline
                            ))
                    except Exception as e:
                        logger.warning(f"Error processing Wikipedia page {title}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            
        return sources
    
    def _search_mit_ocw(self, query: str, max_results: int) -> List[ContentSource]:
        """Search MIT OpenCourseWare using real API client."""
        sources = []
        try:
            # Use real educational_apis module
            mit_results = self.edu_apis.search_mit_ocw(query, max_results)
            
            for result in mit_results:
                # Convert API result to ContentSource
                content = f"""
**{result['title']}**

{result['description']}

URL: {result['url']}
Source: {result['source']}
                """.strip()
                
                sources.append(ContentSource(
                    title=result['title'],
                    url=result['url'],
                    content=content,
                    source_type='academic',
                    credibility_score=result.get('credibility', 0.95)
                ))
                
        except Exception as e:
            logger.error(f"MIT OCW search error: {e}")
            
        return sources
    
    def _search_khan_academy(self, query: str, max_results: int) -> List[ContentSource]:
        """Search Khan Academy using real API client."""
        sources = []
        try:
            # Use real educational_apis module
            khan_results = self.edu_apis.search_khan_academy(query, max_results)
            
            for result in khan_results:
                sources.append(ContentSource(
                    title=result['title'],
                    url=result['url'],
                    content=result['description'],
                    source_type='educational',
                    credibility_score=result.get('credibility', 0.8)
                ))
                
        except Exception as e:
            logger.error(f"Khan Academy search error: {e}")
            
        return sources
    
    def _search_coursera_public(self, query: str, max_results: int) -> List[ContentSource]:
        """Search Coursera using real API client."""
        sources = []
        try:
            # Use real educational_apis module
            coursera_results = self.edu_apis.search_coursera(query, max_results)
            
            for result in coursera_results:
                sources.append(ContentSource(
                    title=result['title'],
                    url=result['url'],
                    content=result['description'],
                    source_type='educational',
                    credibility_score=result.get('credibility', 0.85)
                ))
                
        except Exception as e:
            logger.error(f"Coursera search error: {e}")
            
        return sources
    
    def _search_arxiv(self, query: str, max_results: int) -> List[ContentSource]:
        """Search arXiv using real API client."""
        sources = []
        try:
            # Use real educational_apis module
            arxiv_results = self.edu_apis.search_arxiv(query, max_results)
            
            for result in arxiv_results:
                sources.append(ContentSource(
                    title=result['title'],
                    url=result['url'],
                    content=result['description'],
                    source_type='research',
                    credibility_score=result.get('credibility', 0.85),
                    date_published=result.get('published', None)
                ))
                    
        except Exception as e:
            logger.error(f"arXiv search error: {e}")
            
        return sources
    
    def _search_stanford_encyclopedia(self, query: str, max_results: int) -> List[ContentSource]:
        """Search Stanford Encyclopedia using real API client."""
        sources = []
        try:
            # Use real educational_apis module
            sep_results = self.edu_apis.search_stanford_encyclopedia(query, max_results)
            
            for result in sep_results:
                sources.append(ContentSource(
                    title=result['title'],
                    url=result['url'],
                    content=result['description'],
                    source_type='academic',
                    credibility_score=result.get('credibility', 0.9)
                ))
                
        except Exception as e:
            logger.error(f"Stanford Encyclopedia search error: {e}")
            
        return sources
    
    def generate_comprehensive_course(self, topic: str, level: str = "university") -> Dict[str, Any]:
        """Generate a comprehensive university-level course from multiple sources."""
        
        print(f"🎓 Generating comprehensive {level}-level course: {topic}")
        print("📚 Searching multiple authoritative sources...")
        
        # Gather content from multiple sources
        all_sources = self.search_multiple_sources(topic, max_per_source=4)
        
        if not all_sources:
            print("⚠️  No sources found. Falling back to basic generation.")
            return self._generate_basic_course(topic, level)
        
        print(f"✅ Found {len(all_sources)} sources from multiple providers")
        
        # Generate enhanced course outline
        outline = self._generate_enhanced_outline(topic, level, all_sources)
        
        # Adjust module count based on mode
        modules_to_generate = outline["modules"]
        if self.quick_mode:
            print("⚡ Quick mode enabled - generating condensed course (3 modules)")
            modules_to_generate = modules_to_generate[:3]  # Limit to 3 modules
        else:
            print(f"📚 Full mode - generating comprehensive course ({len(modules_to_generate)} modules)")
        
        # Generate detailed modules with rich content
        course_data = {
            "course_title": outline["course_title"],
            "description": outline["description"],
            "level": level,
            "generation_mode": "quick" if self.quick_mode else "comprehensive",
            "source_summary": self._create_source_summary(all_sources),
            "learning_objectives": outline["learning_objectives"],
            "prerequisites": outline["prerequisites"],
            "modules": []
        }
        
        for i, module_outline in enumerate(modules_to_generate, 1):
            print(f"📖 Generating Module {i}/{len(modules_to_generate)}: {module_outline['title']}")
            
            module_content = self._generate_enhanced_module(
                module_outline, 
                all_sources, 
                topic, 
                level
            )
            course_data["modules"].append(module_content)
            
            # Rate limiting
            time.sleep(0.5 if self.quick_mode else 1)
        
        # Generate final capstone project
        print("🎯 Creating capstone project...")
        course_data["capstone_project"] = self._generate_capstone_project(topic, level, all_sources)
        
        # Add bibliography and further reading
        course_data["bibliography"] = self._create_bibliography(all_sources)
        course_data["further_reading"] = self._suggest_further_reading(topic, all_sources)
        
        print(f"✅ Comprehensive course generation complete!")
        return course_data
    
    def _generate_enhanced_outline(self, topic: str, level: str, sources: List[ContentSource]) -> Dict[str, Any]:
        """Generate comprehensive course outline using multiple authoritative sources."""
        
        source_summaries = "\n\n".join([
            f"**{source.title}** ({source.source_type}):\n{source.content[:800]}..."
            for source in sources[:8]  # Use more sources for comprehensive content
        ])
        
        prompt = f"""Create a COMPREHENSIVE and DETAILED {level}-level course outline for "{topic}".

Use these authoritative sources as foundation:
{source_summaries}

Create an extensive academic course with:

1. **Course Title and Detailed Description** (university catalog style - 150+ words)
   - Clear scope and academic focus
   - What students will master by completion
   - Connection to broader field of study
   - Practical applications and career relevance

2. **8-10 Specific Learning Objectives** aligned with Bloom's taxonomy
   - Include knowledge, comprehension, application, analysis, synthesis, evaluation
   - Make them measurable and assessment-aligned

3. **Detailed Prerequisites** 
   - Required prior courses with specific titles
   - Essential mathematical/technical background
   - Recommended preparatory reading

4. **12-16 Comprehensive Modules** covering the topic in depth
   For each module include:
   - Descriptive academic title (not just "Introduction to...")
   - 4-5 specific learning objectives
   - 8-12 key concepts, theories, and methodologies
   - 3-4 contact hours per module
   - Multiple assessment methods
   - Real-world applications and case studies
   - Current research connections
   - Industry relevance

5. **Course Structure Details**
   - Total credit hours (typically 3-4 for university)
   - Weekly schedule breakdown
   - Major project milestones
   - Assessment distribution

Make this a professional, graduate-level course that would be offered at a top university. Include advanced topics, current research, practical applications, and industry connections.

Format as detailed JSON with extensive content:
{{
    "course_title": "...",
    "course_code": "...",
    "description": "...",
    "total_credit_hours": "3-4",
    "weekly_hours": "...",
    "course_duration": "15 weeks",
    "learning_objectives": [...],
    "prerequisites": [...],
    "course_structure": {{...}},
    "modules": [...]
}}"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert academic curriculum designer creating university-level courses. Use scholarly language and academic standards."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return self._create_fallback_outline(topic, level)
    
    def _generate_enhanced_module(self, module_outline: Dict, sources: List[ContentSource], 
                                topic: str, level: str) -> Dict[str, Any]:
        """Generate detailed module content using multiple sources with extensive information."""
        
        # Filter sources relevant to this module
        relevant_sources = [s for s in sources if any(
            keyword.lower() in s.content.lower() 
            for keyword in module_outline.get("key_concepts", [])
        )][:5]  # Use more sources
        
        if not relevant_sources:
            relevant_sources = sources[:5]  # Use general sources
        
        module_content = {
            "module_number": module_outline.get("module_number", 1),
            "title": module_outline["title"],
            "duration": module_outline.get("duration", "2-3 weeks"),
            "contact_hours": module_outline.get("contact_hours", "6-8 hours"),
            "objectives": module_outline.get("objectives", []),
            "key_concepts": module_outline.get("key_concepts", []),
            "lessons": [],
            "lectures": [],
            "seminars": [],
            "labs_practicals": [],
            "readings": [],
            "assignments": [],
            "case_studies": [],
            "research_papers": [],
            "industry_connections": [],
            "assessment": {},
            "resources": []
        }
        
        # Generate comprehensive lessons (adjusted for mode)
        topics = module_outline.get("topics", [module_outline["title"]])
        key_concepts = module_outline.get("key_concepts", topics)
        
        # Combine topics and key concepts for comprehensive coverage
        all_lesson_topics = list(set(topics + key_concepts))
        
        # Adjust lesson count based on mode
        if self.quick_mode:
            max_lessons = 2  # Quick mode: 2 lessons per module
        else:
            max_lessons = 10  # Full mode: up to 10 lessons
        
        all_lesson_topics = all_lesson_topics[:max_lessons]
        
        for j, lesson_topic in enumerate(all_lesson_topics, 1):
            lesson_content = self._generate_comprehensive_lesson(
                lesson_topic, 
                module_outline["title"], 
                relevant_sources, 
                level
            )
            lesson_content["lesson_number"] = j
            module_content["lessons"].append(lesson_content)
        
        if not self.quick_mode:
            # Generate detailed lectures (only in full mode)
            module_content["lectures"] = self._generate_detailed_lectures(
                module_outline["title"], 
                key_concepts[:6],  # 6 main lecture topics
                relevant_sources, 
                level
            )
            
            # Generate seminars and discussions
            module_content["seminars"] = self._generate_seminars(
                module_outline["title"], 
                relevant_sources, 
                level
            )
            
            # Generate labs/practicals if applicable
            if self._is_practical_subject(topic):
                module_content["labs_practicals"] = self._generate_labs_practicals(
                module_outline["title"], 
                level
            )
        
        # Generate comprehensive reading list
        module_content["readings"] = self._generate_comprehensive_readings(
            module_outline["title"], 
            relevant_sources
        )
        
        # Generate diverse assignments
        module_content["assignments"] = self._generate_diverse_assignments(
            module_outline["title"], 
            relevant_sources, 
            level
        )
        
        # Generate case studies
        module_content["case_studies"] = self._generate_case_studies(
            module_outline["title"], 
            level
        )
        
        # Generate research paper connections
        module_content["research_papers"] = self._generate_research_connections(
            module_outline["title"], 
            relevant_sources
        )
        
        # Generate industry connections
        module_content["industry_connections"] = self._generate_industry_connections(
            module_outline["title"], 
            level
        )
        
        # Generate comprehensive assessment
        module_content["assessment"] = self._generate_comprehensive_assessment(
            module_outline["title"], 
            all_lesson_topics, 
            level
        )
        
        # Generate additional resources
        module_content["resources"] = self._generate_additional_resources(
            module_outline["title"], 
            relevant_sources
        )
        
        return module_content
    
    def _generate_university_lesson(self, topic: str, module_title: str, 
                                  sources: List[ContentSource], level: str) -> Dict[str, Any]:
        """Generate university-level lesson content."""
        
        source_content = "\n\n".join([
            f"**{source.title}**:\n{source.content[:800]}"
            for source in sources[:2]
        ])
        
        prompt = f"""Create a comprehensive university-level lesson on "{topic}" within the module "{module_title}".

Reference these authoritative sources:
{source_content}

Structure the lesson for {level} students with:

**Learning Objectives** (3-4 specific, measurable objectives)

**Theoretical Foundation** (key theories, concepts, historical context)

**Core Content** (detailed explanation with examples)

**Contemporary Applications** (current research, real-world applications)

**Critical Analysis** (different perspectives, debates, limitations)

**Discussion Questions** (thought-provoking questions for class discussion)

**Further Investigation** (research directions, advanced topics)

Use academic language appropriate for university students. Include citations to the source materials.
Make it engaging but scholarly."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a university professor creating detailed lecture content. Use scholarly language and academic rigor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=3000
        )
        
        return {
            "title": topic,
            "duration": "90 minutes",
            "content": response.choices[0].message.content,
            "sources_cited": [{"title": s.title, "url": s.url} for s in sources[:2]]
        }
    
    def _generate_comprehensive_lesson(self, topic: str, module_title: str, 
                                     sources: List[ContentSource], level: str) -> Dict[str, Any]:
        """Generate comprehensive lesson with extensive detail."""
        
        source_content = "\n\n".join([
            f"**{source.title}**:\n{source.content[:1000]}"
            for source in sources[:3]
        ])
        
        prompt = f"""Create an EXTENSIVE and DETAILED university lesson on "{topic}" for the module "{module_title}".

Reference materials:
{source_content}

Create a comprehensive lesson structure for {level} students including:

**LESSON OVERVIEW** (200+ words)
- Detailed introduction to the topic
- Connection to broader field and previous lessons
- Real-world relevance and applications

**LEARNING OBJECTIVES** (6-8 specific, measurable objectives using Bloom's taxonomy)
- Knowledge, comprehension, application, analysis, synthesis, evaluation levels

**THEORETICAL FOUNDATIONS** (500+ words)
- Historical development and key contributors
- Fundamental principles and core theories
- Mathematical/scientific foundations (if applicable)
- Relationship to other concepts in the field

**DETAILED CONTENT SECTIONS** (1000+ words total)
- Multiple subsections with clear headings
- In-depth explanations with examples
- Visual/conceptual representations described
- Step-by-step processes or methodologies
- Comparative analysis with alternative approaches

**CONTEMPORARY RESEARCH & DEVELOPMENTS** (300+ words)
- Current state of research
- Recent breakthroughs and discoveries
- Ongoing debates and controversies
- Future research directions

**PRACTICAL APPLICATIONS** (400+ words)
- Industry applications and use cases
- Real-world examples and case studies
- Professional implementation strategies
- Societal impact and implications

**CRITICAL ANALYSIS** (300+ words)
- Different schools of thought
- Limitations and criticisms
- Ethical considerations (if applicable)
- Comparative perspectives

**INTERACTIVE ELEMENTS**
- 8-10 thought-provoking discussion questions
- 3-4 problem-solving exercises
- Group activity suggestions
- Reflection prompts

**ASSESSMENT INTEGRATION**
- Formative assessment opportunities
- Connection to module assessments
- Self-evaluation guidelines

**EXTENDED LEARNING**
- Advanced topics for further study
- Research project suggestions
- Professional development connections
- Cross-disciplinary links

Use scholarly academic language appropriate for {level} education. Make it comprehensive, engaging, and intellectually rigorous."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a distinguished university professor creating comprehensive lesson content. Use extensive detail, scholarly language, and academic rigor. Make lessons thorough and intellectually demanding."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        return {
            "title": topic,
            "duration": "2-3 hours (including activities)",
            "format": "Lecture + Discussion + Activities",
            "content": response.choices[0].message.content,
            "sources_cited": [{"title": s.title, "url": s.url} for s in sources[:3]],
            "preparation_time": "45-60 minutes",
            "materials_needed": ["Projector", "Whiteboard", "Handouts", "Online resources"]
        }
    
    def _generate_detailed_lectures(self, module_title: str, key_concepts: List[str], 
                                   sources: List[ContentSource], level: str) -> List[Dict[str, Any]]:
        """Generate detailed lecture series for the module."""
        
        lectures = []
        for i, concept in enumerate(key_concepts, 1):
            
            prompt = f"""Create a detailed university lecture on "{concept}" within the "{module_title}" module.

Create a comprehensive {level}-level lecture including:

**LECTURE TITLE & OVERVIEW**
- Engaging title and 150+ word overview
- Learning outcomes specific to this lecture
- Prerequisites and preparation required

**LECTURE STRUCTURE** (75-90 minutes)
- Opening (10 min): Hook, objectives, roadmap
- Main content (60 min): 3-4 major sections with examples
- Synthesis (10-15 min): Summary, connections, questions

**DETAILED CONTENT OUTLINE**
- Section-by-section breakdown
- Key points to emphasize
- Examples and analogies to use
- Interactive moments and check-ins
- Visual aids and demonstrations

**SUPPORTING MATERIALS**
- Slide suggestions (10-15 slides)
- Handout requirements
- Multimedia resources
- Demonstration materials

**STUDENT ENGAGEMENT**
- Questions to pose during lecture
- Think-pair-share moments
- Real-time polling opportunities
- Case study integration

**ASSESSMENT CONNECTION**
- How this lecture connects to module assessments
- Key concepts students must master
- Common misconceptions to address

Make this lecture detailed enough for a professor to deliver effectively."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert lecturer creating detailed lecture plans for university courses. Be comprehensive and practical."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=3000
            )
            
            lectures.append({
                "lecture_number": i,
                "title": f"Lecture {i}: {concept}",
                "duration": "75-90 minutes",
                "format": "Interactive lecture",
                "content": response.choices[0].message.content,
                "materials": ["Projector", "Slides", "Handouts", "Interactive tools"]
            })
        
        return lectures
    
    def _generate_seminars(self, module_title: str, sources: List[ContentSource], 
                          level: str) -> List[Dict[str, Any]]:
        """Generate seminar sessions for deep discussion."""
        
        seminars = []
        seminar_topics = [
            f"Critical Analysis of {module_title}",
            f"Current Research in {module_title}",
            f"Ethical Implications of {module_title}",
            f"Future Directions in {module_title}"
        ]
        
        for i, topic in enumerate(seminar_topics[:3], 1):
            prompt = f"""Design a university seminar session on "{topic}" for {level} students.

Create a detailed seminar plan including:

**SEMINAR OVERVIEW**
- Purpose and learning objectives
- Connection to module content
- Expected outcomes

**PRE-SEMINAR PREPARATION** (for students)
- Required readings (3-4 sources)
- Preparation questions
- Research tasks

**SEMINAR STRUCTURE** (2 hours)
- Opening discussion (20 min)
- Small group analysis (40 min)
- Group presentations (45 min)
- Synthesis and reflection (15 min)

**DISCUSSION FRAMEWORK**
- 8-10 provocative questions
- Debate topics
- Case studies for analysis
- Role-playing scenarios

**FACILITATION NOTES**
- How to guide discussions
- Managing different viewpoints
- Encouraging participation
- Handling conflicts

**ASSESSMENT CRITERIA**
- Participation rubric
- Quality of contributions
- Evidence of preparation
- Critical thinking demonstration

Make this an engaging, intellectually rigorous seminar that promotes deep learning."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in seminar pedagogy, creating engaging discussion-based learning experiences."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2500
            )
            
            seminars.append({
                "seminar_number": i,
                "title": topic,
                "duration": "2 hours",
                "format": "Discussion-based seminar",
                "max_participants": "15-20 students",
                "content": response.choices[0].message.content
            })
        
        return seminars
    
    def _generate_labs_practicals(self, module_title: str, level: str) -> List[Dict[str, Any]]:
        """Generate laboratory/practical sessions."""
        
        labs = []
        lab_topics = [
            f"Hands-on {module_title} Implementation",
            f"{module_title} Case Study Analysis",
            f"Advanced {module_title} Techniques"
        ]
        
        for i, lab_topic in enumerate(lab_topics, 1):
            prompt = f"""Design a practical laboratory session on "{lab_topic}" for {level} students.

Create a comprehensive lab session including:

**LAB OVERVIEW**
- Learning objectives
- Skills to be developed
- Equipment/software needed

**PRE-LAB PREPARATION**
- Required reading
- Theoretical background review
- Setup instructions

**LAB PROCEDURE** (3 hours)
- Step-by-step instructions
- Safety considerations
- Troubleshooting guide
- Data collection methods

**EXERCISES & EXPERIMENTS**
- 4-6 hands-on activities
- Problem-solving challenges
- Group collaboration tasks

**ASSESSMENT & REPORTING**
- Lab report requirements
- Data analysis expectations
- Reflection questions

Make this practical and skill-building."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in laboratory education, creating hands-on learning experiences."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=2500
            )
            
            labs.append({
                "lab_number": i,
                "title": lab_topic,
                "duration": "3 hours",
                "format": "Hands-on practical",
                "content": response.choices[0].message.content
            })
        
        return labs
    
    def _generate_comprehensive_readings(self, module_title: str, sources: List[ContentSource]) -> List[Dict[str, Any]]:
        """Generate comprehensive reading list for the module."""
        readings = []
        
        # Add primary sources
        for source in sources:
            readings.append({
                "type": "primary",
                "title": source.title,
                "url": source.url,
                "source_type": source.source_type,
                "estimated_time": "45-60 minutes",
                "required": True,
                "credibility": source.credibility_score,
                "summary": source.content[:200] + "..." if len(source.content) > 200 else source.content
            })
        
        # Add comprehensive supplementary readings
        supplementary_types = [
            f"Foundational Theories in {module_title}",
            f"Contemporary Research on {module_title}",
            f"{module_title}: Critical Perspectives",
            f"Applied {module_title}: Industry Case Studies",
            f"Future Directions in {module_title} Research",
            f"Cross-disciplinary Approaches to {module_title}",
            f"Historical Development of {module_title}",
            f"Ethical Considerations in {module_title}"
        ]
        
        for i, supp_type in enumerate(supplementary_types, 1):
            readings.append({
                "type": "supplementary",
                "title": supp_type,
                "url": f"#reading-{i}",
                "source_type": "academic",
                "estimated_time": "30-45 minutes",
                "required": i <= 4,  # First 4 are required
                "description": f"Comprehensive analysis of {supp_type.lower()} including current research, methodologies, and practical applications."
            })
        
        # Add textbook chapters
        textbook_chapters = [
            f"Chapter on {module_title} Fundamentals",
            f"Advanced {module_title} Concepts",
            f"{module_title} Applications and Case Studies"
        ]
        
        for chapter in textbook_chapters:
            readings.append({
                "type": "textbook",
                "title": chapter,
                "url": "#textbook",
                "source_type": "educational",
                "estimated_time": "60-90 minutes",
                "required": True,
                "pages": "25-40 pages",
                "difficulty": "intermediate to advanced"
            })
        
        return readings
    
    def _generate_diverse_assignments(self, module_title: str, sources: List[ContentSource], 
                                     level: str) -> List[Dict[str, Any]]:
        """Generate diverse university-level assignments."""
        
        assignments = []
        
        # Research Essay Assignment
        prompt1 = f"""Create a comprehensive research essay assignment on "{module_title}" for {level} students.

Design an assignment that includes:

**ASSIGNMENT OVERVIEW**
- Clear purpose and learning objectives
- Connection to module content
- Academic skills development

**REQUIREMENTS**
- Word count: 3000-4000 words
- Minimum sources: 12-15 academic sources
- Citation style and formatting
- Structure requirements

**TOPIC OPTIONS** (provide 6-8 options)
- Analytical topics requiring critical thinking
- Comparative analysis opportunities
- Contemporary application studies
- Historical development analysis

**ASSESSMENT CRITERIA**
- Detailed rubric with specific criteria
- Weighting for different components
- Grade boundaries and expectations

**SUPPORT MATERIALS**
- Research guidance
- Writing resources
- Citation help
- Example topics and approaches

Make this challenging but achievable for {level} students."""

        response1 = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a university instructor designing challenging academic assignments."},
                {"role": "user", "content": prompt1}
            ],
            temperature=0.4,
            max_tokens=3000
        )
        
        assignments.append({
            "type": "research_essay",
            "title": f"{module_title} Research Analysis",
            "description": response1.choices[0].message.content,
            "due_date": "Week 3 of module",
            "weight": "30%",
            "estimated_time": "25-30 hours"
        })
        
        # Practical Project Assignment
        prompt2 = f"""Create a practical project assignment on "{module_title}" for {level} students.

Design a project that includes:

**PROJECT OVERVIEW**
- Hands-on application of module concepts
- Real-world relevance
- Skill development focus

**PROJECT OPTIONS** (provide 4-5 options)
- Implementation projects
- Case study analysis
- Design challenges
- Problem-solving scenarios

**DELIVERABLES**
- Written report (2000 words)
- Presentation (15-20 minutes)
- Practical demonstration/prototype
- Reflection journal

**TIMELINE**
- Proposal phase
- Development milestones
- Final presentation
- Peer review process

**ASSESSMENT CRITERIA**
- Technical competence
- Innovation and creativity
- Communication quality
- Project management

Make this engaging and professionally relevant."""

        response2 = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are designing practical, engaging projects for university students."},
                {"role": "user", "content": prompt2}
            ],
            temperature=0.5,
            max_tokens=2500
        )
        
        assignments.append({
            "type": "practical_project",
            "title": f"Applied {module_title} Project",
            "description": response2.choices[0].message.content,
            "due_date": "End of module",
            "weight": "40%",
            "estimated_time": "35-40 hours"
        })
        
        # Critical Analysis Assignment
        assignments.append({
            "type": "critical_analysis",
            "title": f"Critical Evaluation of {module_title} Approaches",
            "description": f"Comparative critical analysis of different approaches to {module_title}, requiring synthesis of multiple perspectives and development of original arguments.",
            "requirements": [
                "1500-2000 words",
                "Compare 3-4 different approaches/theories",
                "Develop original critical perspective",
                "Use minimum 8 academic sources"
            ],
            "due_date": "Week 2 of module",
            "weight": "20%",
            "estimated_time": "15-20 hours"
        })
        
        # Group Collaboration Assignment
        assignments.append({
            "type": "group_project",
            "title": f"Collaborative {module_title} Investigation",
            "description": f"Team-based investigation of contemporary issues in {module_title}, requiring coordination, research, and collective presentation.",
            "requirements": [
                "Teams of 4-5 students",
                "Joint presentation (30 minutes)",
                "Individual reflection (1000 words)",
                "Peer assessment component"
            ],
            "due_date": "Week 4 of module",
            "weight": "25%",
            "estimated_time": "20-25 hours per student"
        })
        
        return assignments
    
    def _generate_case_studies(self, module_title: str, level: str) -> List[Dict[str, Any]]:
        """Generate detailed case studies for the module."""
        
        case_studies = []
        
        case_topics = [
            f"Real-world Application of {module_title}",
            f"Industry Implementation of {module_title}",
            f"Historical Case in {module_title}",
            f"Contemporary Challenge in {module_title}"
        ]
        
        for i, case_topic in enumerate(case_topics, 1):
            prompt = f"""Create a detailed case study on "{case_topic}" for {level} students.

Develop a comprehensive case study including:

**CASE BACKGROUND**
- Setting and context (200+ words)
- Key stakeholders and players
- Timeline of events
- Industry/field relevance

**THE CHALLENGE/SITUATION**
- Core problem or opportunity
- Constraints and limitations
- Multiple perspectives involved
- Complexity factors

**RELEVANT THEORY/CONCEPTS**
- Module concepts that apply
- Theoretical frameworks to consider
- Academic literature connections

**ANALYSIS QUESTIONS** (8-10 questions)
- Descriptive questions (what happened?)
- Analytical questions (why did it happen?)
- Evaluative questions (how effective was it?)
- Predictive questions (what might happen?)

**LEARNING OBJECTIVES**
- Skills to be developed
- Knowledge to be applied
- Critical thinking opportunities

**DISCUSSION GUIDELINES**
- Group discussion structure
- Role-playing opportunities
- Debate topics
- Synthesis activities

**ADDITIONAL RESOURCES**
- Supporting materials
- Further reading
- Multimedia resources
- Expert interviews

Make this realistic, engaging, and pedagogically sound."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert case study developer for business and academic education."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=3000
            )
            
            case_studies.append({
                "case_number": i,
                "title": case_topic,
                "duration": "2-3 class sessions",
                "format": "Case analysis + discussion",
                "content": response.choices[0].message.content,
                "learning_outcomes": [
                    "Apply theoretical concepts to real situations",
                    "Develop analytical thinking skills",
                    "Practice decision-making",
                    "Understand practical implications"
                ]
            })
        
        return case_studies
    
    def _generate_research_connections(self, module_title: str, sources: List[ContentSource]) -> List[Dict[str, Any]]:
        """Generate research paper connections and current developments."""
        
        research_papers = []
        
        # Add research papers from sources
        for source in sources:
            if source.source_type == 'research':
                research_papers.append({
                    "title": source.title,
                    "url": source.url,
                    "relevance": "Direct application to module content",
                    "key_findings": source.content[:300] + "...",
                    "date": source.date_published or "Recent",
                    "application": f"Demonstrates current research directions in {module_title}"
                })
        
        # Add current research directions
        research_directions = [
            f"Emerging Trends in {module_title}",
            f"Computational Approaches to {module_title}",
            f"Interdisciplinary Research in {module_title}",
            f"Future Challenges in {module_title}"
        ]
        
        for direction in research_directions:
            research_papers.append({
                "title": direction,
                "url": "#research",
                "relevance": "Future research opportunities",
                "description": f"Current and emerging research directions in {direction.lower()}",
                "student_relevance": "Potential thesis topics and research projects"
            })
        
        return research_papers
    
    def _generate_industry_connections(self, module_title: str, level: str) -> List[Dict[str, Any]]:
        """Generate industry connections and professional relevance."""
        
        connections = []
        
        # Industry applications
        industry_apps = [
            {
                "sector": "Technology",
                "applications": f"How {module_title} is applied in tech companies",
                "roles": "Data Scientist, Research Engineer, Product Manager",
                "companies": "Major tech corporations, startups, consulting firms"
            },
            {
                "sector": "Healthcare",
                "applications": f"{module_title} applications in medical field",
                "roles": "Medical Researcher, Health Data Analyst, Biomedical Engineer",
                "companies": "Hospitals, pharmaceutical companies, medical device manufacturers"
            },
            {
                "sector": "Finance",
                "applications": f"Financial applications of {module_title}",
                "roles": "Quantitative Analyst, Risk Manager, Financial Engineer",
                "companies": "Banks, investment firms, insurance companies"
            },
            {
                "sector": "Education",
                "applications": f"Educational applications and research in {module_title}",
                "roles": "Researcher, Academic, Educational Technologist",
                "companies": "Universities, educational technology companies, think tanks"
            }
        ]
        
        for app in industry_apps:
            connections.append({
                "type": "industry_application",
                "sector": app["sector"],
                "description": app["applications"],
                "career_paths": app["roles"],
                "example_employers": app["companies"],
                "relevance": f"Direct application of {module_title} concepts in professional settings"
            })
        
        # Professional development
        connections.append({
            "type": "professional_development",
            "title": f"Professional Skills in {module_title}",
            "description": f"Key professional skills and competencies developed through {module_title}",
            "skills": [
                "Analytical thinking and problem solving",
                "Research and investigation",
                "Critical evaluation and synthesis",
                "Communication and presentation",
                "Project management and collaboration",
                "Technical implementation and application"
            ],
            "certifications": f"Relevant professional certifications in {module_title}",
            "networking": f"Professional organizations and conferences related to {module_title}"
        })
        
        return connections
    
    def _generate_additional_resources(self, module_title: str, sources: List[ContentSource]) -> List[Dict[str, Any]]:
        """Generate additional learning resources."""
        
        resources = []
        
        # Online resources
        online_resources = [
            {
                "type": "online_course",
                "title": f"Supplementary Online Course: Advanced {module_title}",
                "provider": "Coursera/edX/MIT OpenCourseWare",
                "description": f"Additional online learning opportunities in {module_title}",
                "duration": "4-6 weeks",
                "level": "Intermediate to Advanced"
            },
            {
                "type": "documentation",
                "title": f"{module_title} Documentation and Guides",
                "description": "Official documentation, API references, and implementation guides",
                "format": "Online documentation, tutorials, examples"
            },
            {
                "type": "tools_software",
                "title": f"Software Tools for {module_title}",
                "description": "Recommended software, libraries, and development tools",
                "examples": "Open source tools, commercial software, cloud platforms"
            }
        ]
        
        resources.extend(online_resources)
        
        # Books and publications
        book_resources = [
            {
                "type": "textbook",
                "title": f"Advanced {module_title} Textbook",
                "description": "Comprehensive textbook covering advanced concepts",
                "level": "Graduate level",
                "chapters": "15-20 chapters with exercises"
            },
            {
                "type": "handbook",
                "title": f"Professional Handbook of {module_title}",
                "description": "Practical reference for professionals",
                "format": "Reference guide with case studies"
            }
        ]
        
        resources.extend(book_resources)
        
        # Multimedia resources
        multimedia = [
            {
                "type": "videos",
                "title": f"Video Lectures on {module_title}",
                "description": "Curated video content from experts",
                "sources": "YouTube, academic institutions, conferences"
            },
            {
                "type": "podcasts",
                "title": f"Podcasts about {module_title}",
                "description": "Audio content featuring expert discussions",
                "frequency": "Weekly episodes, expert interviews"
            },
            {
                "type": "datasets",
                "title": f"Datasets for {module_title} Practice",
                "description": "Real-world datasets for hands-on practice",
                "format": "CSV, JSON, database formats"
            }
        ]
        
        resources.extend(multimedia)
        
        return resources
    
    def _is_practical_subject(self, topic: str) -> bool:
        """Check if topic requires practical/lab sessions."""
        practical_keywords = [
            'computer science', 'programming', 'engineering', 'data science',
            'machine learning', 'chemistry', 'physics', 'biology', 'statistics',
            'mathematics', 'design', 'architecture', 'laboratory', 'experimental'
        ]
        return any(keyword in topic.lower() for keyword in practical_keywords)
    
    def _generate_comprehensive_assessment(self, module_title: str, topics: List[str], 
                                          level: str) -> Dict[str, Any]:
        """Generate comprehensive university-level assessment strategy."""
        
        prompt = f"""Create a comprehensive assessment strategy for a {level}-level module on "{module_title}" covering topics: {', '.join(topics)}.

Design a multi-faceted assessment approach including:

**FORMATIVE ASSESSMENTS** (ongoing feedback)
- Weekly quizzes and check-ins
- Discussion participation
- Peer review activities
- Self-assessment tools

**SUMMATIVE ASSESSMENTS** (major evaluations)
- Midterm examination
- Research project/essay
- Practical application assignment
- Final comprehensive assessment

**ASSESSMENT BREAKDOWN**
- Detailed percentage weights
- Clear grading criteria
- Rubrics for each component
- Late submission policies

**ASSESSMENT CRITERIA**
- Learning objective alignment
- Bloom's taxonomy levels
- Skill development focus
- Academic integrity measures

**FEEDBACK MECHANISMS**
- Timely feedback procedures
- Improvement opportunities
- Grade appeal process
- Student support resources

Make assessments challenging, fair, and aligned with learning objectives."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in university-level assessment design and educational evaluation."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=3000
        )
        
        return {
            "strategy": "Comprehensive multi-modal assessment",
            "total_weight": "100%",
            "components": {
                "participation": {"weight": "15%", "description": "Class participation and engagement"},
                "assignments": {"weight": "35%", "description": "Research essays and practical projects"},
                "midterm_exam": {"weight": "20%", "description": "Comprehensive midterm examination"},
                "final_project": {"weight": "30%", "description": "Capstone project or final examination"}
            },
            "detailed_strategy": response.choices[0].message.content,
            "grading_scale": {
                "A": "90-100% (Excellent)",
                "B": "80-89% (Good)", 
                "C": "70-79% (Satisfactory)",
                "D": "60-69% (Minimal Pass)",
                "F": "Below 60% (Fail)"
            },
            "feedback_timeline": "Within 2 weeks of submission",
            "revision_opportunities": "One revision allowed for major assignments"
        }
    
    def _generate_required_readings(self, module_title: str, sources: List[ContentSource]) -> List[Dict[str, Any]]:
        """Generate required reading list for the module."""
        readings = []
        
        # Add primary sources
        for source in sources:
            readings.append({
                "type": "primary",
                "title": source.title,
                "url": source.url,
                "source_type": source.source_type,
                "estimated_time": "30-45 minutes",
                "required": True
            })
        
        # Add supplementary readings (simulated)
        supplementary = [
            f"Advanced {module_title}: Current Research Perspectives",
            f"{module_title} in Practice: Case Studies",
            f"Critical Analysis of {module_title} Theory"
        ]
        
        for supp in supplementary:
            readings.append({
                "type": "supplementary",
                "title": supp,
                "url": "#",
                "source_type": "academic",
                "estimated_time": "20-30 minutes",
                "required": False
            })
        
        return readings
    
    def _generate_university_assignments(self, module_title: str, sources: List[ContentSource], 
                                       level: str) -> List[Dict[str, Any]]:
        """Generate university-level assignments."""
        
        prompt = f"""Create 3 university-level assignments for a module on "{module_title}".

For {level} students, design:

1. **Research Assignment** - A scholarly research task requiring analysis of multiple sources
2. **Critical Essay** - An analytical essay requiring argumentation and evidence
3. **Practical Application** - A project applying concepts to real-world scenarios

Each assignment should include:
- Clear objectives and requirements
- Evaluation criteria
- Estimated time commitment
- Learning outcomes alignment
- Academic integrity guidelines

Make assignments challenging and intellectually rigorous."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a university instructor designing challenging academic assignments."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2000
        )
        
        return [
            {
                "type": "research",
                "title": f"{module_title} Research Analysis",
                "description": response.choices[0].message.content,
                "due_date": "End of module",
                "weight": "25%"
            }
        ]
    
    def _generate_university_assessment(self, module_title: str, topics: List[str], 
                                      level: str) -> Dict[str, Any]:
        """Generate comprehensive university-level assessment."""
        
        return {
            "midterm_exam": {
                "type": "written_exam",
                "duration": "90 minutes",
                "format": "Essay questions + problem solving",
                "weight": "30%"
            },
            "final_project": {
                "type": "research_project",
                "duration": "3 weeks",
                "format": "Written report + presentation",
                "weight": "40%"
            },
            "participation": {
                "type": "class_participation",
                "format": "Discussion + assignments",
                "weight": "30%"
            }
        }
    
    # Helper methods for content sources
    def _is_stem_topic(self, query: str) -> bool:
        """Check if topic is STEM-related."""
        stem_keywords = [
            'mathematics', 'physics', 'chemistry', 'biology', 'engineering',
            'computer science', 'statistics', 'calculus', 'algebra', 'quantum',
            'molecular', 'algorithm', 'programming', 'data science'
        ]
        return any(keyword in query.lower() for keyword in stem_keywords)
    
    def _is_humanities_topic(self, query: str) -> bool:
        """Check if topic is humanities-related."""
        humanities_keywords = [
            'philosophy', 'ethics', 'literature', 'history', 'art',
            'religion', 'theology', 'linguistics', 'anthropology',
            'sociology', 'psychology', 'political science'
        ]
        return any(keyword in query.lower() for keyword in humanities_keywords)
    
    def _extract_structured_content(self, text: str) -> str:
        """Extract and structure content from raw text."""
        # Simple content structuring (could be enhanced with NLP)
        return text[:2000]  # Limit length
    
    def _create_source_summary(self, sources: List[ContentSource]) -> Dict[str, Any]:
        """Create summary of all sources used."""
        return {
            "total_sources": len(sources),
            "by_type": {
                "academic": len([s for s in sources if s.source_type == 'academic']),
                "educational": len([s for s in sources if s.source_type == 'educational']),
                "research": len([s for s in sources if s.source_type == 'research']),
                "reference": len([s for s in sources if s.source_type == 'reference'])
            },
            "average_credibility": sum(s.credibility_score for s in sources) / len(sources) if sources else 0
        }
    
    def _create_bibliography(self, sources: List[ContentSource]) -> List[Dict[str, str]]:
        """Create formatted bibliography."""
        return [
            {
                "title": source.title,
                "url": source.url,
                "type": source.source_type,
                "credibility": f"{source.credibility_score:.1f}/1.0"
            }
            for source in sources
        ]
    
    def _suggest_further_reading(self, topic: str, sources: List[ContentSource]) -> List[str]:
        """Suggest additional reading materials."""
        suggestions = [
            f"Advanced {topic}: Research Frontiers",
            f"{topic} and Society: Contemporary Issues",
            f"Historical Development of {topic}",
            f"Cross-disciplinary Perspectives on {topic}"
        ]
        return suggestions
    
    def _generate_capstone_project(self, topic: str, level: str, sources: List[ContentSource]) -> Dict[str, Any]:
        """Generate comprehensive capstone project."""
        
        return {
            "title": f"Capstone Project: Advanced {topic} Research",
            "description": f"Comprehensive research project demonstrating mastery of {topic} concepts",
            "requirements": [
                "Original research question",
                "Literature review (minimum 15 sources)",
                "Methodology and analysis",
                "Written report (8000-10000 words)",
                "Oral presentation (20 minutes)"
            ],
            "timeline": "6 weeks",
            "evaluation_criteria": [
                "Research quality and originality (30%)",
                "Literature integration (25%)",
                "Analysis and conclusions (25%)",
                "Presentation quality (20%)"
            ]
        }
    
    # Placeholder methods for external content sources
    # These would be implemented with actual APIs or web scraping
    
    def _get_mit_course_topics(self, query: str) -> List[Dict[str, Any]]:
        """Get comprehensive MIT course topics related to query."""
        
        # Generate more detailed and realistic MIT-style course content
        course_variations = [
            {
                "title": f"Introduction to {query}: Foundations and Applications",
                "course_id": f"6.{query.replace(' ', '').upper()[:3]}",
                "description": f"""Comprehensive introduction to {query} covering fundamental concepts, 
                                theoretical foundations, and practical applications. Students will develop 
                                both analytical and implementation skills through lectures, problem sets, 
                                and hands-on projects. Emphasis on mathematical rigor, algorithmic thinking, 
                                and real-world problem solving.""",
                "objectives": [
                    f"Master fundamental principles and theories underlying {query}",
                    f"Develop mathematical and analytical skills for {query} problems",
                    f"Implement {query} algorithms and systems",
                    f"Apply {query} techniques to real-world challenges",
                    f"Critically evaluate {query} approaches and methodologies",
                    f"Design and conduct {query} experiments and research"
                ],
                "prerequisites": [
                    "Calculus I and II (18.01, 18.02)",
                    "Linear Algebra (18.06)",
                    "Probability and Statistics (6.041)",
                    "Programming experience (Python/Java/C++)"
                ],
                "textbooks": [
                    f"Elements of {query}: A Mathematical Introduction",
                    f"{query}: Theory and Practice (MIT Press)",
                    f"Advanced {query}: Algorithms and Applications",
                    f"Mathematical Foundations of {query}"
                ],
                "weekly_structure": {
                    "lectures": "3 hours",
                    "recitations": "2 hours", 
                    "lab_sessions": "3 hours",
                    "problem_sets": "8-10 hours"
                }
            },
            {
                "title": f"Advanced {query}: Theory and Research",
                "course_id": f"6.{query.replace(' ', '').upper()[:3]}.ADV",
                "description": f"""Graduate-level course exploring advanced topics in {query}, 
                                current research directions, and cutting-edge applications. 
                                Students will engage with primary literature, conduct original research, 
                                and present findings to the class.""",
                "objectives": [
                    f"Analyze current research literature in {query}",
                    f"Develop novel approaches to {query} problems",
                    f"Implement state-of-the-art {query} systems",
                    f"Conduct independent research in {query}",
                    f"Present research findings effectively"
                ],
                "prerequisites": [
                    f"Introduction to {query}",
                    "Advanced Mathematics",
                    "Research Methods"
                ],
                "textbooks": [
                    f"Recent Advances in {query} Research",
                    f"Theoretical {query}: A Graduate Perspective",
                    "Selected research papers and conference proceedings"
                ]
            },
            {
                "title": f"Applied {query}: Industry Applications and Case Studies",
                "course_id": f"15.{query.replace(' ', '').upper()[:3]}",
                "description": f"""Practical application of {query} in industry settings, 
                                featuring real-world case studies, industry partnerships, 
                                and hands-on projects. Students work on actual problems 
                                from partner companies and organizations.""",
                "objectives": [
                    f"Apply {query} to solve real industry problems",
                    f"Understand business applications of {query}",
                    f"Develop project management skills",
                    f"Work effectively in interdisciplinary teams",
                    f"Communicate technical concepts to non-technical audiences"
                ],
                "prerequisites": [
                    f"Fundamentals of {query}",
                    "Business basics or work experience"
                ],
                "textbooks": [
                    f"{query} in Practice: Industry Case Studies",
                    f"Business Applications of {query}",
                    "Selected industry reports and white papers"
                ]
            }
        ]
        
        return course_variations
    
    def _get_khan_academy_content(self, query: str) -> List[Dict[str, Any]]:
        """Get Khan Academy content for query."""
        # Placeholder
        return [
            {
                "title": f"{query} Basics",
                "url": f"https://khanacademy.org/{query.lower().replace(' ', '-')}",
                "description": f"Interactive lessons covering {query} fundamentals with exercises and examples."
            }
        ]
    
    def _get_coursera_courses(self, query: str) -> List[Dict[str, Any]]:
        """Get Coursera courses for query."""
        # Placeholder
        return [
            {
                "title": f"Complete {query} Specialization",
                "url": f"https://coursera.org/{query.lower().replace(' ', '-')}",
                "syllabus": f"Comprehensive specialization covering all aspects of {query} from basics to advanced applications."
            }
        ]
    
    def _parse_arxiv_response(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse arXiv XML response."""
        # Placeholder - would use proper XML parsing
        return [
            {
                "title": "Sample Academic Paper",
                "url": "https://arxiv.org/abs/sample",
                "abstract": "This paper presents recent findings in the field...",
                "date": "2024"
            }
        ]
    
    def _get_sep_entries(self, query: str) -> List[Dict[str, Any]]:
        """Get Stanford Encyclopedia entries."""
        # Placeholder
        return [
            {
                "title": f"{query} in Philosophy",
                "url": f"https://plato.stanford.edu/entries/{query.lower().replace(' ', '-')}/",
                "summary": f"Comprehensive philosophical analysis of {query} and its implications."
            }
        ]
    
    def _create_fallback_outline(self, topic: str, level: str) -> Dict[str, Any]:
        """Create comprehensive outline if source parsing fails."""
        
        # Generate a more detailed fallback outline
        base_modules = [
            f"Foundations of {topic}",
            f"Historical Development and Context of {topic}",
            f"Core Theories and Principles in {topic}",
            f"Methodologies and Approaches in {topic}",
            f"Contemporary Applications of {topic}",
            f"Research and Innovation in {topic}",
            f"Critical Analysis and Evaluation of {topic}",
            f"Future Directions and Emerging Trends in {topic}"
        ]
        
        modules = []
        for i, module_title in enumerate(base_modules, 1):
            modules.append({
                "module_number": i,
                "title": module_title,
                "duration": "2-3 weeks",
                "contact_hours": "6-8 hours",
                "objectives": [
                    f"Understand key concepts in {module_title.lower()}",
                    f"Apply {topic} principles to real-world scenarios",
                    f"Critically evaluate approaches in {module_title.lower()}",
                    f"Synthesize knowledge from multiple perspectives"
                ],
                "key_concepts": [
                    f"Fundamental principles of {topic}",
                    f"Historical development",
                    f"Current methodologies",
                    f"Research applications",
                    f"Critical perspectives"
                ],
                "topics": [
                    f"Introduction to {module_title.lower()}",
                    f"Theoretical frameworks",
                    f"Practical applications",
                    f"Case studies and examples"
                ]
            })
        
        return {
            "course_title": f"Comprehensive {topic} Studies",
            "course_code": f"{topic.replace(' ', '').upper()[:4]}401",
            "description": f"""This comprehensive {level}-level course provides an in-depth exploration of {topic}, 
                            covering foundational theories, contemporary research, practical applications, and critical analysis. 
                            Students will develop both theoretical understanding and practical skills through lectures, seminars, 
                            assignments, and hands-on projects. The course emphasizes critical thinking, research skills, 
                            and professional application of {topic} concepts.""",
            "total_credit_hours": "3-4",
            "weekly_hours": "3 hours lecture + 2 hours seminar/lab",
            "course_duration": "15 weeks",
            "learning_objectives": [
                f"Demonstrate comprehensive understanding of {topic} principles and theories",
                f"Apply {topic} methodologies to solve complex problems",
                f"Critically evaluate different approaches and perspectives in {topic}",
                f"Conduct independent research in {topic} areas",
                f"Communicate {topic} concepts effectively to diverse audiences",
                f"Integrate {topic} knowledge with other disciplinary perspectives",
                f"Demonstrate professional competency in {topic} applications"
            ],
            "prerequisites": [
                "Undergraduate degree or equivalent",
                f"Basic knowledge of related fields to {topic}",
                "Research methods and academic writing skills",
                "Mathematics and statistics (if applicable)"
            ],
            "course_structure": {
                "lectures": "2 hours per week",
                "seminars": "1 hour per week", 
                "practical_sessions": "2 hours per week",
                "independent_study": "6-8 hours per week",
                "assessment": "Continuous assessment + final project"
            },
            "modules": modules
        }
    
    def _generate_basic_course(self, topic: str, level: str) -> Dict[str, Any]:
        """Generate basic course when no sources available."""
        return {
            "course_title": f"Basic {topic} Course",
            "description": f"Introduction to {topic}",
            "level": level,
            "modules": [],
            "error": "Limited sources available"
        }

# Test the enhanced generator
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    client = OpenAI(
        api_key=os.getenv("GITHUB_TOKEN"),
        base_url="https://models.inference.ai.azure.com"
    )
    
    generator = EnhancedCourseGenerator(client)
    course = generator.generate_comprehensive_course("Machine Learning", "university")
    
    print(json.dumps(course, indent=2))