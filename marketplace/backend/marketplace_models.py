"""
STEAM Marketplace - Data Models

Global marketplace for students and teachers to share, sell, and monetize
STEAM educational content including projects, lesson plans, and resources.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime
import uuid

class ContentType(Enum):
    """Types of educational content in the marketplace"""
    PROJECT = "project"
    LESSON_PLAN = "lesson_plan"
    ACTIVITY = "activity"
    ASSESSMENT = "assessment"
    RESOURCE_PACK = "resource_pack"
    CODE_TEMPLATE = "code_template"
    ROBOTICS_GUIDE = "robotics_guide"
    STEAM_KIT = "steam_kit"

class ContentCategory(Enum):
    """Content categories for organization"""
    SCIENCE = "science"
    TECHNOLOGY = "technology"
    ENGINEERING = "engineering"
    ARTS = "arts"
    MATHEMATICS = "mathematics"
    ROBOTICS = "robotics"
    PROGRAMMING = "programming"
    ENVIRONMENTAL = "environmental"
    HEALTH = "health"
    SPACE = "space"

class AgeGroup(Enum):
    """Target age groups"""
    EARLY_CHILDHOOD = "3-5"
    ELEMENTARY = "6-11"
    MIDDLE_SCHOOL = "12-14"
    HIGH_SCHOOL = "15-18"
    ADULT = "18+"

class DifficultyLevel(Enum):
    """Content difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class PricingModel(Enum):
    """Pricing models for content"""
    FREE = "free"
    PAID = "paid"
    TOKEN_BASED = "token_based"
    SUBSCRIPTION = "subscription"
    PAY_PER_USE = "pay_per_use"

