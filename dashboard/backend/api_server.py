"""
STEAM Dashboard API Server

Flask-based API server that connects the frontend dashboard with all backend
learning systems including project generation, instance management, and
educational framework integration.
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import traceback

# Add backend modules to path
sys.path.append('/workspaces/STEAM/dashboard/backend')
sys.path.append('/workspaces/STEAM')

# Import our backend systems
try:
    from learning_instance_manager import (
        LearningInstanceManager, LearnerProfile, LearningStyle, 
        MultipleIntelligence, EducationalFramework, DifficultyLevel
    )
    from project_generator import STEAMProjectGenerator, ProjectTheme
except ImportError as e:
    print(f"Warning: Could not import backend modules: {e}")
    # Create mock classes for development
    class LearningInstanceManager:
        def __init__(self): pass
        def get_personalized_recommendations(self, user_id): return {"themes": []}
    class STEAMProjectGenerator:
        def __init__(self): pass

# Initialize Flask app
app = Flask(__name__, 
           static_folder='/workspaces/STEAM/dashboard',
           template_folder='/workspaces/STEAM/dashboard')
CORS(app)

# Initialize backend systems
learning_manager = LearningInstanceManager()
project_generator = STEAMProjectGenerator()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('STEAM_API')

# Mock user data for development
MOCK_USERS = {
    "alex_student": {
        "user_id": "alex_student",
        "name": "Alex Student",
        "age": 14,
        "grade_level": "Grade 8",
        "current_level": 5,
        "streak_days": 7,
        "completed_projects": 15,
        "learning_style": "visual",
        "multiple_intelligences": ["logical_mathematical", "spatial"],
        "interests": ["robotics", "environmental science", "programming"],
        "active_projects": [
            {
                "project_id": "water_sustainability",
                "title": "Water Sustainability Challenge",
                "theme": "Environmental Sustainability",
                "progress": 65,
                "status": "in_progress",
                "frameworks": ["NGSS", "ISTE", "PBL"]
            }
        ],
        "completed_projects_list": [
            {
                "project_id": "mars_rover",
                "title": "Mars Rover Mission",
                "theme": "Space Exploration",
                "completion_date": "2024-09-15",
                "frameworks": ["OECD", "DIGICOMP", "NCF"]
            }
        ]
    }
}

# Routes

@app.route('/')
def dashboard():
    """Serve the main dashboard"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/user/<user_id>/profile')
