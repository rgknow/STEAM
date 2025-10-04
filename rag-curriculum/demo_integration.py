"""
RAG Curriculum System Integration Example
Demonstrates the complete RAG system for educational curricula and resources
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

# Import all RAG components
from rag_curriculum.rag_engine import RAGEngine
from rag_curriculum.curriculum_indexer import CurriculumIndexer, LearningLevel, SubjectArea, CurriculumStandard
from rag_curriculum.resource_processor import ResourceProcessor, ResourceType
from rag_curriculum.query_handler import QueryHandler
from rag_curriculum.embedding_manager import EmbeddingManager, EmbeddingConfig, EmbeddingModel


async def create_sample_curriculum_data():
    """Create comprehensive sample curriculum data for all three levels."""
    
    # Grade Level Curriculum Data
    grade_level_data = [
        {
            "id": "k_math_counting",
            "content": """Kindergarten Mathematics: Counting and Number Recognition
            
Learning Objectives:
- Students will count from 1 to 20
- Students will recognize and write numbers 1-10
- Students will understand one-to-one correspondence
- Students will compare quantities using more, less, and equal

Standards Alignment: CCSS.MATH.K.CC.A.1, CCSS.MATH.K.CC.A.3

Activities:
1. Counting bears and manipulatives
2. Number line games
3. Quantity comparison exercises
4. Number formation practice

Materials: counting bears, number cards, worksheets, manipulatives
Duration: 2 weeks
Assessment: Observation checklist, number recognition quiz""",
            "metadata": {
                "title": "Kindergarten Counting and Numbers",
                "subject_area": "mathematics",
                "grade": "K",
                "topic": "counting",
                "standards": ["CCSS.MATH.K.CC.A.1", "CCSS.MATH.K.CC.A.3"],
                "difficulty_level": "beginner"
            }
        },
        {
            "id": "grade3_science_plants",
            "content": """Grade 3 Science: Plant Life Cycles and Needs
            
Learning Objectives:
- Students will identify the stages of a plant life cycle
- Students will explain what plants need to grow and survive
- Students will observe and record plant growth over time
- Students will compare different types of plants and their characteristics

Standards Alignment: NGSS 3-LS1-1, NGSS 3-LS4-3

Hands-on Activities:
1. Plant germination experiments
2. Life cycle observation journals
3. Plant needs investigation (light, water, soil)
4. Compare local plants and their adaptations

Materials: seeds, soil, pots, measuring tools, observation journals
Duration: 4 weeks
Assessment: Scientific journal, plant growth data collection, life cycle diagram""",
            "metadata": {
                "title": "Plant Life Cycles",
                "subject_area": "science",
                "grade": 3,
                "topic": "life_cycles",
                "standards": ["NGSS 3-LS1-1", "NGSS 3-LS4-3"],
                "difficulty_level": "intermediate"
            }
        },
        {
            "id": "grade8_engineering_design",
            "content": """Grade 8 Engineering: Design Process and Problem Solving
            
Learning Objectives:
- Students will apply the engineering design process to solve real-world problems
- Students will identify constraints and criteria for design solutions
- Students will test and iterate on design prototypes
- Students will communicate design solutions effectively

Standards Alignment: NGSS MS-ETS1-1, NGSS MS-ETS1-2, NGSS MS-ETS1-3

Project-Based Learning:
1. Define a community problem that needs an engineering solution
2. Research existing solutions and constraints
3. Brainstorm and sketch multiple design ideas
4. Build and test prototypes
5. Iterate based on testing results
6. Present final solutions to community partners

Materials: cardboard, tape, motors, sensors, 3D printing materials, design software
Duration: 6 weeks
Assessment: Design portfolio, prototype functionality, presentation rubric""",
            "metadata": {
                "title": "Engineering Design Process",
                "subject_area": "engineering",
                "grade": 8,
                "topic": "design_process",
                "standards": ["NGSS MS-ETS1-1", "NGSS MS-ETS1-2", "NGSS MS-ETS1-3"],
                "difficulty_level": "advanced"
            }
        }
    ]
    
    # Global Learning Standards Data
    global_learning_data = [
        {
            "id": "ib_math_inquiry",
            "content": """International Baccalaureate Mathematics: Mathematical Inquiry and Problem Solving
            
Global Learning Framework:
This curriculum develops mathematical thinking through inquiry-based approaches that transcend cultural boundaries. Students engage with mathematics as a universal language while appreciating diverse problem-solving methods from different cultures.

