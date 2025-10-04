"""
Age Adaptation System for STEAM Encyclopedia
Sophisticated system for adapting content to different developmental stages and learning capabilities
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
from datetime import datetime
import json

from agents.base_agent import ContentItem, AgeGroup


class CognitiveStage(Enum):
    """Piaget's cognitive development stages mapped to age groups."""
    SENSORIMOTOR = "sensorimotor"          # 0-2 years
    PREOPERATIONAL = "preoperational"      # 2-7 years  
    CONCRETE_OPERATIONAL = "concrete"      # 7-11 years
    FORMAL_OPERATIONAL = "formal"          # 11+ years


class LearningStyle(Enum):
    """Different learning modalities."""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"


@dataclass
class AgeGroupProfile:
    """Detailed profile for each age group including learning characteristics."""
    age_group: AgeGroup
    cognitive_stage: CognitiveStage
    attention_span_minutes: int
    vocabulary_level: str
    preferred_learning_styles: List[LearningStyle]
    content_length_words: Tuple[int, int]  # (min, max)
    sentence_length_words: int
    concepts_per_session: int
    multimedia_preferences: List[str]
    safety_considerations: List[str]
    
    # Cognitive capabilities
    abstract_thinking: bool
    logical_reasoning: bool
    hypothesis_formation: bool
    mathematical_operations: List[str]
    scientific_method_understanding: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "age_group": self.age_group.value,
            "cognitive_stage": self.cognitive_stage.value,
            "attention_span_minutes": self.attention_span_minutes,
            "vocabulary_level": self.vocabulary_level,
            "preferred_learning_styles": [style.value for style in self.preferred_learning_styles],
            "content_length_words": self.content_length_words,
            "sentence_length_words": self.sentence_length_words,
            "concepts_per_session": self.concepts_per_session,
            "multimedia_preferences": self.multimedia_preferences,
            "safety_considerations": self.safety_considerations,
            "abstract_thinking": self.abstract_thinking,
            "logical_reasoning": self.logical_reasoning,
            "hypothesis_formation": self.hypothesis_formation,
            "mathematical_operations": self.mathematical_operations,
            "scientific_method_understanding": self.scientific_method_understanding
        }


