// Dashboard JavaScript - Making STEAM Learning Interactive
class STEAMDashboard {
    constructor() {
        this.currentUser = {
            name: 'Alex Student',
            level: 5,
            streak: 7,
            completedProjects: 15,
            learningStyle: 'visual',
            multipleIntelligences: ['logical-mathematical', 'spatial', 'linguistic']
        };
        
        this.chatHistory = [];
        this.availableTools = [
            'project-generator',
            'robotics-lab',
            'code-playground',
            'lesson-planner',
            'assessment-center',
            'resource-library'
        ];
        
        this.educationalFrameworks = {
            'NGSS': 'Next Generation Science Standards',
            'ISTE': 'International Society for Technology in Education',
            'OECD': 'OECD Education 2030',
            'DIGICOMP': 'European Digital Competence Framework',
            'NCF': 'National Curriculum Framework 2023',
            'PBL': 'Project-Based Learning',
            'MI': 'Multiple Intelligence Theory'
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadUserData();
        this.initializeChat();
        this.loadLearningPaths();
        this.startEngagementTracking();
    }
    
    setupEventListeners() {
        // Chat functionality
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendBtn');
        
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        sendBtn.addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Quick actions
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleQuickAction(action);
            });
        });
        
        // Tool cards
        document.querySelectorAll('.tool-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const tool = e.currentTarget.dataset.tool;
                this.launchTool(tool);
            });
        });
        
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleNavigation(e.currentTarget.getAttribute('href'));
            });
        });
        
        // Modal handling
        this.setupModalHandlers();
        
        // Help button
        document.getElementById('helpBtn').addEventListener('click', () => {
            this.showHelpModal();
        });
        
        // Project creation
        document.querySelector('.btn-primary').addEventListener('click', () => {
            this.showProjectModal();
        });
    }
    
    async sendMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Add user message to chat
        this.addMessageToChat('user', message);
        input.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Process message with AI
        try {
            const response = await this.processMessageWithAI(message);
            this.removeTypingIndicator();
            this.addMessageToChat('assistant', response);
        } catch (error) {
            this.removeTypingIndicator();
            this.addMessageToChat('assistant', 'I\'m having trouble connecting right now. Let me help you with some quick suggestions instead!');
            this.showQuickSuggestions();
        }
    }
    
    async processMessageWithAI(message) {
        // Simulate AI processing with educational context
        await this.delay(1500);
        
        const lowerMessage = message.toLowerCase();
        
        // Intent recognition based on educational keywords
        if (lowerMessage.includes('water guardians') || lowerMessage.includes('water guardian')) {
            return this.generateWaterGuardiansResponse(message);
        } else if (lowerMessage.includes('lesson 1') || lowerMessage.includes('start lesson')) {
            return this.generateLessonStartResponse(message);
        } else if (lowerMessage.includes('ready for sensors') || lowerMessage.includes('sensor setup')) {
            return this.generateSensorSetupResponse(message);
        } else if (lowerMessage.includes('project') || lowerMessage.includes('create')) {
            return this.generateProjectResponse(message);
        } else if (lowerMessage.includes('robot') || lowerMessage.includes('modi')) {
            return this.generateRoboticsResponse(message);
        } else if (lowerMessage.includes('code') || lowerMessage.includes('python')) {
            return this.generateCodingResponse(message);
        } else if (lowerMessage.includes('learn') || lowerMessage.includes('study')) {
            return this.generateLearningResponse(message);
        } else if (lowerMessage.includes('help') || lowerMessage.includes('stuck')) {
            return this.generateHelpResponse(message);
        } else {
            return this.generateGeneralResponse(message);
        }
    }
    
    generateProjectResponse(message) {
        const themes = [
            'Environmental Sustainability',
            'Space Exploration',
            'Smart Cities',
            'Renewable Energy',
            'Ocean Conservation',
            'Biotechnology Innovation'
        ];
        
        const randomTheme = themes[Math.floor(Math.random() * themes.length)];
        
        return `Great! I can help you create an exciting STEAM project. Based on your learning style and current level, I suggest a **${randomTheme}** project.

This project would integrate:
🔬 **Science**: Real-world research and hypothesis testing
⚙️ **Technology**: Data collection and analysis tools
🛠️ **Engineering**: Design thinking and prototyping
🎨 **Arts**: Creative presentation and visualization
📊 **Mathematics**: Statistical analysis and modeling

**Aligned Frameworks**: NGSS, ISTE, PBL

Would you like me to generate a detailed project plan with specific learning outcomes and robotics components?`;
    }
    
    generateRoboticsResponse(message) {
        return `Awesome! Let's dive into robotics with the Luxrobo Modi kit! 🤖

**Current Modi Kit Components Available**:
- Network Module (WiFi/Bluetooth connectivity)
- Environment Module (temperature, humidity, light sensors)
- Input Modules (button, dial, joystick)
- Output Modules (speaker, display, LED)
- Motor Module (for movement and actuation)

**Suggested Projects for Your Level**:
1. **Water Guardians: Smart Irrigation System** - Build an automated system that conserves water while keeping plants healthy (Featured Project!)
2. **Smart Environmental Monitor** - Build a system that tracks air quality
3. **Autonomous Navigation Robot** - Create a robot that can navigate obstacles
4. **Interactive Art Installation** - Combine sensors with creative expression

**Learning Integration**:
- Python programming for module control
- Physics concepts (sensors, motors, signals)
- Mathematics (data analysis, algorithms)
- Engineering design process

        Which robotics project interests you most? I can provide step-by-step guidance!

**🌱 Special Feature: Water Guardians Project**
Our newest interdisciplinary project combines:
- Soil moisture sensing with calibration
- Scratch simulation for logic modeling  
- Python programming for real-time control
- Environmental science and conservation ethics
- 8 comprehensive lessons with full robotics integration

Say "Water Guardians" to learn more about this featured project!`;
    }
    
    generateWaterGuardiansResponse(message) {
        return `🌱 **Welcome to Water Guardians: Smart Irrigation System!** 

This is our flagship interdisciplinary project that tackles real-world water conservation through smart technology. Perfect for combining STEAM learning with environmental responsibility!

**🎯 Project Overview**:
- **Duration**: 8 comprehensive lessons (6-8 weeks)
- **Grade Levels**: Adaptable for Middle School through High School
- **Real-World Impact**: Build functioning smart irrigation systems

**🔧 What You'll Build**:
- Soil moisture monitoring system using calibrated sensors
- Automated watering mechanism with precise control
- Data logging and analysis dashboard
- Environmental impact assessment tools

**💻 Technical Skills You'll Learn**:
- **Scratch Programming**: Logic simulation and system modeling
- **Python Coding**: Real-time sensor control and data analysis
- **Electronics**: Luxrobo MODI + ESP32 integration
- **Data Science**: Moisture calibration and predictive modeling

**🌍 STEAM Integration**:
- **Science**: Plant biology, soil science, water cycle
- **Technology**: IoT sensors, automation systems
- **Engineering**: System design, calibration protocols
- **Arts**: User interface design, data visualizations
- **Mathematics**: Statistical analysis, optimization algorithms

**📚 Educational Standards Covered**:
- NGSS: Engineering Design, Earth Systems
- ISTE: Computational Thinking, Digital Citizenship
- UNESCO: Sustainability Education
- And many more international frameworks!

**🎓 Assessment & Differentiation**:
- Portfolio-based authentic assessment
- Peer collaboration and review
- Multiple learning modalities supported
- Extensions for advanced learners

Ready to start your Water Guardians journey? I can guide you through:
1. **Lesson 1**: Project introduction and system planning
2. **Hardware Setup**: Connecting your MODI kit and sensors
3. **Coding Basics**: Starting with Scratch simulations
4. **Real Implementation**: Moving to Python control systems

Which aspect interests you most? Let's dive in! 🚀`;
    }
    
    generateLessonStartResponse(message) {
        return `🎯 **Water Guardians - Lesson 1: Introduction & System Planning**

Welcome to your first lesson! Let's start by understanding the challenge and planning our smart irrigation solution.

**🌟 Today's Learning Objectives**:
- Understand global water scarcity challenges
- Analyze traditional vs. smart irrigation methods
- Design initial system architecture
- Set up project portfolio and collaboration tools

**🔍 Opening Challenge**:
*"Did you know that agriculture uses 70% of global freshwater, but up to 60% is wasted through inefficient irrigation?"*

Let's explore how we can be part of the solution!

**📝 Activity Sequence**:

**1. Problem Investigation (15 minutes)**
- Watch: "Water Crisis Around the World" video
- Discussion: How does water scarcity affect your local community?
- Research: Find 3 examples of water conservation success stories

**2. System Design Thinking (20 minutes)**
- Brainstorm: What makes irrigation "smart"?
- Sketch: Your initial system design ideas
- Consider: What sensors and controls do we need?

**3. Technical Planning (15 minutes)**
- Introduction to your MODI kit components
- Plan: Which modules will handle what functions?
- Timeline: Map out our 8-lesson journey

**4. Portfolio Setup (10 minutes)**
- Create your digital portfolio
- Set learning goals and success criteria
- Establish collaboration partnerships

**🎨 Creative Extension**:
Design a logo for your Water Guardians team and create a mission statement for your project!

**🏠 Connection to Home**:
- Observe irrigation methods in your neighborhood
- Measure water usage in your garden (if available)
- Interview family about water conservation practices

**Next Steps**: After completing these activities, say "Ready for sensors" to learn about the technical components we'll use!

Ready to become a Water Guardian? Let's start saving the world, one drop at a time! 💧🌱`;
    }
    
    generateSensorSetupResponse(message) {
        return `🔧 **Water Guardians - Lesson 2: Sensor Technology & Calibration**

Excellent! Now let's dive into the technical heart of our system - understanding and setting up our sensors.

**🎯 Today's Learning Objectives**:
- Understand different types of moisture sensors
- Learn calibration principles and importance
- Set up MODI Environment Module
- Create accurate measurement protocols

**🔬 The Science Behind Soil Sensors**:

**1. Capacitive vs. Resistive Sensors**
- **Capacitive** (like MODI): Measures dielectric constant changes
- **Resistive**: Measures electrical resistance through soil
- Why capacitive is better for long-term projects

**2. Calibration Science**
- *Dry Point*: Sensor in completely dry conditions
- *Wet Point*: Sensor in water-saturated soil
- *Field Capacity*: Optimal moisture for plant growth

**🛠️ Hands-On Setup**:

**Step 1: MODI Kit Assembly (10 minutes)**
\`\`\`
Components needed:
- Network Module (WiFi/Bluetooth)
- Environment Module (moisture, temperature, light)
- Display Module (for readings)
- Battery Module (power)
\`\`\`

**Step 2: Physical Calibration (15 minutes)**
1. **Dry Calibration**: Place sensor in completely dry soil
   - Record baseline reading
   - This becomes your 0% moisture reference

2. **Wet Calibration**: Saturate soil with water
   - Record maximum reading
   - This becomes your 100% moisture reference

**Step 3: Test Garden Setup (20 minutes)**
- Create test containers with different moisture levels
- 25%, 50%, 75% moisture targets
- Verify sensor accuracy across the range

**💻 Programming Introduction**:

**Scratch Simulation First**:
\`\`\`scratch-blocks
When [green flag] clicked
Set [moisture-reading] to (environment sensor value)
Set [moisture-percent] to (((moisture-reading - dry-value) / (wet-value - dry-value)) * 100)
If <moisture-percent < 30> then
  Say [Plant needs water!] for 2 seconds
End
\`\`\`

**🧮 The Math Behind Calibration**:
*Moisture % = ((Current Reading - Dry Reading) / (Wet Reading - Dry Reading)) × 100*

**🌱 Plant Science Connection**:
- Different plants need different moisture levels
- Overwatering can be as harmful as underwatering
- Root zone vs surface moisture differences

**📊 Data Collection Protocol**:
1. Take readings every 30 seconds
2. Record in your project portfolio
3. Note environmental conditions (temperature, humidity)
4. Create graphs to visualize patterns

**🎨 Extension Activities**:
- Research moisture needs of different plant species
- Design a moisture level indicator system
- Create data visualization dashboard

**Next Steps**: Once you've completed calibration, say "Ready for Python" to move into automated control programming!

Great work setting up the sensing foundation of your Water Guardian system! 📊🌿`;
    }
    
    generateCodingResponse(message) {
        return `Perfect! Let's enhance your Python skills with STEAM-focused coding! 💻

**Coding Challenges Based on Your Level**:

**🔬 Science Data Analysis**:
- Analyze weather patterns using real data
- Create visualizations of scientific phenomena
- Build simulation models

**🤖 Robotics Programming**:
- Control Modi modules with Python
- Implement sensor data processing
- Create autonomous behavior algorithms

**📊 Mathematical Modeling**:
- Solve engineering problems with code
- Create interactive mathematical visualizations
- Build calculators for physics formulas

**🎨 Creative Coding**:
- Generate artistic patterns with algorithms
- Create interactive STEAM presentations
- Build educational games

**Current Recommendation**: Since you excel in logical-mathematical intelligence, let's start with a data analysis project that combines your interests!

What specific coding challenge would you like to tackle?`;
    }
    
    generateLearningResponse(message) {
        return `I love your enthusiasm for learning! Based on your profile and learning style, here's your personalized learning path: 📚

**Your Learning Profile**:
- Visual learner with strong spatial intelligence
- Level 5 STEAM Explorer
- Strengths in logical-mathematical reasoning

**Recommended Learning Sequence**:

1. **Current Focus**: Interdisciplinary problem-solving
2. **Next Challenge**: Advanced robotics integration
3. **Stretch Goal**: Independent research project

**Learning Frameworks Integration**:
- **NGSS**: Science and engineering practices
- **ISTE**: Digital citizenship and computational thinking
- **OECD**: Critical thinking and creativity
- **Multiple Intelligence**: Leveraging your logical-mathematical and spatial strengths

**Personalized Features**:
- Visual diagrams and interactive simulations
- Hands-on building and testing
- Step-by-step guided discovery
- Opportunities for creative expression

**Today's Learning Goal**: Complete one interdisciplinary challenge that combines at least 3 STEAM elements.

What subject area excites you most right now?`;
    }
    
    generateHelpResponse(message) {
        return `Don't worry! Everyone needs help sometimes - that's how we learn and grow! 🌟

**I'm here to support you with**:

🎯 **Immediate Help**:
- Break down complex problems into smaller steps
- Provide visual explanations and examples
- Connect you with appropriate resources
- Suggest alternative approaches

🤝 **Learning Support**:
- Identify your learning style preferences
- Adapt content to your cognitive level
- Provide scaffolded challenges
- Encourage metacognitive reflection

🚀 **Motivation Boost**:
- Celebrate your progress and efforts
- Connect current challenges to your interests
- Show real-world applications
- Provide achievable next steps

**Available Support Tools**:
- Interactive tutorials
- Peer collaboration opportunities
- Expert agent consultations
- Resource library access

**Remember**: Every expert was once a beginner! Your questions show you're thinking critically and engaging deeply with the material.

What specific area would you like help with? I can provide targeted guidance!`;
    }
    
    generateGeneralResponse(message) {
        return `Thanks for sharing that with me! I'm your STEAM learning companion, designed to make your educational journey engaging and personalized. 

**How I can help you today**:
- 🎨 Create interdisciplinary projects combining Science, Technology, Engineering, Arts, and Mathematics
- 🤖 Guide you through robotics experiments with the Modi kit
- 💻 Develop Python coding skills through STEAM applications
- 📊 Generate personalized lesson plans based on your learning style
- 🌟 Provide challenges that stretch your abilities while building confidence

**Your Learning Journey**:
I adapt to your visual learning style and leverage your logical-mathematical intelligence to create the most effective learning experiences.

What aspect of STEAM learning interests you most right now? I can help you dive deeper!`;
    }
    
    addMessageToChat(sender, content) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message fade-in`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = this.formatMessage(content);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Store in chat history
        this.chatHistory.push({ sender, content, timestamp: new Date() });
    }
    
    formatMessage(content) {
        // Convert markdown-like formatting to HTML
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }
    
    showTypingIndicator() {
        const messagesContainer = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant-message typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                Thinking...
            </div>
        `;
        
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    removeTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    handleQuickAction(action) {
        const actionMessages = {
            'project': 'I want to create a new STEAM project that combines multiple disciplines.',
            'robotics': 'Let\'s build something with the Modi robotics kit!',
            'coding': 'I\'d like to work on a Python coding challenge.',
            'lesson': 'Can you create a lesson plan for me?'
        };
        
        const message = actionMessages[action];
        if (message) {
            document.getElementById('chatInput').value = message;
            this.sendMessage();
        }
    }
    
    launchTool(toolName) {
        // Add loading state
        const toolCard = document.querySelector(`[data-tool="${toolName}"]`);
        const originalContent = toolCard.innerHTML;
        
        toolCard.classList.add('loading');
        toolCard.querySelector('.tool-btn').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        
        // Simulate tool loading
        setTimeout(() => {
            this.openToolInterface(toolName);
            toolCard.classList.remove('loading');
            toolCard.innerHTML = originalContent;
        }, 1500);
    }
    
    openToolInterface(toolName) {
        const toolInterfaces = {
            'project-generator': () => this.showProjectGeneratorModal(),
            'robotics-lab': () => this.showRoboticsLabModal(),
            'code-playground': () => this.showCodePlaygroundModal(),
            'lesson-planner': () => this.showLessonPlannerModal(),
            'assessment-center': () => this.showAssessmentCenterModal(),
            'resource-library': () => this.showResourceLibraryModal()
        };
        
        const interfaceFunction = toolInterfaces[toolName];
        if (interfaceFunction) {
            interfaceFunction();
        }
    }
    
    showProjectGeneratorModal() {
        this.addMessageToChat('assistant', `🎯 **Project Generator Activated!**

Let me create a personalized STEAM project for you. I'll consider:
- Your visual learning style
- Your logical-mathematical intelligence strengths
- Your current Level 5 capabilities
- Available Modi robotics components
- Alignment with educational frameworks

**Generating Project**: "Smart Environmental Monitoring System"

**Project Overview**:
Design and build an intelligent system that monitors environmental conditions and provides actionable insights for sustainability.

**STEAM Integration**:
🔬 **Science**: Environmental science, data collection, hypothesis testing
⚙️ **Technology**: IoT sensors, data visualization, cloud storage
🛠️ **Engineering**: System design, problem-solving, optimization
🎨 **Arts**: Interactive dashboard design, data storytelling
📊 **Mathematics**: Statistical analysis, trend modeling, algorithms

**Learning Outcomes** (Aligned with NGSS, ISTE, OECD):
1. Understand environmental systems and their interconnections
2. Apply engineering design process to solve real-world problems
3. Use technology tools for data collection and analysis
4. Communicate findings through multiple media formats
5. Develop computational thinking and programming skills

**Modi Kit Components Needed**:
- Environment Module (temperature, humidity, light sensors)
- Network Module (WiFi connectivity for data transmission)
- Display Module (real-time data visualization)

**Python Programming Elements**:
- Sensor data acquisition and processing
- Data visualization with libraries like matplotlib
- Basic machine learning for pattern recognition

**Timeline**: 2-3 weeks with daily 1-hour sessions
**Difficulty**: Intermediate (perfect for your Level 5 status)

Ready to start building? I can provide step-by-step guidance!`);
    }
    
    showRoboticsLabModal() {
        this.addMessageToChat('assistant', `🤖 **Welcome to the Virtual Robotics Lab!**

Your Modi Kit components are ready for action! Let's build something amazing.

**Available Modi Modules**:
✅ Network Module - WiFi/Bluetooth connectivity
✅ Environment Module - Temperature, humidity, light sensors
✅ Input Modules - Button, dial, joystick for user interaction
✅ Output Modules - Speaker, display, LED for feedback
✅ Motor Module - Movement and mechanical actuation
✅ Gyro Module - Orientation and motion sensing

**Suggested Build for Today**: Autonomous Pet Robot

**What it does**:
- Follows you around using sensors
- Responds to environmental changes
- Displays emotions through LED patterns
- Makes sounds based on interactions
- Learns and adapts behavior over time

**Python Code Structure**:
\`\`\`python
import modi

# Initialize modules
network_module = modi.Network()
env_module = modi.Environment()
motor_module = modi.Motor()
led_module = modi.Led()

# Pet behavior logic
def pet_follow_behavior():
    light_level = env_module.light
    if light_level < 50:  # Dark environment
        led_module.set_color(255, 0, 0)  # Red - cautious
        motor_module.set_speed(30)  # Slow movement
    else:
        led_module.set_color(0, 255, 0)  # Green - happy
        motor_module.set_speed(60)  # Normal movement
\`\`\`

**Learning Objectives**:
- Sensor integration and data processing
- Conditional logic and decision-making algorithms
- Real-time system programming
- Human-robot interaction principles

Ready to start building your robotic companion?`);
    }
    
    showCodePlaygroundModal() {
        this.addMessageToChat('assistant', `💻 **Python Code Playground Activated!**

Let's write some Python code with a STEAM twist! Here's your personalized coding challenge:

**Challenge**: Climate Data Analyzer

**Your Mission**: 
Create a Python program that analyzes climate data and visualizes trends to help understand environmental changes.

**Starter Code**:
\`\`\`python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Sample climate data
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
temp_data_2023 = [2, 4, 8, 14, 19, 24, 27, 26, 22, 16, 9, 4]
temp_data_2024 = [3, 5, 9, 15, 20, 25, 29, 28, 23, 17, 10, 5]

# Your challenge: Complete these functions!

def calculate_average_temp(temperatures):
    # TODO: Calculate and return average temperature
    pass

def find_temperature_trend(temp1, temp2):
    # TODO: Compare two years and return trend analysis
    pass

def create_visualization(months, temp1, temp2):
    # TODO: Create a compelling chart showing temperature comparison
    pass

def predict_next_year(temp_data):
    # TODO: Use simple linear regression to predict next year
    pass

# Test your functions
avg_2023 = calculate_average_temp(temp_data_2023)
avg_2024 = calculate_average_temp(temp_data_2024)
trend = find_temperature_trend(temp_data_2023, temp_data_2024)

print(f"Average 2023: {avg_2023}°C")
print(f"Average 2024: {avg_2024}°C")
print(f"Trend: {trend}")
\`\`\`

**Learning Goals**:
- Data manipulation with lists and arrays
- Mathematical operations and statistics
- Data visualization principles
- Basic predictive modeling

**Extensions for Advanced Learners**:
- Connect to real weather APIs
- Add interactive controls
- Export results to reports
- Integrate with Modi sensors for live data

**Hints for Your Visual Learning Style**:
- Use colorful charts and graphs
- Create step-by-step visual breakdowns
- Build interactive elements you can see change

Ready to code? I'll guide you through each step!`);
    }
    
    setupModalHandlers() {
        // Generic modal close functionality
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay') || 
                e.target.classList.contains('modal-close')) {
                this.closeAllModals();
            }
        });
        
        // Escape key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }
    
    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
        document.getElementById('modalOverlay').style.display = 'none';
    }
    
    showProjectModal() {
        document.getElementById('modalOverlay').style.display = 'block';
        document.getElementById('projectModal').style.display = 'block';
    }
    
    loadUserData() {
        // Simulate loading user data and updating stats
        this.updateStats();
        this.personalizeInterface();
    }
    
    updateStats() {
        // Animate stat counters
        this.animateCounter('.stat-number', [15, 7, 5]);
    }
    
    animateCounter(selector, values) {
        const elements = document.querySelectorAll(selector);
        elements.forEach((el, index) => {
            const finalValue = values[index];
            let currentValue = 0;
            const increment = finalValue / 30;
            
            const timer = setInterval(() => {
                currentValue += increment;
                if (currentValue >= finalValue) {
                    currentValue = finalValue;
                    clearInterval(timer);
                }
                el.textContent = Math.floor(currentValue);
            }, 50);
        });
    }
    
    personalizeInterface() {
        // Personalize based on user's learning style and intelligence profile
        const visualLearnerElements = document.querySelectorAll('.tool-card, .path-card');
        visualLearnerElements.forEach(el => {
            el.style.borderLeft = '4px solid #667eea';
        });
        
        // Add visual indicators for recommended content
        this.highlightRecommendedContent();
    }
    
    highlightRecommendedContent() {
        // Add visual cues for content matching user's profile
        const recommendedCards = document.querySelectorAll('[data-recommended="true"]');
        recommendedCards.forEach(card => {
            const badge = document.createElement('div');
            badge.className = 'recommended-badge';
            badge.innerHTML = '<i class="fas fa-star"></i> Recommended for You';
            card.appendChild(badge);
        });
    }
    
    initializeChat() {
        // Add initial welcome message with personalization
        setTimeout(() => {
            this.addMessageToChat('assistant', 
                `Welcome back, ${this.currentUser.name}! 🌟 

I've prepared some exciting learning opportunities based on your profile:
- **Learning Style**: Visual learner
- **Strengths**: Logical-mathematical and spatial intelligence
- **Current Level**: ${this.currentUser.level} (STEAM Explorer)

**Today's Personalized Recommendations**:
1. Complete your "Water Sustainability Challenge" (65% done!)
2. Try the new Climate Data Analyzer coding challenge
3. Build an autonomous robot with your Modi kit

**Engagement Goal**: Let's maintain your ${this.currentUser.streak}-day learning streak! 🔥

What would you like to explore first?`);
        }, 1000);
    }
    
    loadLearningPaths() {
        // Add dynamic content loading for learning paths
        const pathsGrid = document.querySelector('.paths-grid');
        
        // Add recommended paths based on user profile
        this.addRecommendedPaths();
        
        // Setup path interactions
        document.querySelectorAll('.path-card').forEach(card => {
            card.addEventListener('click', () => {
                this.handlePathSelection(card);
            });
        });
    }
    
    addRecommendedPaths() {
        // Dynamically add paths based on user's learning profile
        const recommendedPaths = this.generateRecommendedPaths();
        // Implementation would add these to the DOM
    }
    
    generateRecommendedPaths() {
        return [
            {
                title: 'AI and Machine Learning Fundamentals',
                description: 'Explore artificial intelligence through hands-on Python projects.',
                frameworks: ['ISTE', 'OECD', 'DIGICOMP'],
                difficulty: 'intermediate',
                estimatedTime: '4 weeks'
            },
            {
                title: 'Sustainable Engineering Solutions',
                description: 'Design eco-friendly solutions using engineering principles.',
                frameworks: ['NGSS', 'NCF', 'PBL'],
                difficulty: 'advanced',
                estimatedTime: '6 weeks'
            }
        ];
    }
    
    handlePathSelection(pathCard) {
        const pathTitle = pathCard.querySelector('.path-title').textContent;
        const isCompleted = pathCard.querySelector('.status-badge').textContent === 'Completed';
        
        if (isCompleted) {
            this.showPathResults(pathTitle);
        } else {
            this.startPath(pathTitle);
        }
    }
    
    startPath(pathTitle) {
        this.addMessageToChat('assistant', 
            `🚀 **Starting Learning Path: ${pathTitle}**

I'm setting up your personalized learning experience:

**Customizations for You**:
- Visual learning materials and interactive diagrams
- Logical step-by-step progressions
- Hands-on activities with immediate feedback
- Integration with Modi robotics components
- Python coding challenges throughout

**Learning Framework Alignment**:
- NGSS science and engineering practices
- ISTE digital citizenship and computational thinking
- PBL authentic, real-world problem solving

**Your Learning Path Structure**:
1. **Explore** - Interactive introduction and context setting
2. **Investigate** - Guided research and data collection
3. **Create** - Design and build solutions
4. **Test** - Iterative improvement and validation
5. **Share** - Present and reflect on learning

**First Activity**: Complete the pre-assessment to customize your experience further.

Ready to begin? I'll guide you through each step! 🌟`);
    }
    
    startEngagementTracking() {
        // Track user engagement and provide motivational feedback
        setInterval(() => {
            this.checkEngagementLevel();
        }, 300000); // Check every 5 minutes
        
        // Track learning session time
        this.sessionStartTime = new Date();
        
        // Provide periodic encouragement
        this.scheduleEncouragement();
    }
    
    checkEngagementLevel() {
        const sessionTime = (new Date() - this.sessionStartTime) / 1000 / 60; // minutes
        
        if (sessionTime > 30 && !this.hasShownBreakReminder) {
            this.showBreakReminder();
            this.hasShownBreakReminder = true;
        }
        
        if (sessionTime > 60 && !this.hasShownProgressCelebration) {
            this.showProgressCelebration();
            this.hasShownProgressCelebration = true;
        }
    }
    
    showBreakReminder() {
        this.addMessageToChat('assistant', 
            `⏰ **Learning Break Reminder**

You've been actively learning for 30 minutes - fantastic dedication! 

**Cognitive Science Tip**: Taking short breaks actually improves learning retention and creativity. 

**Suggested 5-minute break activities**:
- 🚶 Take a short walk
- 💧 Drink some water
- 👀 Look at something far away (rest your eyes)
- 🧘 Do some deep breathing

Your progress is automatically saved. When you're ready, I'll be here to continue your STEAM journey! 

**Today's Achievement**: 30+ minutes of focused learning 🎉`);
    }
    
    showProgressCelebration() {
        this.addMessageToChat('assistant', 
            `🎉 **Outstanding Learning Session!**

You've been engaged for over an hour - that's exceptional dedication to your STEAM education!

**Your Achievements Today**:
- ✅ Extended focused learning session
- ✅ Maintained your ${this.currentUser.streak}-day streak
- ✅ Engaged with multiple learning modalities
- ✅ Applied computational thinking skills

**Streak Bonus**: You're building incredible learning habits! Consistent daily engagement is the key to mastering STEAM concepts.

**Tomorrow's Challenge**: Ready to level up? I have some exciting advanced challenges that will push your boundaries while building on today's foundation.

Keep up the amazing work, ${this.currentUser.name}! 🌟`);
    }
    
    scheduleEncouragement() {
        const encouragements = [
            "Your logical-mathematical thinking is really shining through!",
            "I love how you're connecting different STEAM concepts!",
            "Your visual approach to problem-solving is excellent!",
            "You're developing real 21st-century skills!",
            "The way you break down complex problems shows great computational thinking!"
        ];
        
        setTimeout(() => {
            const randomEncouragement = encouragements[Math.floor(Math.random() * encouragements.length)];
            this.showEncouragementToast(randomEncouragement);
        }, Math.random() * 600000 + 300000); // Random time between 5-15 minutes
    }
    
    showEncouragementToast(message) {
        const toast = document.createElement('div');
        toast.className = 'encouragement-toast fade-in';
        toast.innerHTML = `
            <div class="toast-icon">
                <i class="fas fa-star"></i>
            </div>
            <div class="toast-message">${message}</div>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 4000);
    }
    
    // Utility functions
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    handleNavigation(section) {
        // Handle navigation between different sections
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        document.querySelector(`[href="${section}"]`).classList.add('active');
        
        // Scroll to relevant section or load content
        this.loadSectionContent(section.replace('#', ''));
    }
    
    loadSectionContent(section) {
        // Load content based on navigation selection
        const contentMessages = {
            'dashboard': 'Welcome back to your dashboard! Here\'s your learning overview.',
            'projects': 'Here are all your STEAM projects - active, completed, and recommended.',
            'robotics': 'Welcome to the Robotics Lab! Your Modi kit is ready for action.',
            'coding': 'Let\'s dive into Python coding with STEAM applications!',
            'library': 'Access your curated resource library with age-appropriate content.'
        };
        
        if (contentMessages[section]) {
            this.addMessageToChat('assistant', contentMessages[section]);
        }
    }
}

// Initialize the dashboard when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.steamDashboard = new STEAMDashboard();
    
    // Add some CSS for dynamic elements
    const dynamicStyles = `
        <style>
        .typing-dots {
            display: inline-block;
            margin-right: 0.5rem;
        }
        
        .typing-dots span {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #667eea;
            margin: 0 2px;
            animation: typing 1.4s infinite ease-in-out both;
        }
        
        .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
        .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes typing {
            0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
            40% { transform: scale(1); opacity: 1; }
        }
        
        .encouragement-toast {
            position: fixed;
            bottom: 100px;
            right: 2rem;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
            display: flex;
            align-items: center;
            gap: 0.5rem;
            z-index: 1001;
            max-width: 300px;
        }
        
        .toast-icon {
            font-size: 1.25rem;
        }
        
        .fade-out {
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
        }
        
        .recommended-badge {
            position: absolute;
            top: -10px;
            right: -10px;
            background: linear-gradient(135deg, #ffc107, #ff6b35);
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }
        </style>
    `;
    
    document.head.insertAdjacentHTML('beforeend', dynamicStyles);
});

// Add some utility functions to window for debugging/development
window.steamUtils = {
    simulateUserAction: (action) => {
        console.log(`Simulating user action: ${action}`);
        window.steamDashboard.handleQuickAction(action);
    },
    
    addTestMessage: (content) => {
        window.steamDashboard.addMessageToChat('user', content);
    },
    
    showEngagement: () => {
        window.steamDashboard.showProgressCelebration();
    }
};