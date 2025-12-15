# Capstone-Project: SmartFridge - Smart Recipe Recommendation System

**Find recipes based on what you actually have in your fridge!**

SmartFridge is a full-stack web application that helps you discover recipes you can make with your available ingredients. Built with a focus on software engineering best practices, featuring CQRS+EDA architecture, user authentication, and a distinctive vintage recipe card aesthetic.

---

## Features

### Core Functionality
- **Ingredient-Based Search** - Find recipes by ingredients you have on hand
- **Match Percentages** - See how close you are to making each recipe
- **Smart Shopping Suggestions** - Get recommendations for ingredients that unlock the most new recipes
- **Fuzzy Matching** - Handles typos and variations in ingredient names
- **Dietary Filtering** - Automatic filtering based on dietary restrictions (vegan, vegetarian, gluten-free, etc.)

### User Features
- **User Accounts** - Secure authentication with session management
- **Personal Pantry** - Save your ingredients for quick recipe searches
- **Favorites** - Bookmark your favorite recipes
- **Kitchen Equipment** - Track your appliances for equipment-based filtering
- **Analytics** - View your search history and usage statistics

### Advanced Features
- **Ingredient Substitutions** - Get dietary-appropriate alternatives
- **Cooking Terms Glossary** - Look up culinary terminology
- **Nutritional Information** - Complete nutrition facts with automatic recalculation for substitutions
- **Step-by-Step Cooking Mode** - Follow recipes with timed instructions
- **Vintage Aesthetic** - Beautiful recipe card design inspired by classic cookbooks

---

## Architecture

### Design Pattern
**CQRS + Event-Driven Architecture (CQRS+EDA)**

- **Command Side**: Handles write operations (add ingredient, favorite recipe, etc.)
- **Query Side**: Optimized read models for fast recipe searches
- **Event Bus**: Decouples components via domain events (USER_CREATED, INGREDIENT_ADDED, etc.)
- **Event Consumers**: Update read models and analytics in response to events

### Technology Stack

**Frontend:**
- HTML5, CSS3, JavaScript (Vanilla)
- Vintage-inspired UI design
- GitHub Pages deployment

**Backend:**
- Python 3.12+ with Flask
- PostgreSQL 14+ for data persistence
- psycopg2 for database connectivity
- Flask-CORS for cross-origin requests

**Testing:**
- pytest for unit and integration tests
- unittest.mock for test isolation
- Comprehensive test coverage (API endpoints, query handlers, suggestion engine)

**Development:**
- GitHub Codespaces for cloud development environment
- Git for version control
- Agile methodology with user stories and EPICs

---

## Prerequisites

- **Python**: 3.12 or higher
- **PostgreSQL**: 14 or higher
- **pip**: Python package manager
- **Git**: Version control
- **GitHub Codespaces**: Recommended development environment

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/leazb2/Capstone-Project.git
cd Capstone-Project
```

### 2. Set Up PostgreSQL Database

Run the setup script:

```bash
chmod +x setup_postgres.sh
./setup_postgres.sh
```

This script will:
- ✅ Install PostgreSQL (if needed)
- ✅ Configure authentication for local connections
- ✅ Create the `smartfridge` database
- ✅ Initialize schema from `database/schema.sql`
- ✅ Migrate recipe data from `recipes.json`
- ✅ Create `.env` configuration file
- ✅ Verify installation

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the Application

```bash
./start.sh
```

The backend API will start on the port shown in your Codespaces environment (typically forwarded to a public URL).

### 5. Access the Application

**Frontend:** Visit your GitHub Pages URL (usually `https://klb4mv-a11y.github.io/Capstone-Project`)

**Backend Health Check:** Access your Codespaces forwarded port URL + `/health`

---

## Detailed Setup Instructions

### Manual PostgreSQL Setup (Alternative)

If you prefer manual setup or the script fails:

#### Install PostgreSQL
```bash
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib
sudo service postgresql start
```

#### Create Database
```bash
sudo -u postgres psql -c "CREATE DATABASE smartfridge;"
```

#### Initialize Schema
```bash
sudo -u postgres psql -d smartfridge -f database/schema.sql
```