class AgeAdaptationEngine:
    """Core engine for adapting content to different age groups."""
    
    def __init__(self):
        self.age_profiles = self._initialize_age_profiles()
        self.vocabulary_levels = self._load_vocabulary_levels()
        self.concept_hierarchies = self._build_concept_hierarchies()
        self.safety_filters = self._initialize_safety_filters()
        
    def _initialize_age_profiles(self) -> Dict[AgeGroup, AgeGroupProfile]:
        """Initialize detailed profiles for each age group."""
        return {
            AgeGroup.EARLY_YEARS: AgeGroupProfile(
                age_group=AgeGroup.EARLY_YEARS,
                cognitive_stage=CognitiveStage.PREOPERATIONAL,
                attention_span_minutes=5,
                vocabulary_level="basic_500",
                preferred_learning_styles=[LearningStyle.VISUAL, LearningStyle.KINESTHETIC],
                content_length_words=(50, 150),
                sentence_length_words=8,
                concepts_per_session=1,
                multimedia_preferences=["pictures", "simple_animations", "songs", "interactive_games"],
                safety_considerations=["no_small_parts", "adult_supervision", "safe_materials"],
                abstract_thinking=False,
                logical_reasoning=False,
                hypothesis_formation=False,
                mathematical_operations=["counting", "basic_shapes", "size_comparison"],
                scientific_method_understanding=False
            ),
            
            AgeGroup.ELEMENTARY: AgeGroupProfile(
                age_group=AgeGroup.ELEMENTARY,
                cognitive_stage=CognitiveStage.CONCRETE_OPERATIONAL,
                attention_span_minutes=15,
                vocabulary_level="elementary_2000",
                preferred_learning_styles=[LearningStyle.VISUAL, LearningStyle.KINESTHETIC, LearningStyle.AUDITORY],
                content_length_words=(200, 500),
                sentence_length_words=12,
                concepts_per_session=2,
                multimedia_preferences=["diagrams", "videos", "hands_on_activities", "simple_experiments"],
                safety_considerations=["supervised_experiments", "safe_tools", "clear_instructions"],
                abstract_thinking=False,
                logical_reasoning=True,
                hypothesis_formation=True,
                mathematical_operations=["addition", "subtraction", "multiplication", "division", "fractions"],
                scientific_method_understanding=True
            ),
            
            AgeGroup.MIDDLE_SCHOOL: AgeGroupProfile(
                age_group=AgeGroup.MIDDLE_SCHOOL,
                cognitive_stage=CognitiveStage.FORMAL_OPERATIONAL,
                attention_span_minutes=25,
                vocabulary_level="middle_school_5000",
                preferred_learning_styles=[LearningStyle.VISUAL, LearningStyle.READING_WRITING],
                content_length_words=(500, 1000),
                sentence_length_words=15,
                concepts_per_session=3,
                multimedia_preferences=["interactive_simulations", "detailed_diagrams", "lab_activities"],
                safety_considerations=["lab_safety", "chemical_safety", "equipment_training"],
                abstract_thinking=True,
                logical_reasoning=True,
                hypothesis_formation=True,
                mathematical_operations=["algebra", "geometry", "basic_statistics"],
                scientific_method_understanding=True
            ),
            
            AgeGroup.HIGH_SCHOOL: AgeGroupProfile(
                age_group=AgeGroup.HIGH_SCHOOL,
                cognitive_stage=CognitiveStage.FORMAL_OPERATIONAL,
                attention_span_minutes=45,
                vocabulary_level="high_school_8000",
                preferred_learning_styles=[LearningStyle.READING_WRITING, LearningStyle.VISUAL],
                content_length_words=(1000, 2000),
                sentence_length_words=18,
                concepts_per_session=4,
                multimedia_preferences=["complex_simulations", "research_tools", "data_analysis"],
                safety_considerations=["advanced_lab_safety", "research_ethics", "proper_citations"],
                abstract_thinking=True,
                logical_reasoning=True,
                hypothesis_formation=True,
                mathematical_operations=["calculus", "statistics", "trigonometry", "advanced_algebra"],
                scientific_method_understanding=True
            ),
            
            AgeGroup.HIGHER_ED: AgeGroupProfile(
                age_group=AgeGroup.HIGHER_ED,
                cognitive_stage=CognitiveStage.FORMAL_OPERATIONAL,
                attention_span_minutes=90,
                vocabulary_level="advanced_15000",
                preferred_learning_styles=[LearningStyle.READING_WRITING, LearningStyle.VISUAL],
                content_length_words=(2000, 5000),
                sentence_length_words=25,
                concepts_per_session=6,
                multimedia_preferences=["research_papers", "complex_models", "professional_tools"],
                safety_considerations=["professional_ethics", "research_integrity", "advanced_safety"],
                abstract_thinking=True,
                logical_reasoning=True,
                hypothesis_formation=True,
                mathematical_operations=["advanced_calculus", "linear_algebra", "differential_equations"],
                scientific_method_understanding=True
            )
        }
    
    def _load_vocabulary_levels(self) -> Dict[str, List[str]]:
        """Load vocabulary lists for different levels."""
        return {
            "basic_500": [
                "big", "small", "hot", "cold", "fast", "slow", "up", "down", "in", "out",
                "red", "blue", "green", "yellow", "round", "square", "animal", "plant",
                "water", "air", "sun", "moon", "day", "night", "happy", "sad"
            ],
            "elementary_2000": [
                "observe", "experiment", "measure", "compare", "classify", "predict",
                "energy", "force", "motion", "matter", "solid", "liquid", "gas",
                "living", "nonliving", "habitat", "food chain", "weather", "climate"
            ],
            "middle_school_5000": [
                "hypothesis", "variable", "data", "analysis", "conclusion", "theory",
                "molecule", "atom", "element", "compound", "reaction", "ecosystem",
                "adaptation", "evolution", "gravity", "magnetism", "electricity"
            ],
            "high_school_8000": [
                "photosynthesis", "cellular_respiration", "genetics", "DNA", "RNA",
                "metabolism", "homeostasis", "thermodynamics", "electromagnetic",
                "quantum", "relativity", "calculus", "derivative", "integral"
            ],
            "advanced_15000": [
                "transcription", "translation", "epigenetics", "proteomics", "bioinformatics",
                "nanotechnology", "biotechnology", "artificial_intelligence", "machine_learning",
                "computational_biology", "systems_biology", "synthetic_biology"
            ]
        }
    
    def _build_concept_hierarchies(self) -> Dict[str, Dict[str, List[str]]]:
        """Build hierarchical concept maps for progressive learning."""
        return {
            "matter": {
                AgeGroup.EARLY_YEARS.value: ["solid", "liquid", "gas"],
                AgeGroup.ELEMENTARY.value: ["states_of_matter", "properties", "changes"],
                AgeGroup.MIDDLE_SCHOOL.value: ["molecules", "atoms", "particle_theory"],
                AgeGroup.HIGH_SCHOOL.value: ["atomic_structure", "chemical_bonds", "periodic_table"],
                AgeGroup.HIGHER_ED.value: ["quantum_mechanics", "molecular_orbitals", "spectroscopy"]
            },
            "life": {
                AgeGroup.EARLY_YEARS.value: ["animals", "plants", "growth"],
                AgeGroup.ELEMENTARY.value: ["living_things", "needs", "habitats"],
                AgeGroup.MIDDLE_SCHOOL.value: ["cells", "organs", "systems"],
                AgeGroup.HIGH_SCHOOL.value: ["genetics", "evolution", "ecology"],
                AgeGroup.HIGHER_ED.value: ["molecular_biology", "biotechnology", "genomics"]
            },
            "energy": {
                AgeGroup.EARLY_YEARS.value: ["movement", "heat", "light"],
                AgeGroup.ELEMENTARY.value: ["forms_of_energy", "sources", "uses"],
                AgeGroup.MIDDLE_SCHOOL.value: ["energy_transfer", "conservation", "efficiency"],
                AgeGroup.HIGH_SCHOOL.value: ["thermodynamics", "mechanical_energy", "electromagnetic"],
                AgeGroup.HIGHER_ED.value: ["quantum_energy", "relativity", "field_theory"]
            }
        }
    
    def _initialize_safety_filters(self) -> Dict[AgeGroup, List[str]]:
        """Initialize safety filters for different age groups."""
        return {
            AgeGroup.EARLY_YEARS: [
                "dangerous", "toxic", "sharp", "hot", "electrical", "chemical",
                "explosive", "radiation", "microscopic", "bacteria", "virus"
            ],
            AgeGroup.ELEMENTARY: [
                "toxic", "corrosive", "explosive", "radiation", "high_voltage",
                "biohazard", "carcinogenic", "mutagenic"
            ],
            AgeGroup.MIDDLE_SCHOOL: [
                "highly_toxic", "explosive", "radioactive", "biohazard_level_3",
                "carcinogenic", "mutagenic", "teratogenic"
            ],
            AgeGroup.HIGH_SCHOOL: [
                "extremely_toxic", "explosive", "radioactive", "biohazard_level_4"
            ],
            AgeGroup.HIGHER_ED: []  # No restrictions for advanced learners
        }
    
    async def adapt_content(self, content: ContentItem, target_age: AgeGroup) -> ContentItem:
        """Main method to adapt content for a specific age group."""
        profile = self.age_profiles[target_age]
        
        # Apply content adaptation pipeline
        adapted_content = await self._apply_adaptation_pipeline(content, profile)
        
        return ContentItem(
            id=f"{content.id}_{target_age.value}",
            title=await self._adapt_title(content.title, profile),
            content=adapted_content,
            content_type=content.content_type,
            domain=content.domain,
            age_groups=[target_age],
            sources=content.sources,
            created_at=content.created_at,
            updated_at=datetime.now(),
            version=content.version,
            tags=await self._adapt_tags(content.tags, profile),
            prerequisites=await self._adapt_prerequisites(content.prerequisites, target_age),
            related_concepts=await self._adapt_related_concepts(content.related_concepts, target_age),
            multimedia_assets=await self._adapt_multimedia(content.multimedia_assets, profile)
        )
    
    async def _apply_adaptation_pipeline(self, content: ContentItem, profile: AgeGroupProfile) -> str:
        """Apply the complete adaptation pipeline."""
        text = content.content
        
        # Step 1: Safety filtering
        text = await self._apply_safety_filter(text, profile.age_group)
        
        # Step 2: Vocabulary simplification
        text = await self._simplify_vocabulary(text, profile.vocabulary_level)
        
        # Step 3: Sentence structure adaptation
        text = await self._adapt_sentence_structure(text, profile.sentence_length_words)
        
        # Step 4: Content length adjustment
        text = await self._adjust_content_length(text, profile.content_length_words)
        
        # Step 5: Add age-appropriate examples
        text = await self._add_age_appropriate_examples(text, profile)
        
        # Step 6: Add interactive elements
        text = await self._add_interactive_elements(text, profile)
        
        # Step 7: Structure for attention span
        text = await self._structure_for_attention_span(text, profile.attention_span_minutes)
        
        return text
    
    async def _apply_safety_filter(self, text: str, age_group: AgeGroup) -> str:
        """Remove or modify unsafe content for the age group."""
        safety_words = self.safety_filters.get(age_group, [])
        
        for word in safety_words:
            if word.lower() in text.lower():
                if age_group == AgeGroup.EARLY_YEARS:
                    # Remove dangerous concepts entirely
                    sentences = text.split('.')
                    filtered_sentences = [s for s in sentences if word.lower() not in s.lower()]
                    text = '. '.join(filtered_sentences)
                else:
                    # Add safety warnings
                    text = text.replace(word, f"{word} (⚠️ Safety Note: Requires adult supervision)")
        
        return text
    
    async def _simplify_vocabulary(self, text: str, vocabulary_level: str) -> str:
        """Replace complex words with simpler alternatives."""
        vocabulary = self.vocabulary_levels.get(vocabulary_level, [])
        
        # Complex to simple word mappings
        word_replacements = {
            "utilize": "use",
            "demonstrate": "show",
            "investigate": "look at",
            "hypothesis": "guess",
            "experiment": "test",
            "observe": "watch",
            "phenomenon": "thing that happens",
            "characteristics": "features",
            "composition": "what it's made of",
            "transformation": "change",
            "subsequently": "then",
            "consequently": "so",
            "furthermore": "also",
            "nevertheless": "but"
        }
        
        if vocabulary_level in ["basic_500", "elementary_2000"]:
            for complex_word, simple_word in word_replacements.items():
                text = re.sub(r'\b' + complex_word + r'\b', simple_word, text, flags=re.IGNORECASE)
        
        return text
    
    async def _adapt_sentence_structure(self, text: str, max_sentence_length: int) -> str:
        """Break down complex sentences into simpler ones."""
        sentences = text.split('.')
        adapted_sentences = []
        
        for sentence in sentences:
            words = sentence.strip().split()
            
            if len(words) <= max_sentence_length:
                adapted_sentences.append(sentence.strip())
            else:
                # Break long sentences at conjunctions
                conjunctions = [' and ', ' but ', ' because ', ' when ', ' where ', ' which ']
                broken = False
                
                for conj in conjunctions:
                    if conj in sentence:
                        parts = sentence.split(conj, 1)
                        adapted_sentences.append(parts[0].strip())
                        adapted_sentences.append(parts[1].strip())
                        broken = True
                        break
                
                if not broken:
                    # If can't break at conjunction, truncate and add continuation
                    adapted_sentences.append(' '.join(words[:max_sentence_length]) + '...')
        
        return '. '.join(adapted_sentences)
    
    async def _adjust_content_length(self, text: str, length_range: Tuple[int, int]) -> str:
        """Adjust content to fit within the appropriate length range."""
        words = text.split()
        min_words, max_words = length_range
        
        if len(words) < min_words:
            # Add age-appropriate elaboration
            text += "\n\n## Want to Learn More?\nThis is a very interesting topic! "
            text += "Ask an adult to help you explore more about this."
        
        elif len(words) > max_words:
            # Truncate and create summary
            truncated = ' '.join(words[:max_words])
            text = truncated + "\n\n## Summary\nThis topic has many exciting parts to discover!"
        
        return text
    
    async def _add_age_appropriate_examples(self, text: str, profile: AgeGroupProfile) -> str:
        """Add examples appropriate for the age group."""
        examples = {
            AgeGroup.EARLY_YEARS: {
                "energy": "Like when you run fast, you use energy from your food!",
                "matter": "Ice is cold and hard, water is wet, and steam is like a cloud!",
                "force": "When you push a toy car, you use force to make it move!"
            },
            AgeGroup.ELEMENTARY: {
                "energy": "A battery stores energy to make your flashlight work.",
                "matter": "Ice cubes melt into water when they get warm.",
                "force": "A magnet can pull metal objects without touching them."
            },
            AgeGroup.MIDDLE_SCHOOL: {
                "energy": "Solar panels convert sunlight into electrical energy.",
                "matter": "Water molecules move faster when heated, changing from liquid to gas.",
                "force": "Friction between your shoes and the ground helps you walk."
            }
        }
        
        if profile.age_group in examples:
            age_examples = examples[profile.age_group]
            
            for concept, example in age_examples.items():
                if concept.lower() in text.lower():
                    text += f"\n\n### Example\n{example}"
        
        return text
    
    async def _add_interactive_elements(self, text: str, profile: AgeGroupProfile) -> str:
        """Add interactive elements based on learning preferences."""
        interactive_additions = []
        
        if LearningStyle.KINESTHETIC in profile.preferred_learning_styles:
            interactive_additions.append("## Try This!\nGet up and move around while thinking about this concept!")
        
        if LearningStyle.VISUAL in profile.preferred_learning_styles:
            interactive_additions.append("## Visualize It!\nDraw a picture of what you just learned!")
        
        if LearningStyle.AUDITORY in profile.preferred_learning_styles:
            interactive_additions.append("## Say It Out Loud!\nExplain this concept to someone else!")
        
        if interactive_additions:
            text += "\n\n" + "\n\n".join(interactive_additions)
        
        return text
    
    async def _structure_for_attention_span(self, text: str, attention_span: int) -> str:
        """Structure content to match attention span."""
        if attention_span <= 10:  # Short attention span
            # Add frequent breaks and engagement points
            paragraphs = text.split('\n\n')
            structured_paragraphs = []
            
            for i, paragraph in enumerate(paragraphs):
                structured_paragraphs.append(paragraph)
                
                if (i + 1) % 2 == 0:  # Every 2 paragraphs
                    structured_paragraphs.append("---\n*Take a moment to think about what you just learned!*\n---")
            
            text = '\n\n'.join(structured_paragraphs)
        
        return text
    
    async def _adapt_title(self, title: str, profile: AgeGroupProfile) -> str:
        """Adapt title for age group."""
        if profile.age_group == AgeGroup.EARLY_YEARS:
            # Make titles more engaging and simple
            if "Introduction to" in title:
                title = title.replace("Introduction to", "Let's Learn About")
            title = "🌟 " + title + "!"
        
        elif profile.age_group == AgeGroup.ELEMENTARY:
            title = "🔍 " + title
        
        return title
    
    async def _adapt_tags(self, tags: List[str], profile: AgeGroupProfile) -> List[str]:
        """Adapt tags for age group."""
        adapted_tags = []
        vocabulary = self.vocabulary_levels.get(profile.vocabulary_level, [])
        
        for tag in tags:
            if profile.vocabulary_level in ["basic_500", "elementary_2000"]:
                # Simplify complex tags
                simple_tag = tag.replace("_", " ").title()
                adapted_tags.append(simple_tag)
            else:
                adapted_tags.append(tag)
        
        # Add age-specific tags
        adapted_tags.append(f"age_{profile.age_group.value}")
        adapted_tags.append(profile.cognitive_stage.value)
        
        return adapted_tags
    
    async def _adapt_prerequisites(self, prerequisites: List[str], target_age: AgeGroup) -> List[str]:
        """Adapt prerequisites based on age group capabilities."""
        profile = self.age_profiles[target_age]
        adapted_prerequisites = []
        
        for prereq in prerequisites:
            # Check if prerequisite is age-appropriate
            if profile.abstract_thinking or "abstract" not in prereq.lower():
                if profile.mathematical_operations:
                    # Check if math prerequisite is within capabilities
                    math_concepts = ["algebra", "calculus", "geometry", "statistics"]
                    if any(concept in prereq.lower() for concept in math_concepts):
                        if any(concept in profile.mathematical_operations for concept in math_concepts):
                            adapted_prerequisites.append(prereq)
                    else:
                        adapted_prerequisites.append(prereq)
                else:
                    # Non-math prerequisite
                    adapted_prerequisites.append(prereq)
        
        # Add age-appropriate foundational prerequisites
        if target_age == AgeGroup.EARLY_YEARS:
            adapted_prerequisites = ["adult_supervision", "basic_observation"]
        elif target_age == AgeGroup.ELEMENTARY:
            adapted_prerequisites.extend(["reading_skills", "basic_math"])
        
        return list(set(adapted_prerequisites))
    
    async def _adapt_related_concepts(self, related_concepts: List[str], target_age: AgeGroup) -> List[str]:
        """Adapt related concepts using concept hierarchies."""
        adapted_concepts = []
        
        for concept in related_concepts:
            # Find concept in hierarchies
            for base_concept, hierarchy in self.concept_hierarchies.items():
                if concept.lower() in base_concept.lower() or base_concept.lower() in concept.lower():
                    age_appropriate_concepts = hierarchy.get(target_age.value, [])
                    adapted_concepts.extend(age_appropriate_concepts)
                else:
                    adapted_concepts.append(concept)
        
        return list(set(adapted_concepts))
    
    async def _adapt_multimedia(self, multimedia_assets: List[str], profile: AgeGroupProfile) -> List[str]:
        """Adapt multimedia assets for age group."""
        adapted_assets = []
        
        for asset in multimedia_assets:
            if asset in profile.multimedia_preferences:
                adapted_assets.append(asset)
        
        # Add preferred multimedia for this age group
        adapted_assets.extend(profile.multimedia_preferences)
        
        return list(set(adapted_assets))
    
    def get_age_profile(self, age_group: AgeGroup) -> AgeGroupProfile:
        """Get the profile for a specific age group."""
        return self.age_profiles[age_group]
    
    def assess_content_appropriateness(self, content: ContentItem, target_age: AgeGroup) -> Dict[str, float]:
        """Assess how appropriate content is for a target age group."""
        profile = self.age_profiles[target_age]
        
        # Vocabulary assessment
        vocabulary_score = self._assess_vocabulary_complexity(content.content, profile.vocabulary_level)
        
        # Length assessment
        word_count = len(content.content.split())
        min_words, max_words = profile.content_length_words
        length_score = 1.0 if min_words <= word_count <= max_words else 0.5
        
        # Safety assessment
        safety_score = self._assess_safety(content.content, target_age)
        
        # Concept complexity assessment
        concept_score = self._assess_concept_complexity(content, profile)
        
        return {
            "vocabulary_appropriateness": vocabulary_score,
            "length_appropriateness": length_score,
            "safety_score": safety_score,
            "concept_complexity": concept_score,
            "overall_appropriateness": (vocabulary_score + length_score + safety_score + concept_score) / 4
        }
    
    def _assess_vocabulary_complexity(self, text: str, vocabulary_level: str) -> float:
        """Assess vocabulary complexity for age group."""
        vocabulary = self.vocabulary_levels.get(vocabulary_level, [])
        words = text.lower().split()
        
        complex_words = 0
        for word in words:
            if len(word) > 10 and word not in vocabulary:  # Simple heuristic
                complex_words += 1
        
        complexity_ratio = complex_words / max(1, len(words))
        return max(0.0, 1.0 - complexity_ratio * 5)  # Lower score for higher complexity
    
    def _assess_safety(self, text: str, age_group: AgeGroup) -> float:
        """Assess safety of content for age group."""
        safety_words = self.safety_filters.get(age_group, [])
        
        for word in safety_words:
            if word.lower() in text.lower():
                return 0.3  # Low safety score if dangerous content detected
        
        return 1.0  # High safety score if no dangerous content
    
    def _assess_concept_complexity(self, content: ContentItem, profile: AgeGroupProfile) -> float:
        """Assess concept complexity for age group capabilities."""
        score = 1.0
        
        # Check abstract thinking requirements
        if not profile.abstract_thinking:
            abstract_indicators = ["theory", "hypothesis", "abstract", "conceptual"]
            if any(indicator in content.content.lower() for indicator in abstract_indicators):
                score -= 0.3
        
        # Check mathematical requirements
        math_indicators = ["equation", "formula", "calculate", "algebra", "calculus"]
        content_math_level = sum(1 for indicator in math_indicators if indicator in content.content.lower())
        
        if content_math_level > len(profile.mathematical_operations):
            score -= 0.2
        
        return max(0.0, score)


