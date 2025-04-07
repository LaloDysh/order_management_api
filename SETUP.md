## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Docker and Docker Compose (for containerized deployment)
- Git

## Development Environment Setup

### 1. Database Setup

#### Option A: Local PostgreSQL Installation

1. Install PostgreSQL:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   
   # macOS (using Homebrew)
   brew install postgresql
   ```

2. Start PostgreSQL service:
   ```bash
   # Ubuntu/Debian
   sudo service postgresql start
   
   # macOS
   brew services start postgresql
   ```

3. Create database and user:
   ```bash
   sudo -u postgres psql
   ```

   In the PostgreSQL prompt:
   ```sql
   CREATE DATABASE order_management;
   CREATE USER order_user WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE order_management TO order_user;
   \q
   ```

#### Option B: Docker PostgreSQL (simpler)

```bash
docker run --name postgres-order-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=order_management -p 5432:5432 -d postgres:14
```

### 2. Application Setup

1. Clone the repository and navigate to the project directory:
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

4. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file to set your database URI and other configuration options.

6. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

7. Run the development server:
   ```bash
   flask run
   ```

## Docker Deployment

### 1. One-command Setup

```bash
docker-compose up -d
```

This command will:
- Build the Docker image for the API
- Create and start a PostgreSQL container
- Create and start an API container
- Set up networking between containers
- Map ports to your host machine

### 2. Initialize the Database (First time only)

```bash
docker-compose exec api flask db upgrade
```

### 3. Viewing Logs

```bash
docker-compose logs -f api
```

## Production Deployment Considerations

For production deployments, consider the following modifications:

1. Update `.env` with production-specific settings:
   - Set `FLASK_ENV=production`
   - Use strong random values for secret keys
   - Configure appropriate database credentials

2. Configure database connection pooling:
   - Add `?pool_size=10&max_overflow=20` to your database URI

3. Set up HTTPS:
   - Use a reverse proxy (Nginx, Traefik) for SSL termination
   - Configure proper CORS settings

4. Add monitoring:
   - Integrate with a monitoring solution (Prometheus, Datadog, etc.)

5. Set up database backups:
   - Implement automated PostgreSQL backups

## Database Migrations for Schema Updates

After making changes to models, create and apply migrations:

```bash
# Generate migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade
```