#### Run Data Migration
```bash
python3 -m database.migrate
```

#### Verify Installation
```bash
sudo -u postgres psql -d smartfridge -c "SELECT COUNT(*) FROM recipe;"
```
Expected output: `35` recipes

### Environment Configuration

Create a `.env` file in the project root:

```env
# SmartFridge Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smartfridge
DB_USER=postgres
DB_PASSWORD=

# Flask Configuration
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development
```
---

## Usage

### Creating an Account

1. Navigate to the application URL
2. Click "Sign Up"
3. Enter username and password
4. Click "Create Account"

### Searching for Recipes

**Method 1: Quick Search**
1. Enter ingredients in the search box (comma-separated)
2. Click "Find Recipes"
3. View matching recipes with match percentages

**Method 2: Using Your Pantry**
1. Log in to your account
2. Go to "My Pantry"
3. Add ingredients you have
4. Click "Search with My Pantry"
5. View recipes you can make

### Getting Shopping Suggestions

1. Enter current ingredients
2. Click "Shopping Suggestions"
3. See which ingredients would unlock the most new recipes
4. View "almost there" recipes (50%+ match)

### Managing Favorites

1. Click the ⭐ icon on any recipe
2. Access favorites from "My Favorites" menu
3. See match percentage with current pantry

### Using Dietary Filters

1. Go to "Profile Settings"
2. Select dietary restrictions (vegan, vegetarian, gluten-free, etc.)
3. Recipes will automatically filter based on your restrictions
4. Incompatible recipes shown separately with violation reasons

---

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Categories
```bash
# API endpoint tests
pytest tests/test_api_endpoints.py -v

# Query handler tests
pytest tests/test_query_handlers.py -v

# Suggestion engine tests
pytest tests/test_suggestion_engine.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

### Test Configuration
Tests use mocked database operations for isolation and speed. See `pytest.ini` for configuration.

---

## 📁 Project Structure

```
SmartFridge/
├── api.py                          # Main Flask application
├── start.sh                        # Application startup script
├── setup_and_fix_postgres.sh      # Database setup script
├── requirements.txt                # Python dependencies
├── pytest.ini                      # Test configuration
├── .env                            # Environment variables (create from template)
│
├── commands/                       # CQRS Command Side
│   ├── command_handlers.py         # Write operation handlers
│   └── auth_handlers.py            # Authentication commands
│
├── queries/                        # CQRS Query Side
│   └── query_handlers.py           # Read operation handlers
│
├── consumers/                      # Event Consumers
│   └── event_consumers.py          # Event handlers for read model updates
│
├── services/                       # Business Logic
│   ├── recipe_matcher.py           # Recipe matching algorithm
│   ├── suggestion_engine.py        # Shopping suggestion logic
│   ├── substitutions.py            # Ingredient substitution service
│   └── cooking_terms.py            # Culinary glossary
│
├── database/                       # Database Layer
│   ├── db_connection.py            # PostgreSQL connection pooling
│   ├── init_db.py                  # Database initialization
│   ├── schema.sql                  # Database schema definition
│   ├── migrate.py                  # Data migration script
│
├── frontend/                       # Web Interface
│   ├── index.html                  # Main application page
│
├── tests/                          # Test Suite
│   ├── test_api_endpoints.py       
│   ├── test_query_handlers.py      
│   └── test_suggestion_engine.py   
│   └── test_command_handlers.py   
│   └── test_dietary_restrictions.py
│   └── test_recipe_matcher.py
│   └── test_substitutions.py
│
└── docs/                           # Documentation
    ├── User_Stories_and_EPICS.docx
    ├── Requirement_Analysis_Diagrams.docx
    └── COMPSCI4090Project_Description.pdf
