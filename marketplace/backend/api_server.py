"""
STEAM Marketplace - Flask API Server

RESTful API server for the global educational marketplace providing
endpoints for content management, user management, payments, and analytics.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

from marketplace_manager import marketplace_manager
from marketplace_models import (
    ContentType, ContentCategory, AgeGroup, DifficultyLevel, 
    PricingModel, ContentStatus, MARKETPLACE_CONFIG
)

# Initialize Flask app
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key-here'  # Change in production
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = MARKETPLACE_CONFIG['max_file_size_mb'] * 1024 * 1024

# Initialize extensions
CORS(app)
jwt = JWTManager(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Authentication Endpoints
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new creator account"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'display_name', 'profile_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Hash password
        password_hash = generate_password_hash(data['password'])
        
        # Prepare creator data
        creator_data = {
            'username': data['username'],
            'email': data['email'],
            'display_name': data['display_name'],
            'profile_type': data['profile_type'],
            'institution': data.get('institution', ''),
            'country': data.get('country', ''),
            'bio': data.get('bio', ''),
            'specializations': data.get('specializations', [])
        }
        
        # Create creator
        creator = marketplace_manager.create_creator(creator_data)
        
        # Create access token
        access_token = create_access_token(identity=creator.creator_id)
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'access_token': access_token,
            'creator': {
                'creator_id': creator.creator_id,
                'username': creator.username,
                'display_name': creator.display_name,
                'profile_type': creator.profile_type,
                'token_balance': creator.token_balance
            }
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login with username/email and password"""
    try:
        data = request.get_json()
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Find creator by username or email
        creator = marketplace_manager.get_creator_by_username(username)
        
        if not creator or not check_password_hash(creator.password_hash, password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create access token
        access_token = create_access_token(identity=creator.creator_id)
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'creator': {
                'creator_id': creator.creator_id,
                'username': creator.username,
                'display_name': creator.display_name,
                'profile_type': creator.profile_type,
                'token_balance': creator.token_balance,
                'wallet_balance': creator.wallet_balance
            }
        })
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