Learning Objectives:
- Develop mathematical reasoning and logical thinking
- Apply mathematical concepts to real-world global challenges
- Appreciate the historical and cultural development of mathematics
- Communicate mathematical ideas across linguistic and cultural barriers

Cross-Cultural Connections:
- Ancient number systems from various civilizations
- Traditional mathematical practices from different cultures
- Global applications of mathematics in economics, science, and technology
- Collaborative problem-solving with international partner schools

Assessment Approaches:
- Portfolio of mathematical investigations
- Reflection on cultural perspectives in mathematics
- Peer collaboration with global classrooms
- Mathematical modeling of world issues

Duration: Full academic year
Language: Multiple languages supported with translation resources""",
            "metadata": {
                "title": "Global Mathematical Inquiry",
                "subject_area": "mathematics",
                "topic": "mathematical_thinking",
                "curriculum_standard": "ib",
                "cultural_context": ["international", "multicultural"],
                "difficulty_level": "intermediate"
            }
        },
        {
            "id": "unesco_sustainability",
            "content": """UNESCO Education for Sustainable Development: Environmental Science and Global Citizenship
            
Global Learning Objectives:
- Understand interconnections between local and global environmental challenges
- Develop skills for sustainable living and decision-making
- Foster global citizenship and responsibility for planetary stewardship
- Build capacity for collaborative action on sustainability challenges

Key Themes:
1. Climate Change and Global Impact
2. Biodiversity Conservation Across Cultures
3. Sustainable Resource Management
4. Environmental Justice and Equity
5. Indigenous Knowledge and Traditional Practices

International Collaboration:
- Partner schools from different continents
- Shared environmental monitoring projects
- Cultural exchange on sustainability practices
- Joint advocacy for environmental policies

Learning Activities:
- Global environmental data analysis
- Cross-cultural interviews on sustainability practices
- Collaborative research on regional environmental challenges
- International youth environmental summit participation

Assessment Methods:
- Global project portfolios
- Peer evaluation across international teams
- Reflection on cultural perspectives
- Action plan development for local implementation

Languages: Available in UN official languages with cultural adaptation guides""",
            "metadata": {
                "title": "Global Environmental Citizenship",
                "subject_area": "science",
                "topic": "sustainability",
                "curriculum_standard": "unesco",
                "cultural_context": ["global", "indigenous_knowledge", "international_cooperation"],
                "difficulty_level": "advanced"
            }
        }
    ]
    
    # Global Competition Level Data
    competition_data = [
        {
            "id": "frc_robotics_advanced",
            "content": """FIRST Robotics Competition: Advanced Autonomous Systems and Strategy
            
Competition Overview:
Prepare teams for the highest levels of international robotics competition. Focus on advanced programming concepts, sophisticated mechanical design, and strategic thinking required for FRC World Championship level performance.

Technical Requirements:
- Advanced sensor fusion for autonomous navigation
- Real-time computer vision processing
- Complex mechanical systems with multiple degrees of freedom
- Strategic alliance formation and game theory application
- Advanced programming concepts including multithreading and optimization

Skills Development:
1. Advanced Programming
   - Machine learning for autonomous decision making
   - Computer vision algorithms for object recognition
   - Path planning and motion control systems
   - Real-time system optimization

2. Mechanical Engineering
   - CAD design for complex assemblies
   - Stress analysis and material selection
   - Precision manufacturing techniques
   - System integration and testing

3. Strategic Thinking
   - Game analysis and meta-strategy development
   - Alliance partner selection algorithms
   - Risk assessment and contingency planning
   - Performance analytics and optimization

4. Team Leadership
   - Project management for large technical teams
   - Mentoring and knowledge transfer
   - Competition preparation and logistics
   - Sponsor relations and fundraising

Training Timeline:
- Pre-season: 6 months of skill building and team preparation
- Build season: 6 weeks of intensive robot development
- Competition season: 2-3 months of competition and improvement

Competition Preparation:
- Regional competition strategy
- Championship qualification pathways
- International competition protocols
- Professional mentorship networks