class ContentStatus(Enum):
    """Content approval status"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"

@dataclass
class Creator:
    """Content creator profile"""
    creator_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    display_name: str = ""
    email: str = ""
    profile_type: str = "teacher"  # teacher, student, institution, organization
    institution: str = ""
    country: str = ""
    bio: str = ""
    specializations: List[str] = field(default_factory=list)
    verified: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    
    # Reputation and metrics
    rating: float = 0.0
    total_sales: int = 0
    total_downloads: int = 0
    total_revenue: float = 0.0
    follower_count: int = 0
    content_count: int = 0
    
    # Achievements and badges
    badges: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    
    # Payment information
    payment_methods: List[Dict[str, Any]] = field(default_factory=list)
    wallet_balance: float = 0.0
    token_balance: int = 0

@dataclass
class ContentItem:
    """Individual content item in the marketplace"""
    content_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    title: str = ""
    description: str = ""
    content_type: ContentType = ContentType.PROJECT
    categories: List[ContentCategory] = field(default_factory=list)
    
    # Educational metadata
    age_groups: List[AgeGroup] = field(default_factory=list)
    difficulty_level: DifficultyLevel = DifficultyLevel.BEGINNER
    duration_minutes: int = 60
    learning_objectives: List[str] = field(default_factory=list)
    educational_frameworks: List[str] = field(default_factory=list)
    
    # Technical requirements
    requirements: List[str] = field(default_factory=list)
    tools_needed: List[str] = field(default_factory=list)
    programming_languages: List[str] = field(default_factory=list)
    robotics_kits: List[str] = field(default_factory=list)
    
    # Content files and resources
    content_files: List[Dict[str, Any]] = field(default_factory=list)
    preview_images: List[str] = field(default_factory=list)
    demo_video_url: str = ""
    
    # Pricing and monetization
    pricing_model: PricingModel = PricingModel.FREE
    price_usd: float = 0.0
    token_price: int = 0
    discount_percentage: float = 0.0
    
    # Marketplace metadata
    status: ContentStatus = ContentStatus.DRAFT
    featured: bool = False
    tags: List[str] = field(default_factory=list)
    language: str = "en"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    published_at: Optional[datetime] = None
    
    # Analytics and performance
    view_count: int = 0
    download_count: int = 0
    purchase_count: int = 0
    rating: float = 0.0
    review_count: int = 0
    favorite_count: int = 0
    
    # SEO and discoverability
    seo_keywords: List[str] = field(default_factory=list)
    search_tags: List[str] = field(default_factory=list)

@dataclass
class Review:
    """User review for content"""
    review_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    reviewer_id: str = ""
    rating: int = 5  # 1-5 stars
    title: str = ""
    comment: str = ""
    helpful_votes: int = 0
    verified_purchase: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class Purchase:
    """Purchase transaction record"""
    purchase_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    buyer_id: str = ""
    content_id: str = ""
    creator_id: str = ""
    
    # Transaction details
    payment_method: str = "credit_card"  # credit_card, paypal, tokens, cryptocurrency
    amount_paid: float = 0.0
    currency: str = "USD"
    tokens_used: int = 0
    
    # Transaction status
    status: str = "completed"  # pending, completed, failed, refunded
    transaction_date: datetime = field(default_factory=datetime.now)
    
    # Revenue sharing
    creator_revenue: float = 0.0
    platform_fee: float = 0.0
    processing_fee: float = 0.0

@dataclass
class Collection:
    """Curated collection of content"""
    collection_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    title: str = ""
    description: str = ""
    content_items: List[str] = field(default_factory=list)  # content_ids
    featured: bool = False
    public: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    view_count: int = 0

@dataclass
class TokenTransaction:
    """Token-based transaction record"""
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    transaction_type: str = "purchase"  # purchase, earn, spend, transfer
    token_amount: int = 0
    description: str = ""
    related_content_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    balance_after: int = 0

@dataclass
class MarketplaceAnalytics:
    """Analytics data for the marketplace"""
    date: datetime = field(default_factory=datetime.now)
    
    # Content metrics
    total_content_items: int = 0
    new_content_today: int = 0
    top_categories: List[Dict[str, Any]] = field(default_factory=list)
    
    # User metrics
    total_creators: int = 0
    active_creators: int = 0
    new_creators_today: int = 0
    
    # Financial metrics
    total_revenue: float = 0.0
    revenue_today: float = 0.0
    token_transactions_today: int = 0
    
    # Engagement metrics
    total_downloads: int = 0
    downloads_today: int = 0
    average_rating: float = 0.0
    reviews_today: int = 0

@dataclass
class EducationalFramework:
    """Educational framework metadata"""
    framework_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    standards: List[Dict[str, Any]] = field(default_factory=list)
    age_ranges: List[str] = field(default_factory=list)
    subjects: List[str] = field(default_factory=list)
    country: str = ""
    official_url: str = ""

@dataclass
class QualityAssurance:
    """Quality assurance review for content"""
    qa_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    reviewer_id: str = ""
    review_date: datetime = field(default_factory=datetime.now)
    
    # Quality checks
    educational_accuracy: bool = False
    age_appropriateness: bool = False
    safety_compliance: bool = False
    technical_functionality: bool = False
    
    # Feedback
    feedback: str = ""
    improvements_needed: List[str] = field(default_factory=list)
    approval_status: str = "pending"  # pending, approved, rejected
    
    # Scoring
    overall_score: float = 0.0
    individual_scores: Dict[str, float] = field(default_factory=dict)

# Global marketplace configuration
MARKETPLACE_CONFIG = {
    "platform_fee_percentage": 15.0,  # Platform takes 15% of sales
    "payment_processing_fee": 2.9,    # Payment processor fee
    "token_to_usd_rate": 0.01,        # 1 token = $0.01
    "free_token_allowance": 100,      # Free tokens for new users
    "minimum_payout": 25.0,           # Minimum payout threshold
    "supported_currencies": ["USD", "EUR", "GBP", "CAD", "AUD", "JPY"],
    "supported_languages": ["en", "es", "fr", "de", "zh", "ja", "ko", "pt", "ru", "ar"],
    "max_file_size_mb": 500,          # Maximum file size for uploads
    "allowed_file_types": [
        "pdf", "docx", "pptx", "zip", "py", "ipynb", 
        "mp4", "mov", "avi", "jpg", "png", "gif"
    ]
}