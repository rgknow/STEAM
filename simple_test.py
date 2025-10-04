#!/usr/bin/env python3
"""
Simple Water Guardians Project Test
==================================

Tests the Water Guardians project JSON file directly.
"""

import json
import os

def test_water_guardians_project():
    """Test the Water Guardians project file."""
    
    print("🌱 Water Guardians Project File Test")
    print("=" * 40)
    
    project_file = "/workspaces/STEAM/projects/water_guardians_irrigation.json"
    
    try:
        # Check if file exists
        if not os.path.exists(project_file):
            print(f"❌ Project file not found: {project_file}")
            return False
        
        print(f"✅ Project file found: {project_file}")
        
        # Load and parse JSON
        with open(project_file, 'r') as f:
            project = json.load(f)
        
        print(f"✅ JSON loaded successfully")
        
        # Test key components
        print(f"\n📊 Project Overview:")
        meta = project['project_meta']
        print(f"  Title: {meta['title']}")
        print(f"  Grade Band: {meta['grade_band']}")
        print(f"  Duration: {meta['duration']}")
        print(f"  Theme: {meta['theme']}")
        print(f"  Driving Question: {meta['driving_question'][:80]}...")
        
        # Test lessons
        lessons = project['lesson_sequence']
        print(f"\n📚 Lessons ({len(lessons)} total):")
        for i, lesson in enumerate(lessons[:3], 1):  # Show first 3
            print(f"  {i}. {lesson['title']}")
            print(f"     Duration: {lesson['duration_minutes']} minutes")
            print(f"     Objectives: {len(lesson['objectives'])} goals")
        
        if len(lessons) > 3:
            print(f"  ... and {len(lessons) - 3} more lessons")
        
        # Test robotics integration
        robotics = project['robotics_integration']
        print(f"\n🤖 Robotics Integration:")
        print(f"  Platform: {robotics['primary_kit']}")
        print(f"  Required Modules: {len(robotics['required_modules'])} items")
        for module in robotics['required_modules'][:3]:
            print(f"  - {module['component']}: {module['purpose']}")
        
        # Test coding components
        coding = project['coding_components']
        print(f"\n💻 Coding Components ({len(coding)} components):")
        for component_name, component_details in coding.items():
            if isinstance(component_details, dict) and 'learning_objectives' in component_details:
                print(f"  {component_name}: {len(component_details['learning_objectives'])} objectives")
        
        # Test standards alignment
        standards = project['standards_alignment']
        print(f"\n📋 Educational Standards:")
        for framework, items in standards.items():
            print(f"  {framework}: {len(items)} standards")
        
        # Test assessment framework
        assessment = project['assessment_framework']
        print(f"\n🎯 Assessment Framework:")
        print(f"  Diagnostic Assessment: {'pre_assessment' in assessment.get('diagnostic_assessment', {})}")
        print(f"  Formative Assessments: {len(assessment.get('formative_assessments', []))} checkpoints")
        print(f"  Summative Assessments: {'summative_assessments' in assessment}")
        
        print(f"\n✅ Water Guardians project structure is complete and valid!")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return False
    except KeyError as e:
        print(f"❌ Missing required field: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_dashboard_integration():
    """Test dashboard files are present."""
    
    print("\n💻 Dashboard Integration Test")
    print("=" * 30)
    
    dashboard_files = [
        "/workspaces/STEAM/dashboard/index.html",
        "/workspaces/STEAM/dashboard/script.js",
        "/workspaces/STEAM/dashboard/styles.css"
    ]
    
    all_present = True
    for file_path in dashboard_files:
        if os.path.exists(file_path):
            print(f"✅ {os.path.basename(file_path)} found")
        else:
            print(f"❌ {os.path.basename(file_path)} missing")
            all_present = False
    
    if all_present:
        print("✅ All dashboard files present")
    
    return all_present

def show_next_steps():
    """Show next steps for using the system."""
    
    print("\n🚀 Next Steps:")
    print("=" * 15)
    print("1. 🌐 Open dashboard: http://localhost:8080")
    print("2. 💬 Test chat with 'Water Guardians'")
    print("3. 🤖 Try 'robotics' to see featured projects")
    print("4. 📚 Say 'Lesson 1' for step-by-step guidance")
    print("5. 🔧 Try 'Ready for sensors' for technical setup")
    
    print("\n🎯 Water Guardians Features:")
    print("- 8 comprehensive lessons")
    print("- Luxrobo MODI + ESP32 integration")
    print("- Scratch + Python programming")
    print("- Real-world environmental impact")
    print("- Multi-framework standards alignment")
    print("- Portfolio-based assessment")

if __name__ == "__main__":
    print("🔍 Testing Water Guardians Integration...")
    
    project_ok = test_water_guardians_project()
    dashboard_ok = test_dashboard_integration()
    
    if project_ok and dashboard_ok:
        print("\n🎉 All tests passed! Water Guardians is ready to use!")
        show_next_steps()
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
    
    print("\n🌱 Transform STEAM education with Water Guardians! 🌱")