Assessment Criteria:
- Robot performance metrics
- Technical documentation quality
- Team collaboration effectiveness
- Innovation and creativity demonstration
- Professional presentation skills""",
            "metadata": {
                "title": "Advanced FRC Competition Preparation",
                "subject_area": "robotics",
                "topic": "competition_robotics",
                "difficulty_level": "expert",
                "competition_type": "FIRST Robotics Competition",
                "target_audience": ["high_school", "advanced_students"]
            }
        },
        {
            "id": "math_olympiad_number_theory",
            "content": """International Mathematical Olympiad: Advanced Number Theory and Problem Solving
            
Competition Level: International Mathematical Olympiad (IMO) Preparation
            
Advanced Topics Covered:
1. Elementary Number Theory
   - Divisibility and prime numbers
   - Modular arithmetic and congruences
   - Diophantine equations
   - Quadratic residues and reciprocity

2. Advanced Techniques
   - Mathematical induction variations
   - Pigeonhole principle applications
   - Extremal principles
   - Invariant and monovariant methods

3. Competition Strategies
   - Problem classification and recognition
   - Solution writing and presentation
   - Time management during competitions
   - Psychological preparation for high-stakes events

Problem-Solving Methodology:
- Pattern recognition in competition problems
- Multiple solution approaches for single problems
- Proof techniques and mathematical rigor
- Creative problem-solving under time pressure

Training Structure:
1. Theoretical Foundation (3 months)
   - Core concepts and theorem mastery
   - Proof technique development
   - Historical problem analysis

2. Intensive Problem Solving (6 months)
   - Daily practice with IMO-level problems
   - Mock competitions and time trials
   - Collaborative problem-solving sessions
   - Individual coaching and feedback

3. Competition Preparation (2 months)
   - Final skill refinement
   - Psychological preparation
   - Competition simulation
   - Strategic planning for actual competition

International Network:
- Connection with IMO training programs worldwide
- Access to historical IMO problems and solutions
- Mentorship from former IMO participants
- International mathematical community engagement

Success Metrics:
- National olympiad qualification
- IMO team selection
- Medal achievement at international level
- Preparation for advanced mathematical studies""",
            "metadata": {
                "title": "IMO Number Theory Mastery",
                "subject_area": "mathematics",
                "topic": "number_theory",
                "difficulty_level": "expert",
                "competition_type": "International Mathematical Olympiad",
                "target_audience": ["advanced_high_school", "competition_students"]
            }
        }
    ]
    
    return {
        "grade_level": grade_level_data,
        "global_learning": global_learning_data,
        "competition": competition_data
    }


async def create_sample_resource_data():
    """Create sample educational resources for all three levels."""
    
    # Grade Level Resources
    grade_resources = [
        {
            "id": "elementary_math_guide",
            "content": """Elementary Mathematics Teaching Guide: Best Practices for K-5
            
Introduction:
This comprehensive guide provides elementary teachers with research-based strategies for teaching mathematics to young learners. Emphasis is placed on conceptual understanding, visual learning, and hands-on exploration.

Key Teaching Strategies:
1. Concrete-Pictorial-Abstract (CPA) Progression
   - Begin with physical manipulatives
   - Progress to visual representations
   - Develop abstract understanding
   - Provide multiple representation opportunities

2. Number Sense Development
   - Daily number talks and discussions
   - Estimation and reasoning activities
   - Pattern recognition and extension
   - Mental math strategy development

3. Problem-Solving Approaches
   - Real-world context connections
   - Multiple solution strategies
   - Student explanation and justification
   - Collaborative problem-solving

Classroom Management Tips:
- Organize math manipulatives for easy access
- Create math talk sentence starters for discussions
- Establish routines for different types of math activities
- Use visual displays to support learning

Assessment Strategies:
- Observational assessments during math work
- Student self-reflection and goal setting
- Portfolio documentation of mathematical thinking
- Formative assessment through math journals

Common Challenges and Solutions:
- Supporting students with math anxiety
- Differentiating for diverse learning needs
- Connecting math to other subject areas
- Communicating with parents about math learning

Professional Development Resources:
- Recommended readings on elementary mathematics
- Professional organizations and conferences
- Online communities for elementary math teachers
- Graduate study opportunities in mathematics education""",
            "metadata": {
                "title": "Elementary Mathematics Teaching Guide",
                "resource_type": "user_guide",
                "target_audience": ["teachers"],
                "subject_areas": ["mathematics"],
                "grade_levels": ["K", 1, 2, 3, 4, 5],
                "difficulty_level": "intermediate"
            }
        },
        {
            "id": "stem_activity_collection",
            "content": """STEM Activity Collection: Hands-On Learning for Middle School
            