# Creator Management Endpoints
@app.route('/api/creators/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user's profile"""
    try:
        creator_id = get_jwt_identity()
        creator = marketplace_manager.get_creator(creator_id)
        
        if not creator:
            return jsonify({'error': 'Creator not found'}), 404
        
        return jsonify({
            'success': True,
            'creator': {
                'creator_id': creator.creator_id,
                'username': creator.username,
                'display_name': creator.display_name,
                'email': creator.email,
                'profile_type': creator.profile_type,
                'institution': creator.institution,
                'country': creator.country,
                'bio': creator.bio,
                'specializations': creator.specializations,
                'verified': creator.verified,
                'created_at': creator.created_at.isoformat(),
                'rating': creator.rating,
                'total_sales': creator.total_sales,
                'total_downloads': creator.total_downloads,
                'total_revenue': creator.total_revenue,
                'follower_count': creator.follower_count,
                'content_count': creator.content_count,
                'badges': creator.badges,
                'achievements': creator.achievements,
                'wallet_balance': creator.wallet_balance,
                'token_balance': creator.token_balance
            }
        })
        
    except Exception as e:
        logger.error(f"Profile fetch error: {e}")
        return jsonify({'error': 'Failed to fetch profile'}), 500

@app.route('/api/creators/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user's profile"""
    try:
        creator_id = get_jwt_identity()
        creator = marketplace_manager.get_creator(creator_id)
        
        if not creator:
            return jsonify({'error': 'Creator not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        updatable_fields = ['display_name', 'bio', 'institution', 'country', 'specializations']
        for field in updatable_fields:
            if field in data:
                setattr(creator, field, data[field])
        
        marketplace_manager._update_creator(creator)
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500

# Content Management Endpoints
@app.route('/api/content', methods=['POST'])
@jwt_required()
def create_content():
    """Create new educational content"""
    try:
        creator_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'content_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Prepare content data
        content_data = {
            'creator_id': creator_id,
            'title': data['title'],
            'description': data['description'],
            'content_type': ContentType(data['content_type']),
            'categories': [ContentCategory(cat) for cat in data.get('categories', [])],
            'age_groups': [AgeGroup(age) for age in data.get('age_groups', [])],
            'difficulty_level': DifficultyLevel(data.get('difficulty_level', 'beginner')),
            'duration_minutes': data.get('duration_minutes', 60),
            'learning_objectives': data.get('learning_objectives', []),
            'educational_frameworks': data.get('educational_frameworks', []),
            'requirements': data.get('requirements', []),
            'tools_needed': data.get('tools_needed', []),
            'programming_languages': data.get('programming_languages', []),
            'robotics_kits': data.get('robotics_kits', []),
            'pricing_model': PricingModel(data.get('pricing_model', 'free')),
            'price_usd': data.get('price_usd', 0.0),
            'token_price': data.get('token_price', 0),
            'tags': data.get('tags', []),
            'language': data.get('language', 'en')
        }
        
        # Create content
        content = marketplace_manager.create_content(content_data)
        
        return jsonify({
            'success': True,
            'message': 'Content created successfully',
            'content_id': content.content_id
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Content creation error: {e}")
        return jsonify({'error': 'Failed to create content'}), 500

@app.route('/api/content/search', methods=['GET'])
def search_content():
    """Search for educational content"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category')
        age_group = request.args.get('age_group')
        difficulty = request.args.get('difficulty')
        pricing_model = request.args.get('pricing_model')
        max_price = request.args.get('max_price', type=float)
        
        # Build filters
        filters = {}
        if category:
            filters['category'] = category
        if age_group:
            filters['age_group'] = age_group
        if difficulty:
            filters['difficulty'] = difficulty
        if pricing_model:
            filters['pricing_model'] = pricing_model
        if max_price is not None:
            filters['max_price'] = max_price
        
        # Search content
        content_items = marketplace_manager.search_content(query, filters)
        
        # Convert to JSON-serializable format
        results = []
        for content in content_items:
            results.append({
                'content_id': content.content_id,
                'title': content.title,
                'description': content.description,
                'content_type': content.content_type.value,
                'categories': [cat.value for cat in content.categories],
                'age_groups': [age.value for age in content.age_groups],
                'difficulty_level': content.difficulty_level.value,
                'duration_minutes': content.duration_minutes,
                'pricing_model': content.pricing_model.value,
                'price_usd': content.price_usd,
                'token_price': content.token_price,
                'rating': content.rating,
                'review_count': content.review_count,
                'download_count': content.download_count,
                'preview_images': content.preview_images,
                'demo_video_url': content.demo_video_url,
                'tags': content.tags,
                'created_at': content.created_at.isoformat() if content.created_at else None
            })
        
        return jsonify({
            'success': True,
            'results': results,
            'total_count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Content search error: {e}")
        return jsonify({'error': 'Search failed'}), 500

@app.route('/api/content/<content_id>', methods=['GET'])
def get_content_details():
    """Get detailed information about specific content"""
    try:
        content = marketplace_manager.get_content(content_id)
        
        if not content:
            return jsonify({'error': 'Content not found'}), 404
        
        # Increment view count
        content.view_count += 1
        marketplace_manager._update_content(content)
        
        # Get creator information
        creator = marketplace_manager.get_creator(content.creator_id)
        
        return jsonify({
            'success': True,
            'content': {
                'content_id': content.content_id,
                'title': content.title,
                'description': content.description,
                'content_type': content.content_type.value,
                'categories': [cat.value for cat in content.categories],
                'age_groups': [age.value for age in content.age_groups],
                'difficulty_level': content.difficulty_level.value,
                'duration_minutes': content.duration_minutes,
                'learning_objectives': content.learning_objectives,
                'educational_frameworks': content.educational_frameworks,
                'requirements': content.requirements,
                'tools_needed': content.tools_needed,
                'programming_languages': content.programming_languages,
                'robotics_kits': content.robotics_kits,
                'pricing_model': content.pricing_model.value,
                'price_usd': content.price_usd,
                'token_price': content.token_price,
                'rating': content.rating,
                'review_count': content.review_count,
                'download_count': content.download_count,
                'view_count': content.view_count,
                'preview_images': content.preview_images,
                'demo_video_url': content.demo_video_url,
                'tags': content.tags,
                'language': content.language,
                'created_at': content.created_at.isoformat() if content.created_at else None,
                'creator': {
                    'creator_id': creator.creator_id,
                    'display_name': creator.display_name,
                    'username': creator.username,
                    'profile_type': creator.profile_type,
                    'institution': creator.institution,
                    'country': creator.country,
                    'rating': creator.rating,
                    'verified': creator.verified
                } if creator else None
            }
        })
        
    except Exception as e:
        logger.error(f"Content details error: {e}")
        return jsonify({'error': 'Failed to fetch content details'}), 500

@app.route('/api/content/trending', methods=['GET'])
def get_trending_content():
    """Get trending educational content"""
    try:
        limit = request.args.get('limit', 20, type=int)
        trending_content = marketplace_manager.get_trending_content(limit)
        
        results = []
        for content in trending_content:
            creator = marketplace_manager.get_creator(content.creator_id)
            results.append({
                'content_id': content.content_id,
                'title': content.title,
                'description': content.description[:200] + '...' if len(content.description) > 200 else content.description,
                'content_type': content.content_type.value,
                'categories': [cat.value for cat in content.categories],
                'difficulty_level': content.difficulty_level.value,
                'pricing_model': content.pricing_model.value,
                'price_usd': content.price_usd,
                'token_price': content.token_price,
                'rating': content.rating,
                'download_count': content.download_count,
                'preview_images': content.preview_images[:1],  # Just the first image
                'creator_name': creator.display_name if creator else 'Unknown',
                'created_at': content.created_at.isoformat() if content.created_at else None
            })
        
        return jsonify({
            'success': True,
            'trending_content': results
        })
        
    except Exception as e:
        logger.error(f"Trending content error: {e}")
        return jsonify({'error': 'Failed to fetch trending content'}), 500

# Purchase and Payment Endpoints
@app.route('/api/content/<content_id>/purchase', methods=['POST'])
@jwt_required()
def purchase_content():
    """Purchase educational content"""
    try:
        buyer_id = get_jwt_identity()
        data = request.get_json()
        payment_method = data.get('payment_method', 'tokens')
        
        # Process purchase
        purchase = marketplace_manager.process_purchase(buyer_id, content_id, payment_method)
        
        return jsonify({
            'success': True,
            'message': 'Purchase completed successfully',
            'purchase_id': purchase.purchase_id,
            'download_url': f'/api/content/{content_id}/download'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Purchase error: {e}")
        return jsonify({'error': 'Purchase failed'}), 500

@app.route('/api/tokens/balance', methods=['GET'])
@jwt_required()
def get_token_balance():
    """Get current user's token balance"""
    try:
        creator_id = get_jwt_identity()
        creator = marketplace_manager.get_creator(creator_id)
        
        if not creator:
            return jsonify({'error': 'Creator not found'}), 404
        
        return jsonify({
            'success': True,
            'token_balance': creator.token_balance,
            'wallet_balance': creator.wallet_balance
        })
        
    except Exception as e:
        logger.error(f"Token balance error: {e}")
        return jsonify({'error': 'Failed to fetch balance'}), 500

@app.route('/api/tokens/purchase', methods=['POST'])
@jwt_required()
def purchase_tokens():
    """Purchase tokens with real money"""
    try:
        creator_id = get_jwt_identity()
        data = request.get_json()
        
        token_amount = data.get('token_amount', 0)
        payment_method = data.get('payment_method', 'credit_card')
        
        if token_amount <= 0:
            return jsonify({'error': 'Invalid token amount'}), 400
        
        # Calculate cost
        cost_usd = token_amount * MARKETPLACE_CONFIG['token_to_usd_rate']
        
        # Process payment (simplified - implement Stripe integration)
        # In production, this would handle actual payment processing
        
        # Add tokens to user account
        creator = marketplace_manager.get_creator(creator_id)
        creator.token_balance += token_amount
        marketplace_manager._update_creator(creator)
        
        # Create transaction record
        marketplace_manager._create_token_transaction(
            creator_id, "purchase", token_amount,
            f"Purchased {token_amount} tokens for ${cost_usd:.2f}"
        )
        
        return jsonify({
            'success': True,
            'message': f'Successfully purchased {token_amount} tokens',
            'new_balance': creator.token_balance,
            'cost_usd': cost_usd
        })
        
    except Exception as e:
        logger.error(f"Token purchase error: {e}")
        return jsonify({'error': 'Token purchase failed'}), 500

# Analytics Endpoints
@app.route('/api/analytics/marketplace', methods=['GET'])
def get_marketplace_analytics():
    """Get overall marketplace analytics"""
    try:
        analytics = marketplace_manager.generate_marketplace_analytics()
        
        return jsonify({
            'success': True,
            'analytics': {
                'date': analytics.date.isoformat(),
                'total_content_items': analytics.total_content_items,
                'new_content_today': analytics.new_content_today,
                'total_creators': analytics.total_creators,
                'new_creators_today': analytics.new_creators_today,
                'total_revenue': analytics.total_revenue,
                'revenue_today': analytics.revenue_today,
                'total_downloads': analytics.total_downloads,
                'average_rating': analytics.average_rating
            }
        })
        
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return jsonify({'error': 'Failed to fetch analytics'}), 500

@app.route('/api/analytics/creator', methods=['GET'])
@jwt_required()
def get_creator_analytics():
    """Get analytics for current creator"""
    try:
        creator_id = get_jwt_identity()
        creator = marketplace_manager.get_creator(creator_id)
        
        if not creator:
            return jsonify({'error': 'Creator not found'}), 404
        
        # Get creator's content performance
        creator_content = marketplace_manager.get_creator_content(creator_id)
        
        total_views = sum(content.view_count for content in creator_content)
        total_downloads = sum(content.download_count for content in creator_content)
        total_revenue = creator.total_revenue
        average_rating = sum(content.rating for content in creator_content if content.rating > 0) / len([c for c in creator_content if c.rating > 0]) if creator_content else 0
        
        return jsonify({
            'success': True,
            'analytics': {
                'total_content': len(creator_content),
                'total_views': total_views,
                'total_downloads': total_downloads,
                'total_sales': creator.total_sales,
                'total_revenue': total_revenue,
                'average_rating': round(average_rating, 2),
                'token_balance': creator.token_balance,
                'wallet_balance': creator.wallet_balance,
                'follower_count': creator.follower_count
            }
        })
        
    except Exception as e:
        logger.error(f"Creator analytics error: {e}")
        return jsonify({'error': 'Failed to fetch creator analytics'}), 500

# File Upload Endpoints
@app.route('/api/content/<content_id>/upload', methods=['POST'])
@jwt_required()
def upload_content_file():
    """Upload files for educational content"""
    try:
        creator_id = get_jwt_identity()
        
        # Verify content ownership
        content = marketplace_manager.get_content(content_id)
        if not content or content.creator_id != creator_id:
            return jsonify({'error': 'Content not found or unauthorized'}), 403
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if file_extension not in MARKETPLACE_CONFIG['allowed_file_types']:
            return jsonify({'error': f'File type not allowed: {file_extension}'}), 400
        
        # Save file
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], content_id)
        os.makedirs(upload_path, exist_ok=True)
        
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        
        # Update content record
        if not content.content_files:
            content.content_files = []
        
        content.content_files.append({
            'filename': filename,
            'original_name': file.filename,
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'upload_date': datetime.now().isoformat()
        })
        
        marketplace_manager._update_content(content)
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'filename': filename
        })
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        return jsonify({'error': 'File upload failed'}), 500

# Utility Endpoints
@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all available content categories"""
    return jsonify({
        'success': True,
        'categories': [category.value for category in ContentCategory],
        'content_types': [content_type.value for content_type in ContentType],
        'age_groups': [age_group.value for age_group in AgeGroup],
        'difficulty_levels': [difficulty.value for difficulty in DifficultyLevel],
        'pricing_models': [pricing.value for pricing in PricingModel]
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting STEAM Marketplace API Server...")
    app.run(host='0.0.0.0', port=5001, debug=True)