# Example usage and testing
def main():
    """Example usage of the age adaptation system."""
    adaptation_engine = AgeAdaptationEngine()
    
    # Example content to adapt
    sample_content = ContentItem(
        id="sample_001",
        title="Introduction to Photosynthesis",
        content="""
        Photosynthesis is a complex biochemical process by which plants, algae, and certain bacteria 
        convert light energy, usually from the sun, into chemical energy stored in glucose molecules. 
        This process involves two main stages: the light-dependent reactions and the Calvin cycle. 
        During the light-dependent reactions, chlorophyll molecules absorb photons and initiate 
        a series of electron transfer reactions that produce ATP and NADPH. Subsequently, the 
        Calvin cycle utilizes these energy-rich molecules to fix carbon dioxide into organic compounds.
        """,
        content_type="theory",
        domain="biology",
        age_groups=[AgeGroup.HIGH_SCHOOL],
        sources=["biology_textbook"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        version=1,
        tags=["photosynthesis", "biology", "plants", "energy"],
        prerequisites=["cell_structure", "chemistry_basics"],
        related_concepts=["cellular_respiration", "chloroplast", "glucose"]
    )
    
    # Test adaptation for different age groups
    for age_group in AgeGroup:
        print(f"\n--- Adapting for {age_group.value} ---")
        
        # Assess appropriateness first
        appropriateness = adaptation_engine.assess_content_appropriateness(sample_content, age_group)
        print(f"Appropriateness scores: {appropriateness}")
        
        # Get age profile
        profile = adaptation_engine.get_age_profile(age_group)
        print(f"Profile: {age_group.value}")
        print(f"- Attention span: {profile.attention_span_minutes} minutes")
        print(f"- Vocabulary level: {profile.vocabulary_level}")
        print(f"- Content length: {profile.content_length_words} words")
        print(f"- Abstract thinking: {profile.abstract_thinking}")
        
        # Note: In actual implementation, we would call:
        # adapted_content = await adaptation_engine.adapt_content(sample_content, age_group)
        # print(f"Adapted content: {adapted_content.content[:200]}...")


if __name__ == "__main__":
    main()