Activity 1: Bridge Building Challenge
Objective: Apply engineering design process to build strongest bridge
Materials: Cardboard, tape, pennies for weight testing
Process: Design → Build → Test → Redesign → Present
NGSS Alignment: MS-ETS1-1, MS-ETS1-2

Activity 2: Water Quality Investigation
Objective: Test and analyze local water sources for quality indicators
Materials: Test strips, microscopes, data collection sheets
Process: Hypothesis → Testing → Data Analysis → Conclusions
NGSS Alignment: MS-ESS3-3, MS-ETS1-1

Activity 3: Renewable Energy Solutions
Objective: Design and build working models of renewable energy systems
Materials: Solar panels, motors, batteries, building materials
Process: Research → Design → Build → Test → Optimize
NGSS Alignment: MS-ESS3-3, MS-ETS1-4

Activity 4: Robotics and Programming
Objective: Program robots to complete navigation challenges
Materials: Educational robots, programming software, obstacle courses
Process: Problem Analysis → Algorithm Design → Programming → Testing
CSTA Alignment: 1B-AP-11, 1B-AP-13

Assessment Rubrics:
- Engineering Design Process Application
- Scientific Method Implementation
- Collaboration and Communication
- Problem-Solving and Critical Thinking

Extensions and Modifications:
- Advanced challenges for accelerated learners
- Scaffolding supports for struggling students
- Connections to real-world career applications
- Integration with other academic subjects

Safety Considerations:
- Proper tool usage and supervision
- Material handling guidelines
- Emergency procedures
- Age-appropriate risk assessment""",
            "metadata": {
                "title": "Middle School STEM Activities",
                "resource_type": "activity_guide",
                "target_audience": ["teachers"],
                "subject_areas": ["science", "technology", "engineering", "mathematics"],
                "grade_levels": [6, 7, 8],
                "difficulty_level": "intermediate"
            }
        }
    ]
    
    # Global Learning Resources
    global_resources = [
        {
            "id": "multicultural_stem_practices",
            "content": """Multicultural STEM Education: Global Perspectives and Practices
            
Introduction:
This resource guide helps educators integrate diverse cultural perspectives into STEM education. Drawing from indigenous knowledge systems, international educational practices, and multicultural approaches to scientific thinking.

Cultural Perspectives in Mathematics:
1. Indigenous Number Systems
   - Mayan vigesimal system and calendar calculations
   - Aboriginal Australian counting systems and land management
   - African fractional concepts in traditional crafts
   - Asian abacus traditions and mental mathematics

2. Traditional Problem-Solving Methods
   - Islamic geometric patterns and architectural mathematics
   - Native American astronomical observations and predictions
   - Ancient Egyptian engineering and construction techniques
   - Chinese traditional medicine and mathematical modeling

Global Science Practices:
1. Traditional Ecological Knowledge
   - Indigenous plant medicine and chemical compounds
   - Traditional weather prediction and climate understanding
   - Sustainable agriculture practices across cultures
   - Animal behavior knowledge and biological insights

2. International Scientific Collaboration
   - Global climate research partnerships
   - International space exploration projects
   - Cross-cultural medical research initiatives
   - Worldwide biodiversity conservation efforts

Implementation Strategies:
- Guest speakers from diverse cultural backgrounds
- Virtual exchanges with international classrooms
- Multilingual STEM resources and materials
- Cultural celebration integration with STEM concepts
- Community partnerships with cultural organizations

Assessment Considerations:
- Multiple ways of demonstrating knowledge
- Cultural responsiveness in evaluation methods
- Portfolio approaches that honor diverse perspectives
- Peer evaluation across cultural contexts

Professional Development:
- Cultural competency training for STEM educators
- International teacher exchange programs
- Multicultural curriculum development workshops
- Community engagement and partnership building""",
            "metadata": {
                "title": "Multicultural STEM Education Guide",
                "resource_type": "best_practices",
                "target_audience": ["teachers", "administrators"],
                "subject_areas": ["science", "technology", "engineering", "mathematics"],
                "cultural_context": ["multicultural", "indigenous_knowledge", "international"],
                "difficulty_level": "advanced"
            }
        }
    ]
    
    # Competition Level Resources
    competition_resources = [
        {
            "id": "robotics_competition_strategy",
            "content": """Advanced Robotics Competition Strategy and Preparation
            
