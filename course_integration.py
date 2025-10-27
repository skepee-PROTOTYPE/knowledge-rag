"""
Integration module for Enhanced Course Generator
Connects the new multi-source course generator with the existing Flask app.
"""

import json
from flask import jsonify, request
from enhanced_course_generator import EnhancedCourseGenerator
from openai import OpenAI
import os
import logging

logger = logging.getLogger(__name__)

class CourseGeneratorIntegration:
    """Integration layer for enhanced course generation."""
    
    def __init__(self, app=None):
        self.enhanced_generator = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app."""
        try:
            client = OpenAI(
                api_key=os.getenv("GITHUB_TOKEN"),
                base_url="https://models.inference.ai.azure.com"
            )
            self.enhanced_generator = EnhancedCourseGenerator(client)
            logger.info("Enhanced course generator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize enhanced course generator: {e}")
            self.enhanced_generator = None
    
    def generate_enhanced_course(self, topic: str, level: str = "university", 
                               course_type: str = "comprehensive", quick_mode: bool = False) -> dict:
        """Generate enhanced course with multiple sources."""
        
        if not self.enhanced_generator:
            return {
                "error": "Enhanced course generator not available",
                "fallback": "Using basic generator"
            }
        
        try:
            # Update generator quick mode setting
            self.enhanced_generator.quick_mode = quick_mode
            
            if course_type == "comprehensive":
                course_data = self.enhanced_generator.generate_comprehensive_course(topic, level)
            else:
                # Future: could add other course types (quick, specialized, etc.)
                course_data = self.enhanced_generator.generate_comprehensive_course(topic, level)
            
            # Add metadata
            course_data["generation_info"] = {
                "generator_type": "enhanced_multi_source",
                "generation_mode": "quick" if quick_mode else "comprehensive",
                "sources_used": course_data.get("source_summary", {}),
                "generation_timestamp": self._get_timestamp(),
                "estimated_cost": "Low" if quick_mode else "Medium"
            }
            
            return course_data
            
        except Exception as e:
            logger.error(f"Enhanced course generation failed: {e}")
            return {
                "error": f"Enhanced generation failed: {str(e)}",
                "fallback": "Consider using basic generator"
            }
    
    def get_source_preview(self, topic: str, max_sources: int = 5) -> dict:
        """Preview available sources for a topic without generating full course."""
        
        if not self.enhanced_generator:
            return {"error": "Enhanced generator not available"}
        
        try:
            sources = self.enhanced_generator.search_multiple_sources(topic, max_per_source=2)
            
            source_preview = {
                "topic": topic,
                "total_sources_found": len(sources),
                "sources_by_type": {},
                "top_sources": []
            }
            
            # Count by type
            for source in sources:
                source_type = source.source_type
                if source_type not in source_preview["sources_by_type"]:
                    source_preview["sources_by_type"][source_type] = 0
                source_preview["sources_by_type"][source_type] += 1
            
            # Top sources preview
            for source in sources[:max_sources]:
                source_preview["top_sources"].append({
                    "title": source.title,
                    "type": source.source_type,
                    "credibility_score": source.credibility_score,
                    "preview": source.content[:200] + "..." if len(source.content) > 200 else source.content
                })
            
            return source_preview
            
        except Exception as e:
            logger.error(f"Source preview failed: {e}")
            return {"error": f"Source preview failed: {str(e)}"}
    
    def compare_generators(self, topic: str) -> dict:
        """Compare basic vs enhanced generator capabilities for a topic."""
        
        comparison = {
            "topic": topic,
            "basic_generator": {
                "primary_source": "Wikipedia only",
                "content_depth": "Basic reference material",
                "academic_rigor": "Limited",
                "course_structure": "Standard outline"
            },
            "enhanced_generator": {
                "sources": "Multiple authoritative sources",
                "content_depth": "University-level comprehensive",
                "academic_rigor": "High - academic standards",
                "course_structure": "Detailed with assessments, readings, projects"
            }
        }
        
        # Get source preview for enhanced generator
        if self.enhanced_generator:
            source_preview = self.get_source_preview(topic, max_sources=3)
            comparison["enhanced_generator"]["available_sources"] = source_preview.get("sources_by_type", {})
            comparison["enhanced_generator"]["source_quality"] = source_preview.get("top_sources", [])
        
        return comparison
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

# Flask route integration functions
def create_enhanced_course_routes(app, course_integration):
    """Create Flask routes for enhanced course generation."""
    
    @app.route('/api/course/enhanced', methods=['POST'])
    def generate_enhanced_course():
        """Generate comprehensive university-level course."""
        try:
            data = request.get_json()
            topic = data.get('topic', '')
            level = data.get('level', 'university')
            course_type = data.get('type', 'comprehensive')
            quick_mode = data.get('quick_mode', False)  # New: quick mode option
            
            if not topic:
                return jsonify({"error": "Topic is required"}), 400
            
            # Show estimated time
            estimated_time = "30-60 seconds" if quick_mode else "2-5 minutes"
            logger.info(f"Generating {'quick' if quick_mode else 'comprehensive'} course for: {topic} (est. {estimated_time})")
            
            # Generate enhanced course
            course_data = course_integration.generate_enhanced_course(topic, level, course_type, quick_mode)
            
            if "error" in course_data:
                return jsonify(course_data), 500
            
            return jsonify({
                "success": True,
                "course": course_data,
                "message": f"Enhanced course generated for {topic}",
                "generation_mode": "quick" if quick_mode else "comprehensive"
            })
            
        except Exception as e:
            logger.error(f"Enhanced course generation route error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/course/sources/preview', methods=['POST'])
    def preview_sources():
        """Preview available sources for a topic."""
        try:
            data = request.get_json()
            topic = data.get('topic', '')
            max_sources = data.get('max_sources', 5)
            
            if not topic:
                return jsonify({"error": "Topic is required"}), 400
            
            preview = course_integration.get_source_preview(topic, max_sources)
            
            return jsonify({
                "success": True,
                "preview": preview
            })
            
        except Exception as e:
            logger.error(f"Source preview route error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/course/compare', methods=['POST'])
    def compare_generators():
        """Compare basic vs enhanced course generation."""
        try:
            data = request.get_json()
            topic = data.get('topic', '')
            
            if not topic:
                return jsonify({"error": "Topic is required"}), 400
            
            comparison = course_integration.compare_generators(topic)
            
            return jsonify({
                "success": True,
                "comparison": comparison
            })
            
        except Exception as e:
            logger.error(f"Generator comparison route error: {e}")
            return jsonify({"error": str(e)}), 500

# Usage example for integration with existing app.py
def integrate_with_existing_app():
    """
    Example of how to integrate with your existing app.py:
    
    1. Add these imports to app.py:
       from course_integration import CourseGeneratorIntegration, create_enhanced_course_routes
    
    2. After creating the Flask app, add:
       course_integration = CourseGeneratorIntegration(app)
       create_enhanced_course_routes(app, course_integration)
    
    3. Update your course.html template to include enhanced generation options
    """
    pass

if __name__ == "__main__":
    # Test the integration
    import sys
    sys.path.append('.')
    
    from flask import Flask
    
    app = Flask(__name__)
    course_integration = CourseGeneratorIntegration(app)
    create_enhanced_course_routes(app, course_integration)
    
    # Test source preview
    preview = course_integration.get_source_preview("Machine Learning")
    print(json.dumps(preview, indent=2))