```

---

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - Login to account
- `POST /api/auth/logout` - Logout current user
- `GET /api/auth/session` - Check authentication status

### Recipe Search
- `POST /api/recipes/search` - Search recipes by ingredients
- `GET /api/recipes/:id` - Get recipe details

### User Pantry (Authenticated)
- `GET /api/ingredients` - Get user's pantry
- `POST /api/ingredients` - Add ingredient to pantry
- `DELETE /api/ingredients/:id` - Remove ingredient

### Favorites (Authenticated)
- `GET /api/favorites` - Get user's favorites
- `POST /api/favorites` - Add recipe to favorites
- `DELETE /api/favorites/:id` - Remove from favorites

### Profile (Authenticated)
- `GET /api/profile` - Get user profile
- `PUT /api/profile/dietary-restrictions` - Update dietary restrictions
- `PUT /api/profile/skill-level` - Update cooking skill level

### Shopping Suggestions
- `POST /api/smart-shopping-suggestions` - Get ingredient suggestions

### Substitutions
- `GET /api/substitutions/:ingredient` - Get substitutions for ingredient
- `POST /api/substitutions` - Get substitutions for multiple ingredients

### Cooking Terms
- `GET /api/cooking-terms` - Get all cooking terms
- `GET /api/cooking-terms/:term` - Get specific term definition

### System
- `GET /health` - Health check and feature status
- `GET /api/analytics/system` - System-wide analytics
- `GET /api/analytics/user` - User-specific analytics (Authenticated)

---

## Design Principles

### User Experience
- **Beginner-Friendly**: Clear instructions and cooking term definitions
- **Flexible**: Works with or without authentication
- **Informative**: Match percentages show how close you are
- **Helpful**: Smart suggestions guide shopping decisions

### Software Engineering
- **Separation of Concerns**: CQRS pattern separates reads and writes
- **Event-Driven**: Loose coupling via event bus
- **Testable**: Comprehensive unit and integration tests
- **Scalable**: Connection pooling and optimized queries
- **Maintainable**: Clear code structure and documentation

### Data Integrity
- **Normalized Schema**: Eliminates data redundancy
- **Foreign Keys**: Enforces referential integrity
- **Transactions**: Ensures atomic operations
- **Migrations**: Versioned database changes

---

## Troubleshooting

### PostgreSQL Connection Issues

**Error**: `connection to server failed`

**Solutions**:
1. Ensure PostgreSQL is running: `sudo service postgresql status`
2. Start if needed: `sudo service postgresql start`
3. Re-run setup script: `./setup_and_fix_postgres.sh`

### Database Authentication Issues

**Error**: `authentication failed for user "postgres"`

**Solution**: The fix script handles this automatically, but if needed:
```bash
# Find and edit pg_hba.conf
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Change 'peer' and 'scram-sha-256' to 'trust' for local connections
# Then restart: sudo service postgresql restart
```

### Migration Issues

**Error**: `Recipe data already exists in database`

**Solution**:
```bash
# Drop and recreate database
sudo -u postgres psql -c "DROP DATABASE smartfridge;"
sudo -u postgres psql -c "CREATE DATABASE smartfridge;"
sudo -u postgres psql -d smartfridge -f database/schema.sql
python3 -m database.migrate
```

### Frontend Can't Connect to Backend

**Check**:
1. Backend is running (check terminal)
2. Codespaces port is forwarded (check Ports tab)
3. Frontend `API_BASE_URL` points to forwarded port
4. CORS is enabled in `api.py`

### Import Errors

**Error**: `ModuleNotFoundError`

**Solution**:
```bash
pip install -r requirements.txt
```

---

## Database Schema

### Core Tables
- `users` - User accounts and profiles
- `recipe` - Recipe information
- `ingredient` - Master ingredient list
- `recipe_ingredient` - Recipe-ingredient relationships
- `equipment` - Kitchen equipment catalog

### User Data Tables
- `pantry` - User pantry items
- `favorite` - User favorite recipes
- `user_equipment` - User's kitchen appliances
- `search_log` - Search analytics

---

## Team Members
- Kai Blair
- Luke Angell
- James Miles

---

## Completed Features 
- [x] Ingredient-based recipe search
- [x] User authentication and profiles
- [x] Personal pantries and favorites
- [x] Dietary restriction filtering
- [x] Smart shopping suggestions
- [x] Nutritional information
- [x] Ingredient substitutions
- [x] Cooking terms glossary
- [x] CQRS+EDA architecture
- [x] Comprehensive test suite

---