Competition Analysis Framework:
This guide provides systematic approaches to analyzing robotics competitions and developing winning strategies for high-level competitions including FRC, VEX, and international robotics championships.

Game Analysis Methodology:
1. Rule Set Deconstruction
   - Identify all scoring mechanisms and point values
   - Analyze timing constraints and match flow
   - Map field elements and spatial relationships
   - Understand penalty structures and risk factors

2. Meta-Game Development
   - Historical analysis of successful strategies
   - Prediction of competition evolution patterns
   - Alliance formation strategy optimization
   - Risk/reward calculation for different approaches

3. Robot Design Philosophy
   - Capability prioritization based on expected meta-game
   - Modular design for mid-season adaptability
   - Reliability versus performance trade-offs
   - Manufacturing timeline and resource constraints

Advanced Programming Concepts:
1. Autonomous Period Optimization
   - Path planning algorithms and implementation
   - Sensor fusion for robust localization
   - Machine learning for adaptive behaviors
   - Real-time decision making under uncertainty

2. TeleOp Performance Enhancement
   - Driver assistance systems and automation
   - Predictive interfaces and feedback systems
   - Performance analytics and optimization
   - Human-robot interface design

3. Competition Software Architecture
   - Robust code structure for competition environment
   - Data logging and match analysis systems
   - Emergency procedures and failsafe implementations
   - Version control and deployment strategies

Team Management Excellence:
1. Technical Team Organization
   - Role specialization and cross-training
   - Knowledge documentation and transfer
   - Mentor integration and guidance utilization
   - Skill development pathways for team members

2. Competition Preparation
   - Practice competition scheduling and execution
   - Equipment maintenance and spare parts management
   - Transportation and logistics planning
   - Scouting and alliance selection strategies

3. Performance Analysis
   - Match data collection and analysis systems
   - Continuous improvement methodologies
   - Post-competition evaluation and learning
   - Season planning and goal setting

Championship Pathways:
- Regional competition strategy and qualification
- Championship preparation and advancement
- International competition protocols
- Professional networking and career development

