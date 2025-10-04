"""
Content Difficulty Analyzer
Analyzes content complexity using various linguistic and cognitive metrics
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import re
import math
from collections import Counter
import asyncio
from datetime import datetime

from agents.base_agent import ContentItem, AgeGroup


@dataclass
class DifficultyMetrics:
    """Comprehensive difficulty metrics for content analysis."""
    
    # Linguistic metrics
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    average_sentence_length: float
    average_word_length: float
    syllable_complexity: float
    
    # Vocabulary metrics
    unique_word_ratio: float
    academic_word_percentage: float
    technical_term_percentage: float
    
    # Cognitive metrics
    concept_density: float
    abstract_concept_ratio: float
    logical_complexity: float
    
    # Content structure metrics
    paragraph_consistency: float
    information_density: float
    example_ratio: float
    
    # Overall difficulty score (0-100, higher = more difficult)
    overall_difficulty: float
    
    def to_dict(self) -> Dict[str, float]:
        """Convert metrics to dictionary for serialization."""
        return {
            "flesch_reading_ease": self.flesch_reading_ease,
            "flesch_kincaid_grade": self.flesch_kincaid_grade,
            "average_sentence_length": self.average_sentence_length,
            "average_word_length": self.average_word_length,
            "syllable_complexity": self.syllable_complexity,
            "unique_word_ratio": self.unique_word_ratio,
            "academic_word_percentage": self.academic_word_percentage,
            "technical_term_percentage": self.technical_term_percentage,
            "concept_density": self.concept_density,
            "abstract_concept_ratio": self.abstract_concept_ratio,
            "logical_complexity": self.logical_complexity,
            "paragraph_consistency": self.paragraph_consistency,
            "information_density": self.information_density,
            "example_ratio": self.example_ratio,
            "overall_difficulty": self.overall_difficulty
        }


class ContentDifficultyAnalyzer:
    """Analyzes content difficulty using multiple linguistic and cognitive measures."""
    
    def __init__(self):
        self.academic_words = self._load_academic_word_list()
        self.technical_terms = self._load_technical_terms()
        self.abstract_concepts = self._load_abstract_concepts()
        self.complexity_indicators = self._load_complexity_indicators()
        
    def _load_academic_word_list(self) -> set:
        """Load academic word list (simplified AWL - Academic Word List)."""
        return {
            "analyze", "approach", "area", "assess", "assume", "authority", "available",
            "benefit", "concept", "conclude", "conduct", "consist", "constitute", "context",
            "contract", "create", "data", "define", "derive", "distribute", "economy",
            "element", "environment", "establish", "estimate", "evaluate", "evidence",
            "examine", "factor", "formula", "function", "identify", "income", "indicate",
            "individual", "interpret", "involve", "issue", "labor", "legal", "legislate",
            "major", "method", "occur", "percent", "period", "policy", "principle",
            "proceed", "process", "require", "research", "respond", "role", "section",
            "significant", "similar", "source", "specific", "structure", "theory",
            "variable", "achieve", "acquire", "administrate", "affect", "appropriate",
            "aspect", "assist", "category", "chapter", "commission", "community",
            "complex", "compute", "conclude", "conduct", "consequently", "construct",
            "consume", "contain", "credit", "culture", "design", "distinct",
            "element", "equation", "equivalent", "evaluate", "feature", "final",
            "focus", "impact", "implement", "imply", "initial", "instance", "institute",
            "invest", "item", "journal", "maintain", "normal", "obtain", "participate",
            "perceive", "positive", "potential", "previous", "primary", "purchase",
            "range", "region", "regulate", "relevant", "reliable", "remove", "resource",
            "restrict", "secure", "seek", "select", "site", "strategy", "survey",
            "text", "tradition", "transfer", "alternative", "circumstance", "comment",
            "compensate", "component", "consent", "considerable", "constant", "constrain",
            "contribute", "convention", "coordinate", "core", "corporate", "correspond",
            "criteria", "deduce", "demonstrate", "document", "dominate", "emphasis",
            "ensure", "exclude", "framework", "fund", "illustrate", "immigrate",
            "implication", "impose", "integrate", "internal", "investigate", "job",
            "label", "mechanism", "obvious", "occupy", "option", "output", "overall",
            "parallel", "parameter", "phase", "predict", "principal", "prior", "professional",
            "project", "promote", "regime", "resolve", "retain", "series", "statistics",
            "status", "stress", "subsequent", "sum", "summary", "undertake", "whereas"
        }
    
    def _load_technical_terms(self) -> Dict[str, set]:
        """Load technical terms by domain."""
        return {
            "science": {
                "molecule", "atom", "electron", "proton", "neutron", "element", "compound",
                "reaction", "catalyst", "enzyme", "protein", "DNA", "RNA", "chromosome",
                "cell", "organism", "species", "evolution", "natural_selection", "ecosystem",
                "biodiversity", "photosynthesis", "respiration", "metabolism", "homeostasis"
            },
            "technology": {
                "algorithm", "database", "software", "hardware", "network", "protocol",
                "encryption", "programming", "debugging", "compilation", "optimization",
                "artificial_intelligence", "machine_learning", "neural_network", "blockchain",
                "cloud_computing", "cybersecurity", "user_interface", "framework", "API"
            },
            "engineering": {
                "circuit", "voltage", "current", "resistance", "capacitor", "transistor",
                "mechanical", "structural", "thermal", "fluid", "dynamics", "statics",
                "materials", "stress", "strain", "load", "beam", "foundation", "design",
                "optimization", "efficiency", "sustainability", "renewable", "automation"
            },
            "mathematics": {
                "derivative", "integral", "calculus", "algebra", "geometry", "trigonometry",
                "statistics", "probability", "matrix", "vector", "function", "equation",
                "theorem", "proof", "lemma", "corollary", "hypothesis", "conjecture",
                "algorithm", "complexity", "optimization", "discrete", "continuous"
            },
            "arts": {
                "composition", "perspective", "color_theory", "texture", "form", "line",
                "balance", "rhythm", "emphasis", "unity", "variety", "proportion",
                "technique", "medium", "genre", "style", "movement", "aesthetic",
                "critique", "analysis", "interpretation", "symbolism", "metaphor"
            }
        }
    
    def _load_abstract_concepts(self) -> set:
        """Load abstract concept indicators."""
        return {
            "concept", "theory", "principle", "philosophy", "ideology", "paradigm",
            "framework", "model", "hypothesis", "assumption", "belief", "value",
            "meaning", "significance", "implication", "consequence", "cause", "effect",
            "relationship", "correlation", "pattern", "trend", "tendency", "potential",
            "possibility", "probability", "likelihood", "uncertainty", "ambiguity",
            "complexity", "simplicity", "abstraction", "generalization", "specialization",
            "categorization", "classification", "hierarchy", "structure", "system",
            "organization", "order", "chaos", "randomness", "determinism", "freedom",
            "necessity", "contingency", "universality", "particularity", "objectivity",
            "subjectivity", "reality", "perception", "consciousness", "awareness"
        }
    
    def _load_complexity_indicators(self) -> Dict[str, List[str]]:
        """Load linguistic complexity indicators."""
        return {
            "conditional": ["if", "unless", "provided that", "assuming", "given that"],
            "causal": ["because", "since", "due to", "as a result", "consequently", "therefore"],
            "contrast": ["however", "nevertheless", "nonetheless", "although", "despite", "whereas"],
            "temporal": ["subsequently", "previously", "simultaneously", "meanwhile", "eventually"],
            "comparative": ["compared to", "in contrast", "similarly", "likewise", "conversely"],
            "modal": ["might", "could", "should", "would", "may", "must", "ought to"],
            "quantitative": ["significantly", "substantially", "considerably", "marginally"],
            "evaluative": ["important", "crucial", "essential", "vital", "critical", "significant"]
        }
    
    async def analyze_difficulty(self, content: ContentItem) -> DifficultyMetrics:
        """Perform comprehensive difficulty analysis of content."""
        text = content.content
        
        # Basic text statistics
        sentences = self._split_sentences(text)
        words = self._split_words(text)
        paragraphs = self._split_paragraphs(text)
        
        # Calculate all metrics
        metrics = DifficultyMetrics(
            flesch_reading_ease=self._calculate_flesch_reading_ease(text),
            flesch_kincaid_grade=self._calculate_flesch_kincaid_grade(text),
            average_sentence_length=self._calculate_average_sentence_length(sentences, words),
            average_word_length=self._calculate_average_word_length(words),
            syllable_complexity=self._calculate_syllable_complexity(words),
            unique_word_ratio=self._calculate_unique_word_ratio(words),
            academic_word_percentage=self._calculate_academic_word_percentage(words),
            technical_term_percentage=self._calculate_technical_term_percentage(words, content.domain),
            concept_density=self._calculate_concept_density(text),
            abstract_concept_ratio=self._calculate_abstract_concept_ratio(words),
            logical_complexity=self._calculate_logical_complexity(text),
            paragraph_consistency=self._calculate_paragraph_consistency(paragraphs),
            information_density=self._calculate_information_density(text),
            example_ratio=self._calculate_example_ratio(text),
            overall_difficulty=0.0  # Will be calculated last
        )
        
        # Calculate overall difficulty
        metrics.overall_difficulty = self._calculate_overall_difficulty(metrics)
        
        return metrics
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting (could be improved with NLP libraries)
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _split_words(self, text: str) -> List[str]:
        """Split text into words."""
        # Remove punctuation and split
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return words
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs."""
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified algorithm)."""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Handle special cases
        if word.endswith('e'):
            syllable_count -= 1
        if syllable_count == 0:
            syllable_count = 1
            
        return syllable_count
    
    def _calculate_flesch_reading_ease(self, text: str) -> float:
        """Calculate Flesch Reading Ease score."""
        sentences = len(self._split_sentences(text))
        words = self._split_words(text)
        word_count = len(words)
        syllable_count = sum(self._count_syllables(word) for word in words)
        
        if sentences == 0 or word_count == 0:
            return 0.0
        
        # Flesch Reading Ease formula
        score = 206.835 - (1.015 * (word_count / sentences)) - (84.6 * (syllable_count / word_count))
        return max(0.0, min(100.0, score))
    
    def _calculate_flesch_kincaid_grade(self, text: str) -> float:
        """Calculate Flesch-Kincaid Grade Level."""
        sentences = len(self._split_sentences(text))
        words = self._split_words(text)
        word_count = len(words)
        syllable_count = sum(self._count_syllables(word) for word in words)
        
        if sentences == 0 or word_count == 0:
            return 0.0
        
        # Flesch-Kincaid Grade Level formula
        grade = (0.39 * (word_count / sentences)) + (11.8 * (syllable_count / word_count)) - 15.59
        return max(0.0, grade)
    
    def _calculate_average_sentence_length(self, sentences: List[str], words: List[str]) -> float:
        """Calculate average sentence length in words."""
        if not sentences:
            return 0.0
        return len(words) / len(sentences)
    
    def _calculate_average_word_length(self, words: List[str]) -> float:
        """Calculate average word length in characters."""
        if not words:
            return 0.0
        return sum(len(word) for word in words) / len(words)
    
    def _calculate_syllable_complexity(self, words: List[str]) -> float:
        """Calculate average syllables per word."""
        if not words:
            return 0.0
        total_syllables = sum(self._count_syllables(word) for word in words)
        return total_syllables / len(words)
    
    def _calculate_unique_word_ratio(self, words: List[str]) -> float:
        """Calculate ratio of unique words to total words."""
        if not words:
            return 0.0
        unique_words = len(set(words))
        return unique_words / len(words)
    
    def _calculate_academic_word_percentage(self, words: List[str]) -> float:
        """Calculate percentage of academic words."""
        if not words:
            return 0.0
        academic_count = sum(1 for word in words if word in self.academic_words)
        return (academic_count / len(words)) * 100
    
    def _calculate_technical_term_percentage(self, words: List[str], domain: str) -> float:
        """Calculate percentage of technical terms for the domain."""
        if not words or domain not in self.technical_terms:
            return 0.0
        
        domain_terms = self.technical_terms[domain]
        technical_count = sum(1 for word in words if word in domain_terms)
        return (technical_count / len(words)) * 100
    
    def _calculate_concept_density(self, text: str) -> float:
        """Calculate density of concepts (nouns and technical terms)."""
        words = self._split_words(text)
        if not words:
            return 0.0
        
        # Simple heuristic: words ending in common noun suffixes
        noun_suffixes = ['tion', 'sion', 'ness', 'ment', 'ity', 'ism', 'ance', 'ence']
        concept_count = 0
        
        for word in words:
            if (any(word.endswith(suffix) for suffix in noun_suffixes) or
                word in self.academic_words or
                any(word in terms for terms in self.technical_terms.values())):
                concept_count += 1
        
        return (concept_count / len(words)) * 100
    
    def _calculate_abstract_concept_ratio(self, words: List[str]) -> float:
        """Calculate ratio of abstract concepts."""
        if not words:
            return 0.0
        
        abstract_count = sum(1 for word in words if word in self.abstract_concepts)
        return (abstract_count / len(words)) * 100
    
    def _calculate_logical_complexity(self, text: str) -> float:
        """Calculate logical complexity based on connectors and structures."""
        complexity_score = 0.0
        text_lower = text.lower()
        
        for category, indicators in self.complexity_indicators.items():
            for indicator in indicators:
                count = text_lower.count(indicator)
                # Weight different types of complexity differently
                if category in ['conditional', 'causal']:
                    complexity_score += count * 2.0  # Higher weight for logical structures
                elif category in ['contrast', 'comparative']:
                    complexity_score += count * 1.5
                else:
                    complexity_score += count * 1.0
        
        # Normalize by text length
        word_count = len(self._split_words(text))
        if word_count > 0:
            complexity_score = (complexity_score / word_count) * 100
        
        return min(100.0, complexity_score)
    
    def _calculate_paragraph_consistency(self, paragraphs: List[str]) -> float:
        """Calculate consistency of paragraph lengths."""
        if len(paragraphs) < 2:
            return 100.0  # Perfect consistency for single paragraph
        
        lengths = [len(self._split_words(p)) for p in paragraphs]
        mean_length = sum(lengths) / len(lengths)
        
        if mean_length == 0:
            return 100.0
        
        # Calculate coefficient of variation
        variance = sum((length - mean_length) ** 2 for length in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        cv = (std_dev / mean_length) * 100
        
        # Convert to consistency score (lower CV = higher consistency)
        consistency = max(0.0, 100.0 - cv)
        return consistency
    
    def _calculate_information_density(self, text: str) -> float:
        """Calculate information density (content words vs function words)."""
        words = self._split_words(text)
        if not words:
            return 0.0
        
        # Common function words (simplified list)
        function_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be',
            'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'can', 'shall', 'must', 'ought'
        }
        
        content_words = sum(1 for word in words if word not in function_words)
        return (content_words / len(words)) * 100
    
    def _calculate_example_ratio(self, text: str) -> float:
        """Calculate ratio of examples and illustrations in text."""
        text_lower = text.lower()
        example_indicators = [
            'for example', 'for instance', 'such as', 'like', 'including',
            'e.g.', 'i.e.', 'namely', 'specifically', 'particularly',
            'consider', 'suppose', 'imagine', 'let\'s say'
        ]
        
        example_count = sum(text_lower.count(indicator) for indicator in example_indicators)
        
        # Also count numbered/bulleted lists as examples
        list_patterns = [r'\n\d+\.', r'\n•', r'\n-', r'\n\*']
        for pattern in list_patterns:
            example_count += len(re.findall(pattern, text))
        
        # Normalize by sentence count
        sentence_count = len(self._split_sentences(text))
        if sentence_count > 0:
            return (example_count / sentence_count) * 100
        
        return 0.0
    
    def _calculate_overall_difficulty(self, metrics: DifficultyMetrics) -> float:
        """Calculate weighted overall difficulty score."""
        # Weight factors for different metrics
        weights = {
            'flesch_reading_ease': -0.15,  # Negative because higher = easier
            'flesch_kincaid_grade': 0.15,
            'average_sentence_length': 0.10,
            'average_word_length': 0.10,
            'syllable_complexity': 0.10,
            'academic_word_percentage': 0.12,
            'technical_term_percentage': 0.08,
            'concept_density': 0.10,
            'abstract_concept_ratio': 0.15,
            'logical_complexity': 0.10,
            'information_density': 0.05,
            'example_ratio': -0.10  # Negative because examples make content easier
        }
        
        # Normalize Flesch Reading Ease (flip scale so higher = more difficult)
        normalized_flesch = 100 - metrics.flesch_reading_ease
        
        # Calculate weighted sum
        difficulty_score = (
            weights['flesch_reading_ease'] * normalized_flesch +
            weights['flesch_kincaid_grade'] * min(metrics.flesch_kincaid_grade, 20) * 5 +  # Scale to 0-100
            weights['average_sentence_length'] * min(metrics.average_sentence_length, 50) * 2 +
            weights['average_word_length'] * min(metrics.average_word_length, 15) * 6.67 +
            weights['syllable_complexity'] * min(metrics.syllable_complexity, 5) * 20 +
            weights['academic_word_percentage'] * metrics.academic_word_percentage +
            weights['technical_term_percentage'] * metrics.technical_term_percentage +
            weights['concept_density'] * metrics.concept_density +
            weights['abstract_concept_ratio'] * metrics.abstract_concept_ratio +
            weights['logical_complexity'] * metrics.logical_complexity +
            weights['information_density'] * metrics.information_density +
            weights['example_ratio'] * metrics.example_ratio
        )
        
        # Ensure score is between 0 and 100
        return max(0.0, min(100.0, difficulty_score))
    
    def get_difficulty_level(self, overall_difficulty: float) -> str:
        """Convert numerical difficulty to descriptive level."""
        if overall_difficulty < 20:
            return "Very Easy"
        elif overall_difficulty < 40:
            return "Easy"
        elif overall_difficulty < 60:
            return "Moderate"
        elif overall_difficulty < 80:
            return "Difficult"
        else:
            return "Very Difficult"
    
    def recommend_age_groups(self, metrics: DifficultyMetrics) -> List[AgeGroup]:
        """Recommend appropriate age groups based on difficulty metrics."""
        recommendations = []
        
        # Use Flesch-Kincaid grade level as primary indicator
        grade_level = metrics.flesch_kincaid_grade
        
        if grade_level <= 2:
            recommendations.append(AgeGroup.EARLY_YEARS)
        if grade_level <= 6:
            recommendations.append(AgeGroup.ELEMENTARY)
        if grade_level <= 9:
            recommendations.append(AgeGroup.MIDDLE_SCHOOL)
        if grade_level <= 13:
            recommendations.append(AgeGroup.HIGH_SCHOOL)
        
        recommendations.append(AgeGroup.HIGHER_ED)  # Always appropriate for higher ed
        
        # Adjust based on other factors
        if metrics.abstract_concept_ratio > 10:
            # Remove early age groups if high abstract content
            recommendations = [age for age in recommendations 
                             if age not in [AgeGroup.EARLY_YEARS, AgeGroup.ELEMENTARY]]
        
        if metrics.technical_term_percentage > 15:
            # Remove early age groups if highly technical
            recommendations = [age for age in recommendations 
                             if age != AgeGroup.EARLY_YEARS]
        
        return recommendations if recommendations else [AgeGroup.HIGHER_ED]
    
    async def batch_analyze(self, contents: List[ContentItem]) -> Dict[str, DifficultyMetrics]:
        """Analyze multiple content items in batch."""
        results = {}
        
        # Use asyncio to process multiple items concurrently
        tasks = [self.analyze_difficulty(content) for content in contents]
        metrics_list = await asyncio.gather(*tasks)
        
        for content, metrics in zip(contents, metrics_list):
            results[content.id] = metrics
        
        return results


# Example usage
def main():
    """Example usage of the content difficulty analyzer."""
    analyzer = ContentDifficultyAnalyzer()
    
    # Sample content for testing
    easy_content = ContentItem(
        id="easy_001",
        title="Plants Need Water",
        content="""
        Plants need water to grow. They drink water through their roots. 
        The water goes up to the leaves. Without water, plants will die.
        We must water our plants every day.
        """,
        content_type="explanation",
        domain="science",
        age_groups=[AgeGroup.EARLY_YEARS],
        sources=["kids_science_book"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        version=1,
        tags=["plants", "water", "growth"],
        prerequisites=[],
        related_concepts=["living_things", "growth"]
    )
    
    complex_content = ContentItem(
        id="complex_001",
        title="Quantum Mechanical Principles in Photosynthesis",
        content="""
        Recent investigations have elucidated the quantum mechanical underpinnings 
        of photosynthetic energy transfer processes. The phenomenon of quantum coherence 
        in biological systems represents a paradigm shift in our understanding of 
        bioenergetics. Specifically, the Fenna-Matthews-Olson complex demonstrates 
        remarkably efficient energy transfer through quantum superposition states, 
        suggesting that biological systems have evolved to exploit quantum mechanical 
        principles for optimal functionality. This coherent energy transfer mechanism 
        involves the simultaneous exploration of multiple pathways, thereby maximizing 
        the probability of successful energy capture and minimizing dissipative losses.
        """,
        content_type="research",
        domain="science",
        age_groups=[AgeGroup.HIGHER_ED],
        sources=["nature_journal"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        version=1,
        tags=["quantum_mechanics", "photosynthesis", "biophysics"],
        prerequisites=["quantum_mechanics", "biochemistry", "statistical_mechanics"],
        related_concepts=["quantum_coherence", "energy_transfer", "biological_systems"]
    )
    
    # Analyze difficulty
    print("=== Easy Content Analysis ===")
    # In actual usage: easy_metrics = await analyzer.analyze_difficulty(easy_content)
    print("Would analyze easy content and show metrics...")
    
    print("\n=== Complex Content Analysis ===")
    # In actual usage: complex_metrics = await analyzer.analyze_difficulty(complex_content)
    print("Would analyze complex content and show metrics...")
    
    # Demonstrate some basic calculations
    print(f"\nDemo: Flesch Reading Ease for easy content: {analyzer._calculate_flesch_reading_ease(easy_content.content):.2f}")
    print(f"Demo: Flesch Reading Ease for complex content: {analyzer._calculate_flesch_reading_ease(complex_content.content):.2f}")


if __name__ == "__main__":
    main()