def get_user_profile(user_id):
    """Get user profile information"""
    try:
        # For development, return mock data
        if user_id in MOCK_USERS:
            return jsonify({
                'success': True,
                'data': MOCK_USERS[user_id]
            })
        
        # In production, get from learning manager
        if user_id in learning_manager.learners:
            learner = learning_manager.learners[user_id]
            return jsonify({
                'success': True,
                'data': {
                    'user_id': learner.user_id,
                    'name': learner.name,
                    'age': learner.age,
                    'grade_level': learner.grade_level,
                    'current_level': learner.current_level,
                    'streak_days': learner.streak_days,
                    'completed_projects': learner.completed_projects,
                    'learning_style': learner.learning_style.value,
                    'multiple_intelligences': [mi.value for mi in learner.multiple_intelligences],
                    'interests': learner.interests
                }
            })
        
        return jsonify({
            'success': False,
            'error': 'User not found'
        }), 404
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user/<user_id>/projects')
def get_user_projects(user_id):
    """Get user's projects (active and completed)"""
    try:
        # Mock data for development
        if user_id in MOCK_USERS:
            user_data = MOCK_USERS[user_id]
            return jsonify({
                'success': True,
                'data': {
                    'active_projects': user_data.get('active_projects', []),
                    'completed_projects': user_data.get('completed_projects_list', []),
                    'suggested_projects': generate_suggested_projects(user_id)
                }
            })
        
        return jsonify({
            'success': False,
            'error': 'User not found'
        }), 404
        
    except Exception as e:
        logger.error(f"Error getting user projects: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat/message', methods=['POST'])
def chat_message():
    """Handle chat messages from the frontend"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_id = data.get('user_id', 'alex_student')
        context = data.get('context', {})
        
        # Process message and generate response
        response = process_chat_message(message, user_id, context)
        
        return jsonify({
            'success': True,
            'data': {
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'type': 'text'
            }
        })
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': {
                'response': "I'm having trouble processing your request right now. Let me help you with some quick suggestions instead!",
                'timestamp': datetime.now().isoformat(),
                'type': 'error'
            }
        })

@app.route('/api/project/generate', methods=['POST'])
def generate_project():
    """Generate a new personalized STEAM project"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'alex_student')
        theme = data.get('theme')
        frameworks = data.get('frameworks', [])
        difficulty = data.get('difficulty')
        include_robotics = data.get('include_robotics', True)
        include_coding = data.get('include_coding', True)
        
        # Generate project using our backend system
        project_data = generate_personalized_project(
            user_id, theme, frameworks, difficulty, include_robotics, include_coding
        )
        
        return jsonify({
            'success': True,
            'data': project_data
        })
        
    except Exception as e:
        logger.error(f"Error generating project: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/project/<project_id>/start', methods=['POST'])
def start_project(project_id):
    """Start a learning instance for a project"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'alex_student')
        
        # Create and start learning instance
        instance_data = start_learning_instance(user_id, project_id)
        
        return jsonify({
            'success': True,
            'data': instance_data
        })
        
    except Exception as e:
        logger.error(f"Error starting project: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/project/<project_id>/progress', methods=['POST'])
def update_project_progress(project_id):
    """Update progress on a learning instance"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'alex_student')
        activity_completed = data.get('activity_completed')
        time_spent = data.get('time_spent', 0)
        engagement_score = data.get('engagement_score', 3.0)
        artifacts = data.get('artifacts', [])
        
        # Update progress using learning manager
        progress_data = update_learning_progress(
            user_id, project_id, activity_completed, time_spent, engagement_score, artifacts
        )
        
        return jsonify({
            'success': True,
            'data': progress_data
        })
        
    except Exception as e:
        logger.error(f"Error updating progress: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user/<user_id>/recommendations')
def get_recommendations(user_id):
    """Get personalized learning recommendations"""
    try:
        recommendations = get_personalized_recommendations(user_id)
        
        return jsonify({
            'success': True,
            'data': recommendations
        })
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user/<user_id>/analytics')
def get_learning_analytics(user_id):
    """Get comprehensive learning analytics"""
    try:
        analytics = get_user_analytics(user_id)
        
        return jsonify({
            'success': True,
            'data': analytics
        })
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tools/<tool_name>/launch', methods=['POST'])
def launch_tool(tool_name):
    """Launch a specific STEAM tool"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'alex_student')
        context = data.get('context', {})
        
        tool_data = launch_steam_tool(tool_name, user_id, context)
        
        return jsonify({
            'success': True,
            'data': tool_data
        })
        
    except Exception as e:
        logger.error(f"Error launching tool {tool_name}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/robotics/modules')
def get_robotics_modules():
    """Get available robotics modules and capabilities"""
    try:
        modules_data = get_modi_modules_info()
        
        return jsonify({
            'success': True,
            'data': modules_data
        })
        
    except Exception as e:
        logger.error(f"Error getting robotics modules: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/coding/challenge', methods=['POST'])
def generate_coding_challenge():
    """Generate a personalized coding challenge"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'alex_student')
        topic = data.get('topic', 'data_analysis')
        difficulty = data.get('difficulty', 'intermediate')
        
        challenge_data = create_coding_challenge(user_id, topic, difficulty)
        
        return jsonify({
            'success': True,
            'data': challenge_data
        })
        
    except Exception as e:
        logger.error(f"Error generating coding challenge: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Helper Functions

def process_chat_message(message: str, user_id: str, context: Dict[str, Any]) -> str:
    """Process chat messages and generate appropriate responses"""
    
    message_lower = message.lower()
    
    # Intent recognition
    if any(word in message_lower for word in ['project', 'create', 'generate']):
        return generate_project_chat_response(user_id)
    elif any(word in message_lower for word in ['robot', 'robotics', 'modi']):
        return generate_robotics_chat_response(user_id)
    elif any(word in message_lower for word in ['code', 'coding', 'python', 'program']):
        return generate_coding_chat_response(user_id)
    elif any(word in message_lower for word in ['help', 'stuck', 'confused']):
        return generate_help_chat_response(user_id)
    elif any(word in message_lower for word in ['progress', 'analytics', 'stats']):
        return generate_analytics_chat_response(user_id)
    else:
        return generate_general_chat_response(message, user_id)

def generate_project_chat_response(user_id: str) -> str:
    """Generate project-related chat response"""
    
    user_data = MOCK_USERS.get(user_id, {})
    interests = user_data.get('interests', ['science', 'technology'])
    
    return f"""🎯 **Perfect! Let's create an amazing STEAM project for you!**

Based on your profile, I recommend these project themes:
• **Environmental Sustainability** - Perfect for your interest in {interests[0] if interests else 'science'}
• **Robotics Innovation** - Great way to apply your logical-mathematical thinking
• **Smart Cities Design** - Combines technology with creative problem-solving

**Your Personalized Project Features**:
✅ Visual learning materials (perfect for your learning style)
✅ Modi robotics integration
✅ Python coding challenges
✅ Real-world connections
✅ Multiple framework alignment (NGSS, ISTE, PBL)

**Next Steps**:
1. Choose a theme that excites you
2. I'll generate a complete project with learning outcomes
3. We'll set up your personal learning instance
4. Start building and learning!

Which theme interests you most? I can also suggest specific project ideas based on current events or your local community needs!"""

def generate_robotics_chat_response(user_id: str) -> str:
    """Generate robotics-related chat response"""
    
    return """🤖 **Welcome to the Robotics Lab! Let's build something incredible!**

**Your Modi Kit is Ready**:
• 🔗 **Network Module** - Connect to WiFi and share data
• 🌡️ **Environment Module** - Monitor temperature, humidity, light
• 🎮 **Input Modules** - Buttons, dials, joystick controls
• 📺 **Display Module** - Show information and feedback
• ⚙️ **Motor Module** - Create movement and mechanical actions

**Today's Robotics Challenge Ideas**:

**🌱 Smart Garden Bot**
- Monitor plant conditions automatically
- Water plants based on sensor data
- Send updates to your phone

**🚗 Autonomous Explorer**
- Navigate around obstacles
- Map your room or outdoor space
- Collect environmental data while moving

**🎵 Interactive Music Machine**
- Respond to your movements and gestures
- Create music based on environmental conditions
- Build a collaborative musical experience

**Python + Modi Programming**:
```python
import modi

# Get started with your modules
network = modi.Network()
env = modi.Environment()
motor = modi.Motor()

# Your creative code goes here!
```

Which robotics project excites you most? I can provide step-by-step building and programming guidance!"""

def generate_coding_chat_response(user_id: str) -> str:
    """Generate coding-related chat response"""
    
    user_data = MOCK_USERS.get(user_id, {})
    level = user_data.get('current_level', 3)
    
    if level <= 3:
        complexity = "beginner-friendly"
        topics = ["data visualization", "simple games", "interactive stories"]
    elif level <= 6:
        complexity = "intermediate"
        topics = ["data analysis", "web scraping", "automation tools"]
    else:
        complexity = "advanced"
        topics = ["machine learning", "AI applications", "complex simulations"]
    
    return f"""💻 **Let's dive into Python coding with STEAM applications!**

**Perfect Coding Challenges for Your Level {level}**:

**🔬 Data Science Challenge**:
```python
# Analyze real environmental data
import pandas as pd
import matplotlib.pyplot as plt

# Your mission: Find patterns in climate data
weather_data = pd.read_csv('local_weather.csv')
# What stories does the data tell?
```

**🤖 Robotics Programming**:
```python
# Control your Modi modules with Python
import modi
import time

env_module = modi.Environment()
motor_module = modi.Motor()

# Create intelligent robot behaviors
if env_module.light < 50:
    motor_module.speed = 30  # Slow in dark
else:
    motor_module.speed = 60  # Normal speed
```

**🎨 Creative Coding**:
```python
# Generate beautiful patterns with math
import turtle
import math

# Create fractal art with algorithms
# Combine mathematics with visual creativity
```

**Your {complexity.title()} Coding Path**:
• Focus areas: {', '.join(topics[:2])}
• Real-world applications with STEAM integration
• Projects that connect to your interests
• Step-by-step guidance with immediate feedback

What type of coding challenge interests you most? I can create a personalized challenge that combines programming with your favorite subjects!"""

def generate_help_chat_response(user_id: str) -> str:
    """Generate help-related chat response"""
    
    return """🤝 **I'm here to help! Let's work through this together.**

**Immediate Support Options**:

🎯 **Break It Down**
- Let's split complex problems into smaller, manageable steps
- I can provide visual guides and examples
- We'll go at your own pace

🔍 **Different Approaches**
- Visual explanations with diagrams and examples
- Hands-on activities you can try right now
- Alternative methods that match your learning style

💡 **Learning Resources**
- Interactive tutorials and step-by-step guides
- Video explanations and demonstrations
- Practice activities with immediate feedback

🌟 **Encouragement & Growth**
- Remember: Every expert was once a beginner!
- Mistakes are learning opportunities
- You're building valuable 21st-century skills

**Tell me more about what you're working on**:
- What specific part feels challenging?
- What have you tried so far?
- What type of explanation would help most?

**Quick Help Topics**:
• Understanding project requirements
• Debugging code or circuits
• Organizing your research and ideas
• Planning your next steps
• Connecting concepts to real-world applications

I'm designed to adapt to your learning style and provide exactly the support you need. What would be most helpful right now?"""

def generate_analytics_chat_response(user_id: str) -> str:
    """Generate analytics-related chat response"""
    
    user_data = MOCK_USERS.get(user_id, {})
    
    return f"""📊 **Your Learning Analytics Dashboard**

**🎉 Amazing Progress, {user_data.get('name', 'Learner')}!**

**Current Stats**:
• **Level**: {user_data.get('current_level', 5)} (STEAM Explorer)
• **Streak**: {user_data.get('streak_days', 7)} days of consistent learning 🔥
• **Projects Completed**: {user_data.get('completed_projects', 15)}
• **Learning Style**: {user_data.get('learning_style', 'visual').title()} learner

**Recent Achievements**:
✅ Completed "Mars Rover Mission" project
✅ 65% progress on "Water Sustainability Challenge"
✅ Maintained 7-day learning streak
✅ Demonstrated strong problem-solving skills

**Learning Trends**:
📈 **Engagement**: High and consistent
📈 **Challenge Level**: Appropriately matched to your growth
📈 **STEAM Integration**: Excellent cross-disciplinary connections
📈 **Collaboration**: Active peer interaction

**Strengths Identified**:
• **Logical-Mathematical Intelligence**: Strong pattern recognition
• **Spatial Intelligence**: Excellent 3D visualization skills
• **Visual Learning**: Effective use of diagrams and models
• **Persistence**: Consistent effort despite challenges

**Growth Opportunities**:
• Try more collaborative projects to develop interpersonal skills
• Explore artistic expression in STEAM projects
• Consider mentoring younger learners

**Recommendations for Continued Growth**:
1. **Next Challenge Level**: Ready for advanced projects
2. **New Themes**: AI and Machine Learning projects
3. **Leadership Role**: Become a peer mentor
4. **Extended Projects**: Multi-week deep-dive investigations

Want to see detailed analytics for any specific area? I can show you:
• Time spent by subject area
• Skill development progression
• Framework standards mastery
• Project completion patterns"""

def generate_general_chat_response(message: str, user_id: str) -> str:
    """Generate general chat response"""
    
    user_data = MOCK_USERS.get(user_id, {})
    name = user_data.get('name', 'Learner')
    
    return f"""Thanks for sharing that with me, {name}! 

I'm your STEAM learning companion, designed to make your educational journey engaging and personalized. I can help you with:

🎨 **Create** - Design interdisciplinary projects that combine Science, Technology, Engineering, Arts, and Mathematics
🤖 **Build** - Guide you through robotics experiments with the Modi kit
💻 **Code** - Develop Python programming skills through STEAM applications
📚 **Learn** - Generate personalized lesson plans and learning experiences
🌟 **Grow** - Provide challenges that stretch your abilities while building confidence

**What I Know About You**:
• Visual learner with strong logical-mathematical and spatial intelligence
• Current Level {user_data.get('current_level', 5)} STEAM Explorer
• Interests in {', '.join(user_data.get('interests', ['science', 'technology']))}

**How I Adapt to You**:
• Visual explanations with diagrams and interactive models
• Step-by-step logical progressions
• Hands-on building and experimentation opportunities
• Real-world connections that matter to you

What aspect of STEAM learning would you like to explore today? I'm here to guide you on an exciting educational adventure!"""

def generate_suggested_projects(user_id: str) -> List[Dict[str, Any]]:
    """Generate suggested projects for a user"""
    
    return [
        {
            "project_id": "smart_garden",
            "title": "Smart Garden Ecosystem",
            "theme": "Environmental Sustainability",
            "description": "Create an automated garden system combining IoT, biology, and data analysis.",
            "difficulty": "intermediate",
            "estimated_hours": 25,
            "frameworks": ["STEAM", "Multiple Intelligence", "Learning Styles"],
            "reason": "Perfect match for your environmental interests and logical-mathematical intelligence"
        },
        {
            "project_id": "ai_music",
            "title": "AI Music Composition Lab",
            "theme": "Artificial Intelligence",
            "description": "Explore machine learning by creating AI that composes music based on emotions and patterns.",
            "difficulty": "advanced",
            "estimated_hours": 30,
            "frameworks": ["ISTE", "DIGICOMP", "OECD"],
            "reason": "Combines your programming skills with creative expression"
        },
        {
            "project_id": "space_communication",
            "title": "Deep Space Communication System",
            "theme": "Space Exploration",
            "description": "Design communication protocols for Mars missions using physics and engineering principles.",
            "difficulty": "advanced",
            "estimated_hours": 35,
            "frameworks": ["NGSS", "ISTE", "PBL"],
            "reason": "Builds on your successful Mars Rover project with increased complexity"
        }
    ]

def generate_personalized_project(user_id: str, theme: str, frameworks: List[str], 
                                difficulty: str, include_robotics: bool, include_coding: bool) -> Dict[str, Any]:
    """Generate a personalized project"""
    
    # Mock project generation for development
    project_data = {
        "project_id": f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "title": f"Custom {theme} Challenge",
        "description": f"A personalized {theme} project designed specifically for your learning style and interests.",
        "theme": theme,
        "difficulty": difficulty or "intermediate",
        "estimated_hours": 25,
        "frameworks": frameworks or ["NGSS", "ISTE", "PBL"],
        "learning_outcomes": [
            {
                "outcome_id": "lo_1",
                "description": "Apply scientific practices to investigate real-world phenomena",
                "framework": "NGSS",
                "assessment_criteria": ["Formulates questions", "Collects data", "Analyzes results"]
            },
            {
                "outcome_id": "lo_2", 
                "description": "Use technology tools for data collection and analysis",
                "framework": "ISTE",
                "assessment_criteria": ["Selects appropriate tools", "Uses tools effectively", "Interprets results"]
            }
        ],
        "steam_components": {
            "Science": ["Scientific inquiry", "Data collection", "Evidence-based reasoning"],
            "Technology": ["Digital tools", "Data visualization", "Simulation software"],
            "Engineering": ["Design process", "Problem solving", "System optimization"],
            "Arts": ["Creative communication", "Visual design", "Storytelling"],
            "Mathematics": ["Statistical analysis", "Mathematical modeling", "Pattern recognition"]
        },
        "robotics_components": [
            "Modi Environment Module for sensor data",
            "Network Module for data transmission", 
            "Display Module for real-time feedback"
        ] if include_robotics else [],
        "coding_elements": [
            "Python data analysis scripts",
            "Visualization with matplotlib",
            "Statistical analysis with pandas",
            "Algorithm development"
        ] if include_coding else [],
        "materials": ["Computer/tablet", "Modi robotics kit", "Sensors", "Building materials"],
        "timeline": [
            {"week": 1, "focus": "Research and planning", "activities": ["Background research", "Goal setting"]},
            {"week": 2, "focus": "Design and prototyping", "activities": ["System design", "Initial build"]},
            {"week": 3, "focus": "Testing and refinement", "activities": ["Data collection", "Analysis"]},
            {"week": 4, "focus": "Documentation and presentation", "activities": ["Results analysis", "Final presentation"]}
        ]
    }
    
    return project_data

def start_learning_instance(user_id: str, project_id: str) -> Dict[str, Any]:
    """Start a learning instance"""
    
    return {
        "instance_id": f"inst_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "user_id": user_id,
        "project_id": project_id,
        "status": "started",
        "start_date": datetime.now().isoformat(),
        "first_activity": {
            "activity_id": "intro_001",
            "title": "Project Introduction and Goal Setting",
            "description": "Let's explore your project and set personal learning goals.",
            "estimated_duration": 15,
            "instructions": [
                "Review the project overview and objectives",
                "Think about what you already know about this topic",
                "Set 2-3 personal learning goals",
                "Create your project workspace and timeline"
            ]
        },
        "adaptations": [
            "Visual step-by-step guides provided",
            "Interactive diagrams and models included",
            "Immediate feedback mechanisms enabled",
            "Choice in presentation formats available"
        ]
    }

def update_learning_progress(user_id: str, project_id: str, activity_completed: str, 
                           time_spent: int, engagement_score: float, artifacts: List[str]) -> Dict[str, Any]:
    """Update learning progress"""
    
    return {
        "progress_percentage": min(100, 35 + (time_spent * 2)),  # Mock calculation
        "status": "in_progress",
        "next_activity": {
            "activity_id": "research_001",
            "title": "Background Research and Investigation",
            "description": "Conduct research on your chosen topic using reliable sources.",
            "estimated_duration": 30,
            "instructions": [
                "Use at least 3 different types of sources",
                "Take notes using the provided research template",
                "Identify key questions for investigation",
                "Create a preliminary hypothesis or design challenge"
            ]
        },
        "achievements": [
            "Completed project introduction",
            "Set clear learning goals",
            "Demonstrated engagement and enthusiasm"
        ],
        "time_spent_total": 45 + time_spent,
        "engagement_trend": "increasing"
    }

def get_personalized_recommendations(user_id: str) -> Dict[str, Any]:
    """Get personalized recommendations"""
    
    return {
        "suggested_themes": [
            {"theme": "Artificial Intelligence", "relevance_score": 85, "reason": "Matches logical-mathematical intelligence"},
            {"theme": "Smart Cities", "relevance_score": 80, "reason": "Combines technology with creative problem-solving"},
            {"theme": "Ocean Conservation", "relevance_score": 75, "reason": "Environmental focus with data analysis opportunities"}
        ],
        "skill_development": [
            {"skill": "Advanced Python Programming", "current_level": 65, "next_milestone": "Machine Learning Integration"},
            {"skill": "Systems Thinking", "current_level": 78, "next_milestone": "Complex System Modeling"},
            {"skill": "Data Visualization", "current_level": 72, "next_milestone": "Interactive Dashboards"}
        ],
        "learning_path_suggestions": [
            {
                "path_title": "AI and Machine Learning Journey",
                "description": "Progressive path from basic AI concepts to advanced applications",
                "estimated_weeks": 8,
                "projects": ["AI Chatbot", "Image Recognition", "Predictive Modeling"]
            }
        ],
        "collaboration_opportunities": [
            {
                "type": "Peer Project",
                "title": "Climate Change Solutions Team",
                "description": "Join other students working on environmental challenges",
                "participants": 4
            }
        ]
    }

def get_user_analytics(user_id: str) -> Dict[str, Any]:
    """Get user analytics"""
    
    return {
        "learning_summary": {
            "total_projects": 16,
            "completed_projects": 15,
            "in_progress_projects": 1,
            "total_learning_hours": 87,
            "average_engagement": 4.2,
            "current_level": 5,
            "streak_days": 7
        },
        "skill_progression": {
            "Science": {"level": 78, "trend": "increasing"},
            "Technology": {"level": 85, "trend": "stable"}, 
            "Engineering": {"level": 72, "trend": "increasing"},
            "Arts": {"level": 65, "trend": "stable"},
            "Mathematics": {"level": 82, "trend": "increasing"}
        },
        "framework_mastery": {
            "NGSS": 75,
            "ISTE": 88,
            "PBL": 70,
            "OECD": 65
        },
        "learning_patterns": {
            "preferred_session_length": "25-30 minutes",
            "most_productive_time": "afternoon",
            "collaboration_preference": "small groups",
            "challenge_level_preference": "moderate stretch"
        },
        "recent_achievements": [
            {"date": "2024-10-01", "achievement": "Completed Mars Rover project with distinction"},
            {"date": "2024-09-28", "achievement": "Reached Level 5 STEAM Explorer status"},
            {"date": "2024-09-25", "achievement": "Started 7-day learning streak"}
        ]
    }

def launch_steam_tool(tool_name: str, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Launch a STEAM tool"""
    
    tool_responses = {
        "project-generator": {
            "tool": "Project Generator",
            "status": "launched",
            "interface": "modal",
            "features": [
                "AI-powered project creation",
                "Framework alignment",
                "Personalized adaptations",
                "Real-world connections"
            ],
            "next_steps": ["Select theme", "Choose frameworks", "Set preferences", "Generate project"]
        },
        "robotics-lab": {
            "tool": "Robotics Lab",
            "status": "launched", 
            "interface": "interactive",
            "available_modules": ["Network", "Environment", "Motor", "Display", "Input"],
            "suggested_projects": ["Line-following robot", "Environmental monitor", "Interactive pet"],
            "programming_options": ["Block-based", "Python text", "Hybrid mode"]
        },
        "code-playground": {
            "tool": "Code Playground",
            "status": "launched",
            "interface": "editor",
            "features": ["Syntax highlighting", "Real-time error checking", "STEAM examples", "Step-by-step tutorials"],
            "available_libraries": ["matplotlib", "pandas", "numpy", "requests", "modi"],
            "current_challenge": "Climate Data Analysis"
        }
    }
    
    return tool_responses.get(tool_name, {
        "tool": tool_name,
        "status": "error",
        "message": "Tool not found"
    })

def get_modi_modules_info() -> Dict[str, Any]:
    """Get Modi robotics modules information"""
    
    return {
        "available_modules": {
            "Network": {
                "description": "WiFi and Bluetooth connectivity",
                "capabilities": ["Data transmission", "Cloud integration", "Remote control"],
                "age_range": "10+",
                "difficulty": "intermediate"
            },
            "Environment": {
                "description": "Environmental sensing",
                "capabilities": ["Temperature", "Humidity", "Light", "Sound level"],
                "age_range": "8+",
                "difficulty": "beginner"
            },
            "Motor": {
                "description": "Movement and rotation control",
                "capabilities": ["Speed control", "Direction control", "Position tracking"],
                "age_range": "8+",
                "difficulty": "beginner"
            },
            "Display": {
                "description": "Visual output and feedback",
                "capabilities": ["Text display", "Numbers", "Simple graphics", "Status indicators"],
                "age_range": "6+",
                "difficulty": "beginner"
            }
        },
        "project_templates": [
            {
                "title": "Smart Weather Station",
                "modules": ["Environment", "Network", "Display"],
                "description": "Monitor and report weather conditions",
                "difficulty": "intermediate"
            },
            {
                "title": "Automated Pet Feeder",
                "modules": ["Motor", "Display", "Network"],
                "description": "Schedule and control pet feeding",
                "difficulty": "intermediate"
            }
        ],
        "programming_resources": {
            "getting_started": "Basic Modi programming tutorial",
            "examples": "Sample code for common tasks",
            "documentation": "Complete API reference"
        }
    }

def create_coding_challenge(user_id: str, topic: str, difficulty: str) -> Dict[str, Any]:
    """Create a personalized coding challenge"""
    
    challenges = {
        "data_analysis": {
            "title": "Climate Data Detective",
            "description": "Analyze real climate data to discover trends and patterns",
            "starter_code": """
import pandas as pd
import matplotlib.pyplot as plt

# Load climate data
data = pd.read_csv('climate_data.csv')

# Your mission: Find the trends!
# 1. Calculate average temperatures by year
# 2. Create visualizations
# 3. Identify patterns
# 4. Make predictions

def analyze_temperature_trends(data):
    # TODO: Your code here
    pass

def create_visualization(data):
    # TODO: Create compelling charts
    pass

def predict_future_trends(data):
    # TODO: Use simple modeling
    pass
""",
            "learning_objectives": [
                "Data manipulation with pandas",
                "Statistical analysis techniques", 
                "Data visualization principles",
                "Pattern recognition skills"
            ],
            "hints": [
                "Start by exploring the data structure",
                "Use groupby() for aggregating data",
                "matplotlib.pyplot has many chart types",
                "Look for seasonal and yearly patterns"
            ],
            "extensions": [
                "Add real-time data from weather APIs",
                "Create interactive visualizations",
                "Apply machine learning models",
                "Build a web dashboard"
            ]
        }
    }
    
    return challenges.get(topic, {
        "title": f"{topic.title()} Challenge",
        "description": f"Personalized {difficulty} level challenge for {topic}",
        "starter_code": "# Your coding adventure starts here!\nprint('Hello, STEAM coder!')",
        "learning_objectives": ["Problem solving", "Programming skills", "Creative thinking"]
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Development server
    app.run(debug=True, host='0.0.0.0', port=5000)