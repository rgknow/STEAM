# STEAM Marketplace - Global Educational Content Hub

A comprehensive marketplace platform for educators worldwide to share, sell, and discover innovative STEAM (Science, Technology, Engineering, Arts, Mathematics) educational content.

## 🌟 Features

### For Educators
- **Content Creation**: Upload lesson plans, projects, activities, assessments, and courses
- **Global Reach**: Share content with educators across 120+ countries
- **Monetization**: Earn money or tokens from your educational materials
- **Analytics Dashboard**: Track downloads, ratings, and revenue
- **Quality Assurance**: Content validation and quality scoring system

### For Students & Teachers
- **Vast Library**: Browse thousands of educational resources
- **Smart Search**: Find content by subject, age group, difficulty, and more
- **Multiple Formats**: Lesson plans, hands-on projects, digital activities
- **Flexible Pricing**: Free content, token-based purchases, or cash payments
- **Review System**: Community ratings and feedback

### Platform Features
- **Token Economy**: 1 token = $0.01, 100 free tokens for new users
- **Multi-Currency**: Support for USD, EUR, GBP, CAD, AUD, JPY
- **International**: Multi-language support and global payment processing
- **Educational Frameworks**: Aligned with ISTE, OECD, NGSS, DIGICOMP, NCF 2023
- **Quality Control**: Automated content validation and human review

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Internet connection for package installation

### Installation & Launch

1. **Clone or navigate to the marketplace directory**
   ```bash
   cd marketplace
   ```

2. **Run the launcher (automatically installs dependencies)**
   ```bash
   python launcher.py
   ```

3. **Access the application**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:5001

The launcher will:
- Install required Python packages automatically
- Initialize the SQLite database with sample data
- Start both backend and frontend servers
- Open your browser to the application
- Monitor and restart services if needed

### Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Install dependencies
pip install flask flask-cors flask-jwt-extended werkzeug requests

# Start backend server
cd backend
python api_server.py

# In another terminal, start frontend server
cd frontend
python -m http.server 8080
```

## 📁 Project Structure

```
marketplace/
├── backend/
│   ├── marketplace_models.py      # Data models and schemas
│   ├── marketplace_manager.py     # Core business logic and database management
│   ├── api_server.py             # Flask REST API server
│   └── marketplace.db            # SQLite database (created automatically)
├── frontend/
│   ├── index.html                # Main application interface
│   ├── styles.css               # Complete styling and responsive design
│   └── script.js                # Frontend logic and API integration
├── launcher.py                   # Application launcher and process manager
└── README.md                    # This file
```

## 💡 Usage Guide

### Getting Started
1. **Create Account**: Sign up with your email to get 100 free tokens
2. **Browse Content**: Explore trending educational materials
3. **Search & Filter**: Find content by category, age group, difficulty
4. **Purchase Content**: Use tokens or cash to buy premium materials
5. **Create Content**: Share your own educational resources

### For Content Creators
1. **Profile Setup**: Complete your educator profile
2. **Upload Content**: Use the creation wizard to add your materials
3. **Set Pricing**: Choose free, paid, or freemium pricing models
4. **Monitor Performance**: Track views, downloads, and earnings
5. **Engage Community**: Respond to reviews and feedback

### Token System
- **Earning Tokens**: Receive tokens from content sales
- **Buying Tokens**: Purchase with credit card (bulk discounts available)
- **Using Tokens**: Buy educational content from other creators
- **Conversion**: 1 token = $0.01 USD

## 🛠 Technical Architecture

### Backend (Python/Flask)
- **API Server**: RESTful API with JWT authentication
- **Database**: SQLite with comprehensive data models
- **Payment Processing**: Stripe integration for global payments
- **File Storage**: Local storage with AWS S3 support planned
- **Content Management**: Upload, validation, and quality scoring

### Frontend (HTML/CSS/JavaScript)
- **Responsive Design**: Mobile-first, works on all devices
- **Modern UI**: Clean, intuitive interface inspired by modern platforms
- **Real-time Updates**: Dynamic content loading and notifications
- **Search & Filtering**: Advanced content discovery features

### Database Schema
- **Creators**: User profiles and authentication
- **Content Items**: Educational materials with metadata
- **Purchases**: Transaction history and access control
- **Reviews**: Community feedback and ratings
- **Analytics**: Performance tracking and insights

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Configure external services
STRIPE_SECRET_KEY=your_stripe_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET=your_bucket_name
```

