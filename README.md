# Order Management API


## Technical Stack

* **Backend**: Python 3.11, Flask
* **Database**: PostgreSQL (via SQLAlchemy ORM)
* **Authentication**: JWT Tokens
* **Testing**: Pytest
* **Deployment**: Docker, Docker Compose


## Setup and Installation

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd order-management-api
   ```

2. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

3. Update the environment variables in `.env` if needed.

4. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

5. Initialize the database (first time only):
   ```bash
   docker-compose exec api flask db upgrade
   ```

The API will be available at: http://localhost:5000

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd order-management-api
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file and configure your environment variables.

5. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. Run the development server:
   ```bash
   python3 scripts/run_app.py
   ```

## API Endpoints

### Authentication
- `POST /api/auth/login`: Get JWT token using email
- `GET /api/auth/verify`: Verify JWT token validity

### Users
- `POST /api/users`: Create a new user-waiter
- `GET /api/users`: Get all users (requires auth)
- `GET /api/users/<id>`: Get user by ID (requires auth)

### Orders
- `POST /api/orders`: Create a new order with products (requires auth)
- `GET /api/orders`: Get orders for current user (requires auth)
- `GET /api/orders/<id>`: Get order by ID (requires auth)

### Reports
- `GET /api/reports/products`: Get product sales report (requires auth)
  - Query params: `start_date`, `end_date` (format: YYYY-MM-DD)

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_users.py

# Run with coverage report
pytest --cov=app tests/
```

## Database Schema

- **Users**: Stores User-Waiters information
- **Products**: Stores product catalog
- **Orders**: Stores order information with customer details
- **OrderProducts**: Junction table mapping products to orders with quantity and price