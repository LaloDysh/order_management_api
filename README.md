# Order Management API

A RESTful API for managing restaurant orders, waiters, and sales reporting. Built with Flask and designed for high traffic and scalability.

## Features

* User-Waiter management
* Order creation with product management
* Sales reporting with filtering and sorting
* JWT Authentication
* RESTful API design
* Optimized database queries
* Containerized deployment with Docker

## Technical Stack

* **Backend**: Python 3.11, Flask
* **Database**: PostgreSQL (via SQLAlchemy ORM)
* **Authentication**: JWT Tokens
* **Testing**: Pytest
* **Deployment**: Docker, Docker Compose

## Project Structure

The project follows a modular architecture:

- `app/`: Main application package
  - `models/`: Database models
  - `api/`: API routes and controllers
  - `utils/`: Helper functions and utilities
- `tests/`: Unit and integration tests
- `migrations/`: Database migrations

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
   flask run
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

## Performance Considerations

- Database indexes on frequently queried fields
- Pagination for listing endpoints
- Optimized queries for reports
- Connection pooling for database access
- Proper error handling and transaction management

## Architecture Decisions

### Authentication
JWT tokens are used for authentication, providing a stateless mechanism for API protection. This choice facilitates horizontal scaling and improves performance by eliminating the need for session storage.

### Database Design
The relational schema is optimized for ACID transactions and data integrity, with proper indexes for high-traffic queries. Products are reused across orders to maintain data consistency.

### Code Organization
The code follows a modular approach with clear separation of concerns:
- Models for database interaction
- API modules for request handling
- Utilities for shared functionality

This structure enhances maintainability and testability while facilitating future expansion.