### Marketplace Settings
Edit `marketplace_models.py` to customize:
- Token conversion rates
- Platform fees
- File size limits
- Supported file types
- Payment methods

## 📊 Sample Data

The launcher creates sample data including:
- **3 Sample Creators**: Teachers and content creators from different countries
- **5 Sample Content Items**: 
  - AI-Powered Robotics for Beginners
  - 3D Printing Workshop
  - Math Through Art: Geometric Patterns
  - Climate Change Data Analysis with Python
  - Solar-Powered Car Challenge

## 🌍 Global Features

### Multi-Currency Support
- USD, EUR, GBP, CAD, AUD, JPY
- Automatic currency conversion
- Local payment methods

### Educational Framework Alignment
- **ISTE Standards**: Technology in education
- **OECD Learning Framework**: 21st-century skills
- **NGSS**: Next Generation Science Standards
- **DIGICOMP**: Digital competence framework
- **NCF 2023**: India's National Curriculum Framework

### Content Categories
- Science (Physics, Chemistry, Biology, Earth Science)
- Technology (Programming, Digital Literacy, AI, Robotics)
- Engineering (Design Process, Mechanical, Electrical, Civil)
- Arts (Visual Arts, Music, Design, Creative Writing)
- Mathematics (Algebra, Geometry, Statistics, Calculus)

## 🔒 Security Features

- **JWT Authentication**: Secure user sessions
- **Password Hashing**: Werkzeug secure password storage
- **Input Validation**: Comprehensive data validation
- **File Security**: Safe file upload and storage
- **Payment Security**: PCI-compliant payment processing

## 🚦 API Endpoints

### Authentication
- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - User login
- `GET /api/creators/profile` - Get user profile

### Content Management
- `GET /api/content/search` - Search content
- `GET /api/content/trending` - Get trending content
- `GET /api/content/<id>` - Get content details
- `POST /api/content` - Create new content

### Commerce
- `POST /api/content/<id>/purchase` - Purchase content
- `POST /api/tokens/purchase` - Buy tokens
- `GET /api/tokens/balance` - Check token balance

### Analytics
- `GET /api/analytics/marketplace` - Platform statistics
- `GET /api/analytics/creator` - Creator performance

## 🤝 Contributing

This is a demonstration project showcasing a complete marketplace platform. Key areas for enhancement:

1. **Payment Integration**: Complete Stripe and international payment setup
2. **File Storage**: Implement AWS S3 for scalable file storage
3. **Advanced Search**: Elasticsearch integration for better search
4. **Mobile App**: React Native or Flutter mobile application
5. **AI Features**: Content recommendation and auto-tagging
6. **Internationalization**: Complete multi-language support

## 📞 Support

For questions about this demonstration:
- Check the console output for detailed logs
- Review the database schema in `marketplace_models.py`
- Examine API endpoints in `api_server.py`
- Inspect frontend interactions in `script.js`

## 📜 License

This project is a demonstration of marketplace architecture and educational technology integration. See LICENSE file for details.

## 🎯 Educational Impact

This marketplace platform demonstrates:
- **Global Collaboration**: Connecting educators worldwide
- **Quality Education**: Curated, high-quality educational content
- **Economic Empowerment**: Monetization opportunities for educators
- **Innovation in Learning**: STEAM interdisciplinary approaches
- **Technology Integration**: Modern web technologies for education
- **Sustainable Model**: Token-based economy supporting creators

---

**Built with ❤️ for educators and learners worldwide**