Success Metrics and Evaluation:
- Quantitative performance measurements
- Qualitative skill development assessment
- Team culture and collaboration evaluation
- Long-term impact on participant development""",
            "metadata": {
                "title": "Advanced Robotics Competition Strategy",
                "resource_type": "reference_manual",
                "target_audience": ["advanced_students", "coaches"],
                "subject_areas": ["robotics", "engineering", "technology"],
                "difficulty_level": "expert",
                "competition_type": "robotics_competitions"
            }
        }
    ]
    
    return {
        "grade_level": grade_resources,
        "global_learning": global_resources,
        "competition": competition_resources
    }


async def demonstrate_complete_rag_system():
    """Demonstrate the complete RAG system functionality."""
    
    print("=== Complete RAG Curriculum System Demo ===")
    print(f"Starting comprehensive demo at {datetime.now()}")
    
    # Step 1: Initialize all components
    print("\n1. Initializing RAG System Components...")
    
    # Initialize RAG engine
    rag_engine = RAGEngine()
    print("   ✓ RAG Engine initialized")
    
    # Initialize curriculum indexer
    curriculum_indexer = CurriculumIndexer(rag_engine)
    await curriculum_indexer.initialize_collections()
    print("   ✓ Curriculum Indexer initialized with collections")
    
    # Initialize resource processor  
    resource_processor = ResourceProcessor(rag_engine)
    await resource_processor.initialize_resource_collections()
    print("   ✓ Resource Processor initialized with collections")
    
    # Initialize embedding manager
    embedding_config = EmbeddingConfig(
        model_name=EmbeddingModel.ALL_MINILM_L6_V2,
        dimension=384,
        batch_size=16,
        normalize_embeddings=True,
        cache_embeddings=True
    )
    
    try:
        embedding_manager = EmbeddingManager(embedding_config)
        print("   ✓ Embedding Manager initialized with SentenceTransformers")
    except ImportError:
        # Fall back to mock for demo
        embedding_manager = EmbeddingManager(embedding_config)
        print("   ✓ Embedding Manager initialized with mock provider")
    
    # Initialize query handler
    query_handler = QueryHandler(rag_engine, curriculum_indexer, resource_processor)
    print("   ✓ Query Handler initialized")
    
    # Step 2: Load sample data
    print("\n2. Loading Sample Educational Data...")
    
    curriculum_data = await create_sample_curriculum_data()
    resource_data = await create_sample_resource_data()
    
    # Index curriculum data for all learning levels
    for level_name, data in curriculum_data.items():
        level_enum = {
            "grade_level": LearningLevel.GRADE_LEVEL,
            "global_learning": LearningLevel.GLOBAL_LEARNING, 
            "competition": LearningLevel.GLOBAL_COMPETITION
        }[level_name]
        
        await curriculum_indexer.index_curriculum_content(data, level_enum)
        print(f"   ✓ Indexed {len(data)} {level_name} curriculum items")
    
    # Process resource data for all learning levels
    for level_name, resources in resource_data.items():
        level_enum = {
            "grade_level": LearningLevel.GRADE_LEVEL,
            "global_learning": LearningLevel.GLOBAL_LEARNING,
            "competition": LearningLevel.GLOBAL_COMPETITION
        }[level_name]
        
        for resource in resources:
            # Create temporary resource content for processing
            resource_enhanced = {
                **resource,
                "metadata": {
                    **resource["metadata"],
                    "learning_level": level_enum.value
                }
            }
            
            # Add to appropriate collection
            collection_id = resource_processor.resource_collections[level_enum]
            await rag_engine.add_documents_to_collection(collection_id, [resource_enhanced])
        
        print(f"   ✓ Processed {len(resources)} {level_name} resource items")
    
    # Step 3: Demonstrate comprehensive queries
    print("\n3. Demonstrating Advanced Query Capabilities...")
    
    demo_queries = [
        {
            "query": "How do I teach fractions to Grade 3 students using hands-on activities?",
            "context": {"role": "teacher", "experience_level": "intermediate"},
            "description": "Grade-level lesson planning query"
        },
        {
            "query": "What are the NGSS standards for middle school engineering design?",
            "context": {"role": "teacher", "depth_preference": "comprehensive"},
            "description": "Standards alignment query"
        },
        {
            "query": "I need advanced robotics competition preparation resources for FRC teams",
            "context": {"role": "coach", "experience_level": "advanced"},
            "description": "Competition-level resource query"
        },
        {
            "query": "Show me multicultural approaches to STEM education for international classrooms",
            "context": {"role": "administrator", "depth_preference": "comprehensive"},
            "description": "Global learning perspective query"
        },
        {
            "query": "What assessment methods work best for project-based engineering learning?",
            "context": {"role": "teacher", "experience_level": "intermediate"},
            "description": "Assessment strategy query"
        }
    ]
    
    for i, demo_query in enumerate(demo_queries, 1):
        print(f"\n   Query {i}: {demo_query['description']}")
        print(f"   Question: {demo_query['query']}")
        
        try:
            response = await query_handler.handle_query(
                demo_query["query"], 
                demo_query["context"]
            )
            
            print(f"   Intent: {response.query_context.intent.value}")
            print(f"   Complexity: {response.query_context.complexity.value}")
            print(f"   Learning Levels: {[l.value for l in response.query_context.learning_levels]}")
            print(f"   Subject Areas: {[s.value for s in response.query_context.subject_areas]}")
            print(f"   Sources Used: {response.total_sources}")
            print(f"   Confidence: {response.confidence_score:.2f}")
            print(f"   Answer Preview: {response.primary_answer[:150]}...")
            
            if response.suggested_follow_ups:
                print(f"   Follow-ups: {response.suggested_follow_ups[:2]}")
                
        except Exception as e:
            print(f"   Error processing query: {e}")
    
    # Step 4: Demonstrate advanced features
    print("\n4. Demonstrating Advanced RAG Features...")
    
    # Embedding similarity analysis
    print("\n   4a. Semantic Similarity Analysis")
    educational_concepts = [
        "hands-on learning activities",
        "project-based STEM education", 
        "assessment rubrics for engineering",
        "robotics competition preparation",
        "multicultural mathematics teaching"
    ]
    
    similarity_results = await embedding_manager.find_most_similar(
        "interactive learning methods", 
        educational_concepts, 
        top_k=3
    )
    
    print(f"   Query: 'interactive learning methods'")
    for concept, similarity in similarity_results:
        print(f"   Similarity {similarity:.3f}: {concept}")
    
    # Collection statistics
    print("\n   4b. Collection Statistics")
    for level in LearningLevel:
        if level in curriculum_indexer.level_collections:
            collection_id = curriculum_indexer.level_collections[level]
            stats = await rag_engine.get_collection_statistics(collection_id)
            print(f"   {level.value}: {stats['total_chunks']} chunks, {stats['source_documents']} documents")
    
    # Query enhancement demonstration
    print("\n   4c. Query Enhancement")
    original_query = "math teaching"
    context_texts = [item["content"] for item in curriculum_data["grade_level"] if "math" in item["content"].lower()]
    
    enhanced_query = await embedding_manager.enhance_query(original_query, context_texts[:3])
    print(f"   Original: {original_query}")
    print(f"   Enhanced: {enhanced_query}")
    
    # Performance metrics
    print("\n5. System Performance Summary")
    
    embedding_stats = embedding_manager.get_performance_stats()
    print(f"   Total embeddings generated: {embedding_stats['total_embeddings_generated']}")
    print(f"   Cache hit rate: {embedding_stats.get('cache_hit_rate', 0):.2%}")
    print(f"   Average processing time: {embedding_stats.get('avg_processing_time', 0):.4f}s")
    
    # Model information
    model_info = embedding_manager.get_model_info()
    print(f"   Embedding model: {model_info['model_name']}")
    print(f"   Embedding dimension: {model_info['dimension']}")
    print(f"   Provider type: {model_info['provider_type']}")
    
    # Collection overview
    collections = rag_engine.list_collections()
    print(f"   Total collections: {len(collections)}")
    
    total_documents = sum(
        col.get('document_count', 0) for col in collections
    )
    print(f"   Total documents indexed: {total_documents}")
    
    print(f"\n=== Demo completed successfully at {datetime.now()} ===")
    print("\nThe RAG Curriculum System demonstrates:")
    print("✓ Multi-level curriculum indexing (Grade, Global, Competition)")
    print("✓ Comprehensive resource processing and classification")
    print("✓ Intelligent query analysis and intent recognition")
    print("✓ Advanced embedding and semantic similarity")
    print("✓ Context-aware response generation")
    print("✓ Performance optimization with caching")
    print("✓ Educational domain expertise integration")


async def run_specific_use_cases():
    """Run specific educational use cases to demonstrate practical applications."""
    
    print("\n=== Specific Educational Use Cases ===")
    
    # Initialize minimal system for use cases
    rag_engine = RAGEngine()
    curriculum_indexer = CurriculumIndexer(rag_engine)
    resource_processor = ResourceProcessor(rag_engine)
    query_handler = QueryHandler(rag_engine, curriculum_indexer, resource_processor)
    
    await curriculum_indexer.initialize_collections()
    await resource_processor.initialize_resource_collections()
    
    # Use Case 1: Teacher Lesson Planning
    print("\n1. Use Case: Elementary Teacher Planning Math Lesson")
    teacher_query = "I need a hands-on fraction lesson for 3rd graders that aligns with Common Core standards"
    
    context = await query_handler.analyzer.analyze_query(teacher_query)
    print(f"   Intent detected: {context.intent.value}")
    print(f"   Subject areas: {[s.value for s in context.subject_areas]}")
    print(f"   Grade levels: {context.grade_levels}")
    print(f"   Keywords: {context.keywords[:5]}")
    
    # Use Case 2: Administrator Curriculum Review
    print("\n2. Use Case: Administrator Reviewing STEM Programs")
    admin_query = "Show me research on effective STEM education practices for middle school programs"
    
    context = await query_handler.analyzer.analyze_query(admin_query, {"role": "administrator"})
    print(f"   Intent detected: {context.intent.value}")
    print(f"   Complexity: {context.complexity.value}")
    print(f"   Target audience: {context.target_audience}")
    
    # Use Case 3: Competition Coach Preparation
    print("\n3. Use Case: Robotics Coach Preparing Team")
    coach_query = "Advanced programming strategies for autonomous period in robotics competitions"
    
    context = await query_handler.analyzer.analyze_query(coach_query, {"role": "coach", "experience_level": "advanced"})
    print(f"   Intent detected: {context.intent.value}")
    print(f"   Learning levels: {[l.value for l in context.learning_levels]}")
    print(f"   Preferred resources: {[r.value for r in context.preferred_resource_types]}")
    
    print("\n✓ Use cases demonstrate practical query understanding and context extraction")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the complete demonstration
    asyncio.run(demonstrate_complete_rag_system())
    
    # Run specific use cases
    asyncio.run(run_specific_use_cases())