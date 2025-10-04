"""
STEAM Marketplace - Backend Management System

Comprehensive backend system for managing the global educational marketplace
including content management, user management, payments, and analytics.
"""

import json
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
import logging
from dataclasses import asdict
import sqlite3
from decimal import Decimal

# Optional imports for external services
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    stripe = None

try:
    import boto3
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    boto3 = None

from marketplace_models import (
    Creator, ContentItem, Review, Purchase, Collection, TokenTransaction,
    MarketplaceAnalytics, EducationalFramework, QualityAssurance,
    ContentType, ContentCategory, AgeGroup, DifficultyLevel, 
    PricingModel, ContentStatus, MARKETPLACE_CONFIG
)

class MarketplaceManager:
    """Main marketplace management system"""
    
    def __init__(self, database_path: str = "marketplace.db"):
        """Initialize the marketplace manager"""
        self.database_path = database_path
        self.logger = logging.getLogger('MarketplaceManager')
        self._setup_logging()
        self._initialize_database()
        self._setup_payment_processing()
        self._setup_s3_storage()
        
        # In-memory caches for performance
        self.creators_cache: Dict[str, Creator] = {}
        self.content_cache: Dict[str, ContentItem] = {}
        self.analytics_cache = None
        
        # Load initial data
        self._load_caches()
    
    def _setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('marketplace.log'),
                logging.StreamHandler()
            ]
        )
    
    def _initialize_database(self):
        """Initialize SQLite database with all required tables"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Create tables for all marketplace entities
        tables = [
            """CREATE TABLE IF NOT EXISTS creators (
                creator_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                display_name TEXT,
                email TEXT UNIQUE,
                profile_type TEXT,
                institution TEXT,
                country TEXT,
                bio TEXT,
                specializations TEXT,
                verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                rating REAL DEFAULT 0.0,
                total_sales INTEGER DEFAULT 0,
                total_downloads INTEGER DEFAULT 0,
                total_revenue REAL DEFAULT 0.0,
                follower_count INTEGER DEFAULT 0,
                content_count INTEGER DEFAULT 0,
                badges TEXT,
                achievements TEXT,
                payment_methods TEXT,
                wallet_balance REAL DEFAULT 0.0,
                token_balance INTEGER DEFAULT 100
            )""",
            
            """CREATE TABLE IF NOT EXISTS content_items (
                content_id TEXT PRIMARY KEY,
                creator_id TEXT,
                title TEXT NOT NULL,
                description TEXT,
                content_type TEXT,
                categories TEXT,
                age_groups TEXT,
                difficulty_level TEXT,
                duration_minutes INTEGER,
                learning_objectives TEXT,
                educational_frameworks TEXT,
                requirements TEXT,
                tools_needed TEXT,
                programming_languages TEXT,
                robotics_kits TEXT,
                content_files TEXT,
                preview_images TEXT,
                demo_video_url TEXT,
                pricing_model TEXT,
                price_usd REAL DEFAULT 0.0,
                token_price INTEGER DEFAULT 0,
                discount_percentage REAL DEFAULT 0.0,
                status TEXT DEFAULT 'draft',
                featured BOOLEAN DEFAULT FALSE,
                tags TEXT,
                language TEXT DEFAULT 'en',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                published_at TIMESTAMP,
                view_count INTEGER DEFAULT 0,
                download_count INTEGER DEFAULT 0,
                purchase_count INTEGER DEFAULT 0,
                rating REAL DEFAULT 0.0,
                review_count INTEGER DEFAULT 0,
                favorite_count INTEGER DEFAULT 0,
                seo_keywords TEXT,
                search_tags TEXT,
                FOREIGN KEY (creator_id) REFERENCES creators (creator_id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS reviews (
                review_id TEXT PRIMARY KEY,
                content_id TEXT,
                reviewer_id TEXT,
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                title TEXT,
                comment TEXT,
                helpful_votes INTEGER DEFAULT 0,
                verified_purchase BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (content_id) REFERENCES content_items (content_id),
                FOREIGN KEY (reviewer_id) REFERENCES creators (creator_id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS purchases (
                purchase_id TEXT PRIMARY KEY,
                buyer_id TEXT,
                content_id TEXT,
                creator_id TEXT,
                payment_method TEXT,
                amount_paid REAL,
                currency TEXT DEFAULT 'USD',
                tokens_used INTEGER DEFAULT 0,
                status TEXT DEFAULT 'completed',
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                creator_revenue REAL,
                platform_fee REAL,
                processing_fee REAL,
                FOREIGN KEY (buyer_id) REFERENCES creators (creator_id),
                FOREIGN KEY (content_id) REFERENCES content_items (content_id),
                FOREIGN KEY (creator_id) REFERENCES creators (creator_id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS token_transactions (
                transaction_id TEXT PRIMARY KEY,
                user_id TEXT,
                transaction_type TEXT,
                token_amount INTEGER,
                description TEXT,
                related_content_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                balance_after INTEGER,
                FOREIGN KEY (user_id) REFERENCES creators (creator_id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS collections (
                collection_id TEXT PRIMARY KEY,
                creator_id TEXT,
                title TEXT,
                description TEXT,
                content_items TEXT,
                featured BOOLEAN DEFAULT FALSE,
                public BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                view_count INTEGER DEFAULT 0,
                FOREIGN KEY (creator_id) REFERENCES creators (creator_id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS quality_assurance (
                qa_id TEXT PRIMARY KEY,
                content_id TEXT,
                reviewer_id TEXT,
                review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                educational_accuracy BOOLEAN DEFAULT FALSE,
                age_appropriateness BOOLEAN DEFAULT FALSE,
                safety_compliance BOOLEAN DEFAULT FALSE,
                technical_functionality BOOLEAN DEFAULT FALSE,
                feedback TEXT,
                improvements_needed TEXT,
                approval_status TEXT DEFAULT 'pending',
                overall_score REAL DEFAULT 0.0,
                individual_scores TEXT,
                FOREIGN KEY (content_id) REFERENCES content_items (content_id),
                FOREIGN KEY (reviewer_id) REFERENCES creators (creator_id)
            )"""
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
        
        # Create indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_content_creator ON content_items(creator_id)",
            "CREATE INDEX IF NOT EXISTS idx_content_category ON content_items(categories)",
            "CREATE INDEX IF NOT EXISTS idx_content_status ON content_items(status)",
            "CREATE INDEX IF NOT EXISTS idx_purchases_buyer ON purchases(buyer_id)",
            "CREATE INDEX IF NOT EXISTS idx_purchases_content ON purchases(content_id)",
            "CREATE INDEX IF NOT EXISTS idx_reviews_content ON reviews(content_id)",
            "CREATE INDEX IF NOT EXISTS idx_tokens_user ON token_transactions(user_id)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        conn.close()
        self.logger.info("Database initialized successfully")
    
    def _setup_payment_processing(self):
        """Setup payment processing with Stripe"""
        if not STRIPE_AVAILABLE:
            print("⚠️  Stripe not available - payment processing will be simulated")
            self.payment_processor = None
            return
            
        # Initialize Stripe (in production, load from environment)
        stripe.api_key = "sk_test_..."  # Replace with actual key
        self.payment_processor = stripe
    
    def _setup_s3_storage(self):
        """Setup AWS S3 for file storage"""
        if not AWS_AVAILABLE:
            print("⚠️  AWS not available - using local storage")
            self.s3_client = None
            self.s3_bucket = None
            return
            
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id='your_access_key',  # Load from environment
                aws_secret_access_key='your_secret_key',  # Load from environment
            )
            self.s3_bucket = 'steam-marketplace-content'  # Configure bucket name
        except Exception as e:
            # Fallback to local storage
            print(f"S3 setup failed, using local storage: {e}")
            self.s3_client = None
            self.s3_bucket = None
    
    def _load_caches(self):
        """Load frequently accessed data into memory caches"""
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Load creators cache
        cursor.execute("SELECT * FROM creators LIMIT 1000")
        for row in cursor.fetchall():
            creator_data = dict(row)
            # Convert JSON strings back to lists/dicts
            for field in ['specializations', 'badges', 'achievements', 'payment_methods']:
                if creator_data[field]:
                    creator_data[field] = json.loads(creator_data[field])
                else:
                    creator_data[field] = []
            creator = Creator(**creator_data)
            self.creators_cache[creator.creator_id] = creator
        
        conn.close()
        self.logger.info(f"Loaded {len(self.creators_cache)} creators into cache")
    
    # Creator Management
    def create_creator(self, creator_data: Dict[str, Any]) -> Creator:
        """Create a new content creator"""
        creator = Creator(**creator_data)
        
        # Add welcome tokens
        creator.token_balance = MARKETPLACE_CONFIG['free_token_allowance']
        
        # Store in database
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO creators (
                    creator_id, username, display_name, email, profile_type,
                    institution, country, bio, specializations, token_balance
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                creator.creator_id, creator.username, creator.display_name,
                creator.email, creator.profile_type, creator.institution,
                creator.country, creator.bio, json.dumps(creator.specializations),
                creator.token_balance
            ))
            conn.commit()
            
            # Add to cache
            self.creators_cache[creator.creator_id] = creator
            
            # Create welcome token transaction
            self._create_token_transaction(
                creator.creator_id, "earn", 
                MARKETPLACE_CONFIG['free_token_allowance'],
                "Welcome bonus tokens"
            )
            
            self.logger.info(f"Created new creator: {creator.username}")
            return creator
            
        except sqlite3.IntegrityError as e:
            self.logger.error(f"Creator creation failed: {e}")
            raise ValueError("Username or email already exists")
        finally:
            conn.close()
    
    def get_creator(self, creator_id: str) -> Optional[Creator]:
        """Get creator by ID"""
        if creator_id in self.creators_cache:
            return self.creators_cache[creator_id]
        
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM creators WHERE creator_id = ?", (creator_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            creator_data = dict(row)
            # Convert JSON strings back to lists
            for field in ['specializations', 'badges', 'achievements', 'payment_methods']:
                if creator_data[field]:
                    creator_data[field] = json.loads(creator_data[field])
                else:
                    creator_data[field] = []
            creator = Creator(**creator_data)
            self.creators_cache[creator_id] = creator
            return creator
        
        return None
    
    # Content Management
    def create_content(self, content_data: Dict[str, Any]) -> ContentItem:
        """Create new educational content"""
        content = ContentItem(**content_data)
        
        # Store in database
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO content_items (
                content_id, creator_id, title, description, content_type,
                categories, age_groups, difficulty_level, duration_minutes,
                learning_objectives, educational_frameworks, requirements,
                tools_needed, programming_languages, robotics_kits,
                pricing_model, price_usd, token_price, tags, language
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            content.content_id, content.creator_id, content.title,
            content.description, content.content_type.value,
            json.dumps([cat.value for cat in content.categories]),
            json.dumps([age.value for age in content.age_groups]),
            content.difficulty_level.value, content.duration_minutes,
            json.dumps(content.learning_objectives),
            json.dumps(content.educational_frameworks),
            json.dumps(content.requirements),
            json.dumps(content.tools_needed),
            json.dumps(content.programming_languages),
            json.dumps(content.robotics_kits),
            content.pricing_model.value, content.price_usd,
            content.token_price, json.dumps(content.tags),
            content.language
        ))
        
        conn.commit()
        conn.close()
        
        # Update creator content count
        creator = self.get_creator(content.creator_id)
        if creator:
            creator.content_count += 1
            self._update_creator(creator)
        
        # Add to cache
        self.content_cache[content.content_id] = content
        
        self.logger.info(f"Created new content: {content.title}")
        return content
    
    def search_content(self, query: str = "", filters: Dict[str, Any] = None) -> List[ContentItem]:
        """Search for content with advanced filtering"""
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build search query
        sql = "SELECT * FROM content_items WHERE status = 'approved'"
        params = []
        
        if query:
            sql += " AND (title LIKE ? OR description LIKE ? OR tags LIKE ?)"
            query_param = f"%{query}%"
            params.extend([query_param, query_param, query_param])
        
        if filters:
            if 'category' in filters:
                sql += " AND categories LIKE ?"
                params.append(f"%{filters['category']}%")
            
            if 'age_group' in filters:
                sql += " AND age_groups LIKE ?"
                params.append(f"%{filters['age_group']}%")
            
            if 'difficulty' in filters:
                sql += " AND difficulty_level = ?"
                params.append(filters['difficulty'])
            
            if 'pricing_model' in filters:
                sql += " AND pricing_model = ?"
                params.append(filters['pricing_model'])
            
            if 'max_price' in filters:
                sql += " AND price_usd <= ?"
                params.append(filters['max_price'])
        
        # Add ordering
        sql += " ORDER BY rating DESC, download_count DESC LIMIT 50"
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to ContentItem objects
        content_items = []
        for row in rows:
            content_data = dict(row)
            # Convert JSON strings back to appropriate types
            json_fields = [
                'categories', 'age_groups', 'learning_objectives',
                'educational_frameworks', 'requirements', 'tools_needed',
                'programming_languages', 'robotics_kits', 'tags',
                'content_files', 'preview_images', 'seo_keywords', 'search_tags'
            ]
            
            for field in json_fields:
                if content_data[field]:
                    content_data[field] = json.loads(content_data[field])
                else:
                    content_data[field] = []
            
            # Convert enum strings back to enums
            content_data['content_type'] = ContentType(content_data['content_type'])
            content_data['difficulty_level'] = DifficultyLevel(content_data['difficulty_level'])
            content_data['pricing_model'] = PricingModel(content_data['pricing_model'])
            content_data['status'] = ContentStatus(content_data['status'])
            
            # Convert category and age group strings back to enums
            content_data['categories'] = [ContentCategory(cat) for cat in content_data['categories']]
            content_data['age_groups'] = [AgeGroup(age) for age in content_data['age_groups']]
            
            content = ContentItem(**content_data)
            content_items.append(content)
        
        return content_items
    
    # Purchase and Payment Processing
    def process_purchase(self, buyer_id: str, content_id: str, payment_method: str) -> Purchase:
        """Process a content purchase"""
        content = self.get_content(content_id)
        buyer = self.get_creator(buyer_id)
        creator = self.get_creator(content.creator_id)
        
        if not all([content, buyer, creator]):
            raise ValueError("Invalid buyer, content, or creator")
        
        if content.pricing_model == PricingModel.FREE:
            # Free content - just record the download
            purchase = Purchase(
                buyer_id=buyer_id,
                content_id=content_id,
                creator_id=content.creator_id,
                payment_method="free",
                amount_paid=0.0,
                status="completed"
            )
        
        elif content.pricing_model == PricingModel.TOKEN_BASED:
            # Token-based purchase
            if buyer.token_balance < content.token_price:
                raise ValueError("Insufficient token balance")
            
            # Deduct tokens from buyer
            buyer.token_balance -= content.token_price
            self._update_creator(buyer)
            
            # Add tokens to creator (minus platform fee)
            creator_tokens = int(content.token_price * (1 - MARKETPLACE_CONFIG['platform_fee_percentage'] / 100))
            creator.token_balance += creator_tokens
            self._update_creator(creator)
            
            # Create token transactions
            self._create_token_transaction(buyer_id, "spend", -content.token_price, f"Purchased: {content.title}")
            self._create_token_transaction(content.creator_id, "earn", creator_tokens, f"Sale: {content.title}")
            
            purchase = Purchase(
                buyer_id=buyer_id,
                content_id=content_id,
                creator_id=content.creator_id,
                payment_method="tokens",
                tokens_used=content.token_price,
                status="completed"
            )
        
        elif content.pricing_model == PricingModel.PAID:
            # Cash-based purchase through Stripe
            try:
                # Calculate fees
                platform_fee = content.price_usd * MARKETPLACE_CONFIG['platform_fee_percentage'] / 100
                processing_fee = content.price_usd * MARKETPLACE_CONFIG['payment_processing_fee'] / 100
                creator_revenue = content.price_usd - platform_fee - processing_fee
                
                # Process payment (simplified - in production, handle Stripe webhooks)
                charge = self.payment_processor.Charge.create(
                    amount=int(content.price_usd * 100),  # Stripe uses cents
                    currency='usd',
                    description=f"Purchase of {content.title}",
                    metadata={'buyer_id': buyer_id, 'content_id': content_id}
                )
                
                purchase = Purchase(
                    buyer_id=buyer_id,
                    content_id=content_id,
                    creator_id=content.creator_id,
                    payment_method=payment_method,
                    amount_paid=content.price_usd,
                    creator_revenue=creator_revenue,
                    platform_fee=platform_fee,
                    processing_fee=processing_fee,
                    status="completed"
                )
                
                # Update creator revenue
                creator.total_revenue += creator_revenue
                creator.wallet_balance += creator_revenue
                self._update_creator(creator)
                
            except Exception as e:
                self.logger.error(f"Payment processing failed: {e}")
                raise ValueError("Payment processing failed")
        
        # Store purchase record
        self._store_purchase(purchase)
        
        # Update content and creator metrics
        content.purchase_count += 1
        content.download_count += 1
        creator.total_sales += 1
        
        self._update_content(content)
        self._update_creator(creator)
        
        self.logger.info(f"Purchase completed: {purchase.purchase_id}")
        return purchase
    
    def _create_token_transaction(self, user_id: str, transaction_type: str, 
                                  token_amount: int, description: str, 
                                  related_content_id: str = None):
        """Create a token transaction record"""
        user = self.get_creator(user_id)
        transaction = TokenTransaction(
            user_id=user_id,
            transaction_type=transaction_type,
            token_amount=token_amount,
            description=description,
            related_content_id=related_content_id,
            balance_after=user.token_balance
        )
        
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO token_transactions (
                transaction_id, user_id, transaction_type, token_amount,
                description, related_content_id, balance_after
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            transaction.transaction_id, transaction.user_id,
            transaction.transaction_type, transaction.token_amount,
            transaction.description, transaction.related_content_id,
            transaction.balance_after
        ))
        
        conn.commit()
        conn.close()
    
    # Analytics and Reporting
    def generate_marketplace_analytics(self) -> MarketplaceAnalytics:
        """Generate comprehensive marketplace analytics"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Content metrics
        cursor.execute("SELECT COUNT(*) FROM content_items WHERE status = 'approved'")
        total_content = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM content_items WHERE DATE(created_at) = DATE('now')")
        new_content_today = cursor.fetchone()[0]
        
        # User metrics
        cursor.execute("SELECT COUNT(*) FROM creators")
        total_creators = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM creators WHERE DATE(created_at) = DATE('now')")
        new_creators_today = cursor.fetchone()[0]
        
        # Financial metrics
        cursor.execute("SELECT SUM(amount_paid) FROM purchases WHERE status = 'completed'")
        total_revenue = cursor.fetchone()[0] or 0.0
        
        cursor.execute("SELECT SUM(amount_paid) FROM purchases WHERE DATE(transaction_date) = DATE('now')")
        revenue_today = cursor.fetchone()[0] or 0.0
        
        # Engagement metrics
        cursor.execute("SELECT SUM(download_count) FROM content_items")
        total_downloads = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT AVG(rating) FROM content_items WHERE rating > 0")
        average_rating = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        analytics = MarketplaceAnalytics(
            total_content_items=total_content,
            new_content_today=new_content_today,
            total_creators=total_creators,
            new_creators_today=new_creators_today,
            total_revenue=total_revenue,
            revenue_today=revenue_today,
            total_downloads=total_downloads,
            average_rating=round(average_rating, 2)
        )
        
        self.analytics_cache = analytics
        return analytics
    
    def get_trending_content(self, limit: int = 10) -> List[ContentItem]:
        """Get trending content based on recent activity"""
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Calculate trending score based on recent downloads, views, and ratings
        cursor.execute("""
            SELECT *, 
                   (download_count * 0.4 + view_count * 0.3 + rating * review_count * 0.3) as trend_score
            FROM content_items 
            WHERE status = 'approved' 
            ORDER BY trend_score DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        trending_content = []
        for row in rows:
            content_data = dict(row)
            # Convert data types as needed
            content = self._row_to_content_item(content_data)
            trending_content.append(content)
        
        return trending_content
    
    # Quality Assurance
    def submit_for_review(self, content_id: str) -> bool:
        """Submit content for quality assurance review"""
        content = self.get_content(content_id)
        if not content:
            return False
        
        content.status = ContentStatus.PENDING_REVIEW
        self._update_content(content)
        
        # Notify QA team (implement notification system)
        self.logger.info(f"Content submitted for review: {content.title}")
        return True
    
    def review_content(self, content_id: str, reviewer_id: str, 
                      review_data: Dict[str, Any]) -> QualityAssurance:
        """Conduct quality assurance review"""
        qa_review = QualityAssurance(
            content_id=content_id,
            reviewer_id=reviewer_id,
            **review_data
        )
        
        # Calculate overall score
        scores = [
            qa_review.educational_accuracy,
            qa_review.age_appropriateness,
            qa_review.safety_compliance,
            qa_review.technical_functionality
        ]
        qa_review.overall_score = sum(scores) / len(scores)
        
        # Determine approval status
        if qa_review.overall_score >= 0.8:
            qa_review.approval_status = "approved"
            # Update content status
            content = self.get_content(content_id)
            content.status = ContentStatus.APPROVED
            content.published_at = datetime.now()
            self._update_content(content)
        else:
            qa_review.approval_status = "rejected"
            content = self.get_content(content_id)
            content.status = ContentStatus.REJECTED
            self._update_content(content)
        
        # Store QA review
        self._store_qa_review(qa_review)
        
        return qa_review
    
    # Helper Methods
    def get_content(self, content_id: str) -> Optional[ContentItem]:
        """Get content item by ID"""
        if content_id in self.content_cache:
            return self.content_cache[content_id]
        
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM content_items WHERE content_id = ?", (content_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            content = self._row_to_content_item(dict(row))
            self.content_cache[content_id] = content
            return content
        
        return None
    
    def _row_to_content_item(self, row_data: Dict) -> ContentItem:
        """Convert database row to ContentItem object"""
        # Convert JSON strings back to appropriate types
        json_fields = [
            'categories', 'age_groups', 'learning_objectives',
            'educational_frameworks', 'requirements', 'tools_needed',
            'programming_languages', 'robotics_kits', 'tags'
        ]
        
        for field in json_fields:
            if row_data.get(field):
                row_data[field] = json.loads(row_data[field])
            else:
                row_data[field] = []
        
        # Convert enum strings back to enums
        if 'content_type' in row_data:
            row_data['content_type'] = ContentType(row_data['content_type'])
        if 'difficulty_level' in row_data:
            row_data['difficulty_level'] = DifficultyLevel(row_data['difficulty_level'])
        if 'pricing_model' in row_data:
            row_data['pricing_model'] = PricingModel(row_data['pricing_model'])
        if 'status' in row_data:
            row_data['status'] = ContentStatus(row_data['status'])
        
        # Convert category and age group lists
        if row_data.get('categories'):
            row_data['categories'] = [ContentCategory(cat) for cat in row_data['categories']]
        if row_data.get('age_groups'):
            row_data['age_groups'] = [AgeGroup(age) for age in row_data['age_groups']]
        
        return ContentItem(**row_data)
    
    def _update_creator(self, creator: Creator):
        """Update creator in database and cache"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE creators SET
                display_name = ?, bio = ?, specializations = ?,
                rating = ?, total_sales = ?, total_downloads = ?,
                total_revenue = ?, follower_count = ?, content_count = ?,
                badges = ?, achievements = ?, wallet_balance = ?, token_balance = ?
            WHERE creator_id = ?
        """, (
            creator.display_name, creator.bio, json.dumps(creator.specializations),
            creator.rating, creator.total_sales, creator.total_downloads,
            creator.total_revenue, creator.follower_count, creator.content_count,
            json.dumps(creator.badges), json.dumps(creator.achievements),
            creator.wallet_balance, creator.token_balance, creator.creator_id
        ))
        
        conn.commit()
        conn.close()
        
        # Update cache
        self.creators_cache[creator.creator_id] = creator
    
    def _update_content(self, content: ContentItem):
        """Update content in database and cache"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE content_items SET
                title = ?, description = ?, status = ?,
                view_count = ?, download_count = ?, purchase_count = ?,
                rating = ?, review_count = ?, favorite_count = ?,
                updated_at = ?, published_at = ?
            WHERE content_id = ?
        """, (
            content.title, content.description, content.status.value,
            content.view_count, content.download_count, content.purchase_count,
            content.rating, content.review_count, content.favorite_count,
            datetime.now(), content.published_at, content.content_id
        ))
        
        conn.commit()
        conn.close()
        
        # Update cache
        self.content_cache[content.content_id] = content
    
    def _store_purchase(self, purchase: Purchase):
        """Store purchase record in database"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO purchases (
                purchase_id, buyer_id, content_id, creator_id,
                payment_method, amount_paid, currency, tokens_used,
                status, creator_revenue, platform_fee, processing_fee
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            purchase.purchase_id, purchase.buyer_id, purchase.content_id,
            purchase.creator_id, purchase.payment_method, purchase.amount_paid,
            purchase.currency, purchase.tokens_used, purchase.status,
            purchase.creator_revenue, purchase.platform_fee, purchase.processing_fee
        ))
        
        conn.commit()
        conn.close()
    
    def _store_qa_review(self, qa_review: QualityAssurance):
        """Store quality assurance review in database"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO quality_assurance (
                qa_id, content_id, reviewer_id, educational_accuracy,
                age_appropriateness, safety_compliance, technical_functionality,
                feedback, improvements_needed, approval_status, overall_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            qa_review.qa_id, qa_review.content_id, qa_review.reviewer_id,
            qa_review.educational_accuracy, qa_review.age_appropriateness,
            qa_review.safety_compliance, qa_review.technical_functionality,
            qa_review.feedback, json.dumps(qa_review.improvements_needed),
            qa_review.approval_status, qa_review.overall_score
        ))
        
        conn.commit()
        conn.close()

# Global marketplace instance
marketplace_manager = MarketplaceManager()