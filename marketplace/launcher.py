#!/usr/bin/env python3
"""
STEAM Marketplace Application Launcher

Comprehensive launcher script that initializes and starts the complete
STEAM Marketplace ecosystem including backend API, frontend server,
and database initialization.
"""

import os
import sys
import subprocess
import time
import signal
import threading
import json
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / 'backend'))

from marketplace_manager import marketplace_manager
from marketplace_models import MARKETPLACE_CONFIG

class MarketplaceLauncher:
    """
    Main launcher class for the STEAM Marketplace application.
    Manages backend API server, frontend server, and application lifecycle.
    """
    
    def __init__(self):
        self.processes = []
        self.running = False
        self.base_dir = Path(__file__).parent
        self.backend_dir = self.base_dir / 'backend'
        self.frontend_dir = self.base_dir / 'frontend'
        
    def initialize_database(self):
        """Initialize the marketplace database with sample data"""
        print("🔄 Initializing marketplace database...")
        
        try:
            # Initialize database
            marketplace_manager.initialize_database()
            
            # Create sample data if database is empty
            creators = marketplace_manager.get_all_creators()
            if not creators:
                self.create_sample_data()
            
            print("✅ Database initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            return False
    
    def create_sample_data(self):
        """Create sample creators and content for demonstration"""
        print("📝 Creating sample data...")
        
        try:
            # Sample creators
            sample_creators = [
                {
                    'username': 'dr_smith',
                    'email': 'dr.smith@university.edu',
                    'display_name': 'Dr. Sarah Smith',
                    'profile_type': 'teacher',
                    'institution': 'MIT',
                    'country': 'United States',
                    'bio': 'Professor of Computer Science specializing in AI and robotics education.',
                    'specializations': ['artificial_intelligence', 'robotics', 'programming']
                },
                {
                    'username': 'eng_builder',
                    'email': 'mike@maker.space',
                    'display_name': 'Mike the Builder',
                    'profile_type': 'content_creator',
                    'institution': 'Maker Space Community',
                    'country': 'Canada',
                    'bio': 'Mechanical engineer passionate about hands-on STEAM learning.',
                    'specializations': ['engineering', 'maker_projects', '3d_printing']
                },
                {
                    'username': 'art_science',
                    'email': 'elena@artscience.org',
                    'display_name': 'Elena Rodriguez',
                    'profile_type': 'teacher',
                    'institution': 'International Arts & Science Academy',
                    'country': 'Spain',
                    'bio': 'Interdisciplinary educator combining arts with scientific exploration.',
                    'specializations': ['arts_integration', 'science', 'creative_thinking']
                }
            ]
            
            created_creators = []
            for creator_data in sample_creators:
                creator = marketplace_manager.create_creator(creator_data)
                created_creators.append(creator)
                print(f"   Created creator: {creator.display_name}")
            
            # Sample content
            sample_content = [
                {
                    'creator_id': created_creators[0].creator_id,
                    'title': 'AI-Powered Robotics for Beginners',
                    'description': 'Learn the fundamentals of artificial intelligence and robotics through hands-on projects. Perfect for students aged 12-16 who want to explore the exciting world of AI and autonomous systems.',
                    'content_type': 'project',
                    'categories': ['technology', 'engineering'],
                    'age_groups': ['middle_school', 'high_school'],
                    'difficulty_level': 'beginner',
                    'duration_minutes': 120,
                    'learning_objectives': [
                        'Understand basic AI concepts',
                        'Build a simple robot',
                        'Program autonomous behaviors',
                        'Explore ethical considerations in AI'
                    ],
                    'requirements': [
                        'Arduino or Raspberry Pi kit',
                        'Basic computer literacy',
                        'Adult supervision recommended'
                    ],
                    'tools_needed': [
                        'Computer with internet access',
                        'Arduino IDE or Python',
                        'Robotics kit components'
                    ],
                    'programming_languages': ['python', 'c++'],
                    'robotics_kits': ['arduino', 'raspberry_pi'],
                    'pricing_model': 'paid',
                    'price_usd': 15.99,
                    'token_price': 1599,
                    'tags': ['ai', 'robotics', 'programming', 'beginner', 'hands-on']
                },
                {
                    'creator_id': created_creators[1].creator_id,
                    'title': '3D Printing Workshop: Design to Reality',
                    'description': 'Complete guide to 3D printing from concept to finished product. Students will learn CAD design, printing techniques, and post-processing methods while creating functional objects.',
                    'content_type': 'course',
                    'categories': ['technology', 'engineering', 'arts'],
                    'age_groups': ['high_school', 'adult'],
                    'difficulty_level': 'intermediate',
                    'duration_minutes': 180,
                    'learning_objectives': [
                        'Master CAD design principles',
                        'Understand 3D printing technologies',
                        'Create functional printed objects',
                        'Learn post-processing techniques'
                    ],
                    'requirements': [
                        'Access to 3D printer',
                        'Computer with CAD software',
                        'Basic design understanding'
                    ],
                    'tools_needed': [
                        '3D printer',
                        'CAD software (Fusion 360, Tinkercad)',
                        'Filament materials',
                        'Basic hand tools'
                    ],
                    'pricing_model': 'paid',
                    'price_usd': 29.99,
                    'token_price': 2999,
                    'tags': ['3d-printing', 'cad', 'design', 'engineering', 'maker']
                },
                {
                    'creator_id': created_creators[2].creator_id,
                    'title': 'Math Through Art: Geometric Patterns',
                    'description': 'Explore mathematical concepts through beautiful geometric art. This interdisciplinary lesson combines algebra, geometry, and artistic expression to make math engaging and visual.',
                    'content_type': 'lesson_plan',
                    'categories': ['mathematics', 'arts'],
                    'age_groups': ['elementary', 'middle_school'],
                    'difficulty_level': 'beginner',
                    'duration_minutes': 90,
                    'learning_objectives': [
                        'Identify geometric patterns in art',
                        'Apply mathematical formulas creatively',
                        'Create original geometric artwork',
                        'Connect math to real-world applications'
                    ],
                    'requirements': [
                        'Basic arithmetic skills',
                        'Art supplies (paper, pencils, rulers)',
                        'Optional: computer with drawing software'
                    ],
                    'tools_needed': [
                        'Graph paper',
                        'Compass and ruler',
                        'Colored pencils or markers',
                        'Calculator'
                    ],
                    'pricing_model': 'free',
                    'price_usd': 0.0,
                    'token_price': 0,
                    'tags': ['math', 'art', 'geometry', 'patterns', 'interdisciplinary']
                },
                {
                    'creator_id': created_creators[0].creator_id,
                    'title': 'Climate Change Data Analysis with Python',
                    'description': 'Learn data science while tackling real climate change data. Students will use Python and scientific libraries to analyze temperature trends, visualize data, and draw conclusions about climate patterns.',
                    'content_type': 'project',
                    'categories': ['science', 'technology', 'mathematics'],
                    'age_groups': ['high_school', 'adult'],
                    'difficulty_level': 'advanced',
                    'duration_minutes': 240,
                    'learning_objectives': [
                        'Analyze real climate datasets',
                        'Use Python for data science',
                        'Create compelling data visualizations',
                        'Understand statistical significance'
                    ],
                    'requirements': [
                        'Python programming knowledge',
                        'Basic statistics understanding',
                        'Computer with Python installed'
                    ],
                    'tools_needed': [
                        'Python 3.8+',
                        'Jupyter Notebook',
                        'pandas, matplotlib, numpy libraries',
                        'Internet access for data downloads'
                    ],
                    'programming_languages': ['python'],
                    'pricing_model': 'freemium',
                    'price_usd': 12.99,
                    'token_price': 1299,
                    'tags': ['python', 'data-science', 'climate', 'statistics', 'visualization']
                },
                {
                    'creator_id': created_creators[1].creator_id,
                    'title': 'Solar-Powered Car Challenge',
                    'description': 'Build and race solar-powered cars while learning about renewable energy, engineering design, and physics. Perfect for team-based learning and STEM competitions.',
                    'content_type': 'activity',
                    'categories': ['science', 'engineering', 'technology'],
                    'age_groups': ['middle_school', 'high_school'],
                    'difficulty_level': 'intermediate',
                    'duration_minutes': 150,
                    'learning_objectives': [
                        'Understand solar energy principles',
                        'Apply engineering design process',
                        'Test and iterate designs',
                        'Learn about sustainable technology'
                    ],
                    'requirements': [
                        'Solar car kit or components',
                        'Workshop space',
                        'Team of 2-4 students'
                    ],
                    'tools_needed': [
                        'Solar panels',
                        'Motors and wheels',
                        'Chassis materials',
                        'Basic electronics tools'
                    ],
                    'pricing_model': 'paid',
                    'price_usd': 8.99,
                    'token_price': 899,
                    'tags': ['solar', 'engineering', 'competition', 'renewable-energy', 'hands-on']
                }
            ]
            
            for content_data in sample_content:
                content = marketplace_manager.create_content(content_data)
                print(f"   Created content: {content.title}")
            
            print("✅ Sample data created successfully!")
            
        except Exception as e:
            print(f"❌ Failed to create sample data: {e}")
    
    def check_dependencies(self):
        """Check if required Python packages are installed"""
        print("🔍 Checking dependencies...")
        
        required_packages = [
            'flask', 'flask-cors', 'flask-jwt-extended', 
            'werkzeug', 'sqlite3', 'requests'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                if package == 'sqlite3':
                    import sqlite3
                else:
                    __import__(package.replace('-', '_'))
                print(f"   ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"   ❌ {package} (missing)")
        
        if missing_packages:
            print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', *missing_packages
                ])
                print("✅ Dependencies installed successfully!")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install dependencies: {e}")
                return False
        
        return True
    
    def start_backend_server(self):
        """Start the Flask API server"""
        print("🚀 Starting backend API server...")
        
        try:
            # Change to backend directory
            os.chdir(self.backend_dir)
            
            # Start Flask server
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.backend_dir)
            env['FLASK_ENV'] = 'development'
            
            process = subprocess.Popen([
                sys.executable, 'api_server.py'
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes.append(('backend', process))
            print("✅ Backend server started on http://localhost:5001")
            
            # Give it a moment to start
            time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start backend server: {e}")
            return False
    
    def start_frontend_server(self):
        """Start a simple HTTP server for the frontend"""
        print("🌐 Starting frontend server...")
        
        try:
            # Change to frontend directory
            os.chdir(self.frontend_dir)
            
            # Start simple HTTP server
            process = subprocess.Popen([
                sys.executable, '-m', 'http.server', '8080'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes.append(('frontend', process))
            print("✅ Frontend server started on http://localhost:8080")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start frontend server: {e}")
            return False
    
    def wait_for_servers(self):
        """Wait for servers to be ready"""
        print("⏳ Waiting for servers to be ready...")
        
        import requests
        
        # Wait for backend
        backend_ready = False
        for _ in range(30):  # 30 second timeout
            try:
                response = requests.get('http://localhost:5001/api/health', timeout=1)
                if response.status_code == 200:
                    backend_ready = True
                    break
            except requests.RequestException:
                pass
            time.sleep(1)
        
        if backend_ready:
            print("✅ Backend server is ready!")
        else:
            print("⚠️  Backend server may not be fully ready")
        
        # Wait for frontend
        frontend_ready = False
        for _ in range(10):  # 10 second timeout
            try:
                response = requests.get('http://localhost:8080', timeout=1)
                if response.status_code == 200:
                    frontend_ready = True
                    break
            except requests.RequestException:
                pass
            time.sleep(1)
        
        if frontend_ready:
            print("✅ Frontend server is ready!")
        else:
            print("⚠️  Frontend server may not be fully ready")
        
        return backend_ready and frontend_ready
    
    def open_browser(self):
        """Open the application in the default web browser"""
        try:
            import webbrowser
            webbrowser.open('http://localhost:8080')
            print("🌐 Opened application in browser: http://localhost:8080")
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
            print("💡 Please manually open: http://localhost:8080")
    
    def monitor_processes(self):
        """Monitor running processes and restart if needed"""
        while self.running:
            for name, process in self.processes[:]:  # Copy list to avoid modification during iteration
                if process.poll() is not None:  # Process has terminated
                    print(f"⚠️  {name} server has stopped unexpectedly")
                    self.processes.remove((name, process))
                    
                    # Attempt to restart
                    if name == 'backend':
                        print("🔄 Restarting backend server...")
                        self.start_backend_server()
                    elif name == 'frontend':
                        print("🔄 Restarting frontend server...")
                        self.start_frontend_server()
            
            time.sleep(5)  # Check every 5 seconds
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}, shutting down...")
        self.shutdown()
    
    def shutdown(self):
        """Gracefully shutdown all processes"""
        print("🛑 Shutting down STEAM Marketplace...")
        
        self.running = False
        
        # Terminate all processes
        for name, process in self.processes:
            print(f"   Stopping {name} server...")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"   Force killing {name} server...")
                process.kill()
            except Exception as e:
                print(f"   Error stopping {name} server: {e}")
        
        print("✅ STEAM Marketplace shut down successfully!")
        sys.exit(0)
    
    def print_status(self):
        """Print application status and access information"""
        print("\n" + "="*60)
        print("🎓 STEAM MARKETPLACE - GLOBAL EDUCATIONAL HUB 🌍")
        print("="*60)
        print("\n📊 Application Status:")
        print("   ✅ Database: Ready")
        print("   ✅ Backend API: http://localhost:5001")
        print("   ✅ Frontend App: http://localhost:8080")
        print("\n🌟 Features Available:")
        print("   • Browse and search educational content")
        print("   • Create and share lesson plans & projects") 
        print("   • Purchase content with tokens or cash")
        print("   • Global marketplace for educators")
        print("   • STEAM interdisciplinary learning")
        print("\n💡 Quick Start:")
        print("   1. Visit: http://localhost:8080")
        print("   2. Create an account (get 100 free tokens!)")
        print("   3. Explore trending content")
        print("   4. Share your own educational materials")
        print("\n🔧 Management:")
        print("   • Press Ctrl+C to shutdown")
        print("   • Check logs above for any issues")
        print("   • Backend API docs: http://localhost:5001/api/health")
        print("\n" + "="*60)
    
    def run(self):
        """Main application runner"""
        print("🎓 STEAM Marketplace Launcher")
        print("=" * 50)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Initialize database
        if not self.initialize_database():
            return False
        
        # Start servers
        if not self.start_backend_server():
            return False
        
        if not self.start_frontend_server():
            return False
        
        # Wait for servers to be ready
        if not self.wait_for_servers():
            print("⚠️  Some servers may not be fully ready, but continuing...")
        
        # Print status
        self.print_status()
        
        # Open browser
        self.open_browser()
        
        # Start monitoring
        self.running = True
        monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
        monitor_thread.start()
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()
        
        return True

def main():
    """Main entry point"""
    launcher = MarketplaceLauncher()
    try:
        success = launcher.run()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Launcher failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())