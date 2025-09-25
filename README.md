# E-commerce Monorepo

A full-stack e-commerce application built with Next.js and Django, containerized with Docker.

## Architecture

- **Frontend**: Next.js 15 with TypeScript, Tailwind CSS, and App Router
- **Backend**: Django 5 with Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **Email**: MailHog (development)
- **Reverse Proxy**: Nginx
- **Package Manager**: PNPM with workspaces

## Project Structure

```
ecommerce/
├── apps/
│   ├── web/          # Next.js frontend
│   └── api/          # Django backend
├── .github/
│   └── workflows/    # GitHub Actions CI
├── docker-compose.yml
├── nginx.conf
└── package.json      # Root package.json with workspaces
```

## Development Setup

### Prerequisites

- Docker and Docker Compose
- PNPM (for local development)

### Running the Application

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd ecommerce
   ```

2. Start all services:

   ```bash
   docker compose up --build
   ```

3. Access the application:
   - Web app: http://localhost:3000
   - API: http://localhost:8000
   - Admin: http://localhost:8000/admin
   - MailHog: http://localhost:8025

### Services

- **Web App**: Next.js development server with hot reload
- **API**: Django development server with auto-reload
- **Database**: PostgreSQL with persistent data
- **Cache**: Redis for session storage and caching
- **Email**: MailHog for email testing
- **Nginx**: Reverse proxy for production-like setup

## Development Commands

### Root Level (Monorepo)

```bash
# Install all dependencies
pnpm install

# Run linting
pnpm lint

# Run formatting
pnpm format

# Run type checking
pnpm typecheck

# Build all packages
pnpm build

# Run all tests
pnpm test
```

### Web App

```bash
cd apps/web

# Install dependencies
pnpm install

# Start development server
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start
```

### API

```bash
cd apps/api

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

## Environment Variables

### Web App

- `NEXT_PUBLIC_API_URL`: API base URL (default: http://localhost:8000)

### API

- `DEBUG`: Debug mode (default: True)
- `SECRET_KEY`: Django secret key
- `DB_HOST`: Database host (default: localhost)
- `DB_NAME`: Database name (default: ecommerce)
- `DB_USER`: Database user (default: postgres)
- `DB_PASSWORD`: Database password (default: postgres)
- `DB_PORT`: Database port (default: 5432)

## CI/CD

The project includes GitHub Actions workflows for:

- Linting and formatting checks
- TypeScript type checking
- Building all packages
- Running tests
- Python tests

## Contributing

1. Follow conventional commit messages
2. Run `pnpm lint` and `pnpm format` before committing
3. Ensure all tests pass
4. Update documentation as needed

## License

MIT
