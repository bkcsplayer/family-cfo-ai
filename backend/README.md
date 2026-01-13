# Family CFO Backend

FastAPI backend for the Family CFO Dashboard application.

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

### Running with Docker

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Start all services:**
   ```bash
   docker-compose up --build
   ```

3. **Access the API:**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Local Development

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```

## Database Models

- **User**: Authentication and role-based access
- **Transaction**: Financial transactions with AI matching
- **Asset**: Real estate, vehicles, stocks
- **Subscription**: Recurring payments
- **CanadianAccount**: TFSA, RRSP, RESP, FHSA
- **InsurancePolicy**: Auto, home, life, health insurance

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check with DB connectivity
- `GET /api/info` - API information

## Environment Variables

See `.env.example` for required configuration.
