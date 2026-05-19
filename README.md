# Allsome Orders Analytics

A full-stack application that processes an orders dataset and produces useful analytics including total revenue and best-selling SKU identification.

## Tech Stack

- **Frontend:** React
- **Backend:** Django REST Framework (Python)
- **Database:** MySQL
- **Containerization:** Docker & Docker Compose
- **Infrastructure:** Terraform (AWS EC2)
- **CI/CD:** GitHub Actions

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                      AWS EC2 Instance                     │
│                                                          │
│  ┌─────────┐     ┌──────────────────────────────────┐   │
│  │  Nginx  │────▶│        Docker Compose             │   │
│  │  :80    │     │                                    │   │
│  └─────────┘     │  ┌──────────┐    ┌────────────┐  │   │
│                   │  │ Frontend │    │  Backend   │  │   │
│       /  ────────▶│  │ React    │    │  Django    │  │   │
│                   │  │ :3000    │    │  DRF :8000 │  │   │
│      /api/ ──────▶│  └──────────┘    └─────┬──────┘  │   │
│                   │                        │         │   │
│                   │                  ┌─────▼──────┐  │   │
│                   │                  │   MySQL    │  │   │
│                   │                  │   :3306    │  │   │
│                   │                  └────────────┘  │   │
│                   └──────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

**Data Flow:**
```
CSV File ──▶ Upload API ──▶ Parse & Validate ──▶ MySQL DB
                                                     │
Browser ◀── React UI ◀── Analytics API ◀── Django ORM ◀─┘
```

## Project Structure

```
allsome-orders-analytics/
├── .github/workflows/     # GitHub Actions CI/CD pipeline
├── backend/               # Django REST API
├── frontend/              # React UI
├── terraform/             # AWS infrastructure as code
├── data/                  # CSV data files
├── output/                # Generated JSON output
├── docker-compose.yml     # Container orchestration
└── README.md
```

## Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)
- AWS CLI (for deployment)
- Terraform (for infrastructure provisioning)

## Quick Start (Docker)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd allsome-orders-analytics
   ```

2. **Start all services:**
   ```bash
   docker-compose up --build
   ```

3. **Import CSV data:**
   ```bash
   docker-compose exec backend python manage.py import_csv /app/data/allsome_interview_test_orders.csv
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/
   - Analytics endpoint: http://localhost:8000/api/orders/analytics/

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py import_csv ../data/allsome_interview_test_orders.csv
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/orders/` | List all orders |
| POST | `/api/orders/import/` | Import orders from CSV upload |
| GET | `/api/orders/analytics/` | Get revenue and best-selling SKU |

## Analytics Output

The analytics endpoint returns JSON in the following format:

```json
{
  "total_revenue": 610.00,
  "best_selling_sku": {
    "sku": "SKU-A123",
    "total_quantity": 5
  }
}
```

## Running Tests

```bash
# Backend tests
docker-compose exec backend python manage.py test

# Frontend tests
docker-compose exec frontend npm test
```

### Test Coverage

The backend includes **16 unit and integration tests** covering:

| Test Suite | What's Tested |
|------------|---------------|
| `OrderModelTest` | Model properties and string representation |
| `OrderServiceParseCSVTest` | CSV parsing: valid data, missing columns, invalid order_id, empty SKU, negative quantity, invalid price, empty file |
| `OrderServiceAnalyticsTest` | Revenue calculation, best-selling SKU identification, empty database edge case |
| `OrderAPITest` | API endpoints: list orders, analytics response, import with no file, import valid CSV |

Error handling scenarios tested:
- Missing/invalid CSV columns
- Non-numeric `order_id`
- Empty SKU values
- Negative quantities
- Invalid price formats
- Empty CSV files
- Missing file upload

## Deployment (AWS EC2)

### 1. Configure AWS credentials:
```bash
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
```

### 2. Provision infrastructure:
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### 3. Deploy via GitHub Actions:
Push to the `main` branch to trigger the CI/CD pipeline which will:
- Run tests
- Build Docker images
- Deploy to EC2

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_NAME` | MySQL database name | `allsome_orders` |
| `DB_USER` | MySQL username | `allsome` |
| `DB_PASSWORD` | MySQL password | `allsome_pass` |
| `DB_HOST` | MySQL host | `db` |
| `DB_PORT` | MySQL port | `3306` |
| `DJANGO_SECRET_KEY` | Django secret key | (generated) |
| `DJANGO_DEBUG` | Debug mode | `False` |
| `REACT_APP_API_URL` | Backend API URL | `http://localhost:8000` |
