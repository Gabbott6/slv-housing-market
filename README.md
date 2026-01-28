# Salt Lake Valley Housing Market Web Application

A comprehensive web application for the Salt Lake Valley housing market featuring real-time property listings, AI-powered housing code assistance, advanced filtering, and market trend tracking.

## Features

✅ **Real Property Data** - Support for multiple data sources (CSV uploads, RentCast API, manual entry)
✅ **AI-Powered Q&A** - Claude AI integration for housing codes, laws, and regulations
✅ **Accurate Cost Calculations** - Monthly mortgage, taxes, insurance, and HOA calculations
✅ **Smart Rankings** - Sort by monthly cost, total price, seller score, and more
✅ **Market Trend Tracking** - Historical data visualization and analysis
✅ **Source Citations** - Every data point linked to its source
✅ **Direct Listing Links** - One-click access to original property listings

## Tech Stack

**Backend:**
- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- Anthropic Claude API

**Frontend:**
- React 18
- TypeScript
- Vite
- Tailwind CSS
- React Router

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- Docker & Docker Compose (for PostgreSQL and Redis)
- Anthropic API key (for AI features)

## Quick Start

### 1. Clone the Repository

```bash
cd slv-housing-market
```

### 2. Start Database Services

```bash
docker-compose up -d
```

This starts PostgreSQL and Redis containers.

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run the server
python -m uvicorn app.main:app --reload
```

Backend will be available at http://localhost:8000

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at http://localhost:5173

## Configuration

### Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

```env
# Required for AI features
ANTHROPIC_API_KEY=your_api_key_here

# Optional API keys
RENTCAST_API_KEY=your_rentcast_key  # For RentCast data source

# Database (default works with Docker Compose)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/slv_housing

# Mortgage calculation defaults
DEFAULT_DOWN_PAYMENT_PERCENT=20.0
DEFAULT_MORTGAGE_RATE=7.0
DEFAULT_LOAN_TERM_YEARS=30

# Salt Lake County tax rate
SLC_PROPERTY_TAX_RATE=0.0056
```

## Usage

### Adding Property Data

#### Option 1: CSV Upload (Recommended for Getting Started)

1. Navigate to the homepage
2. Click "Upload CSV" button
3. Select a CSV file with the following columns:
   - `address` (required)
   - `price` (required)
   - `city`
   - `beds`
   - `baths`
   - `sqft`
   - `property_type`
   - `hoa_fee`
   - `listing_url`

Example CSV:
```csv
address,city,price,beds,baths,sqft,property_type,hoa_fee,listing_url
123 Main St,Salt Lake City,450000,3,2,1800,Single Family,0,https://example.com/listing1
456 Oak Ave,Provo,325000,2,1,1200,Condo,200,https://example.com/listing2
```

#### Option 2: RentCast API

1. Sign up for RentCast API (50 free calls/month)
2. Add `RENTCAST_API_KEY` to your `.env` file
3. Change `DATA_SOURCE=rentcast` in `.env`
4. Restart the backend

### Using the AI Assistant

1. Navigate to "AI Assistant" page
2. Ask questions about housing codes, regulations, or building requirements
3. Examples:
   - "What are the setback requirements for residential properties in Salt Lake County?"
   - "What is the minimum ceiling height for bedrooms?"
   - "Do I need a permit to build a deck?"

**Note:** The AI assistant requires housing codes to be populated in the database. You can add codes via the API:

```bash
curl -X POST http://localhost:8000/api/ai/codes \
  -H "Content-Type: application/json" \
  -d '{
    "code_section": "15.1.2",
    "title": "Residential Setback Requirements",
    "content": "Residential properties must maintain a minimum setback of...",
    "jurisdiction": "Salt Lake County",
    "source_name": "Municode Library",
    "source_url": "https://example.com/code"
  }'
```

### Filtering and Sorting Properties

Use the filter panel to:
- Set price range (min/max)
- Filter by beds and baths
- Search by city
- Sort by:
  - Best Monthly Cost (total monthly payment)
  - Best Overall Price (purchase price)
  - Best Seller Score (composite metric)
  - Best Price per Square Foot
  - Days on Market

## API Documentation

Once the backend is running, visit:
- **Interactive API Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

### Key Endpoints

**Properties:**
- `GET /api/properties` - List properties with filters
- `GET /api/properties/{id}` - Get single property
- `POST /api/properties/upload-csv` - Upload CSV file
- `GET /api/properties/{id}/costs` - Get cost breakdown

**AI Assistant:**
- `POST /api/ai/ask` - Ask a question about housing codes
- `GET /api/ai/codes/search` - Search housing codes
- `POST /api/ai/codes` - Add housing code to database

**Market Trends:**
- `GET /api/trends` - Get market trends
- `GET /api/trends/summary` - Get trend summary
- `POST /api/trends` - Add trend data

## Project Structure

```
slv-housing-market/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # Database setup
│   │   ├── models/              # SQLAlchemy models
│   │   ├── routers/             # API endpoints
│   │   ├── services/            # Business logic
│   │   └── utils/               # Utilities
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API client
│   │   ├── types/               # TypeScript types
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
└── README.md
```

## Cost Calculation Details

The application calculates total monthly housing costs using:

1. **Monthly Mortgage:** Standard amortization formula
   ```
   M = P * [r(1+r)^n] / [(1+r)^n - 1]
   ```
   - P = Loan amount (price - down payment)
   - r = Monthly interest rate
   - n = Number of payments

2. **Monthly Property Tax:** Price × Tax Rate ÷ 12
   - Default Salt Lake County rate: 0.56% annual

3. **Monthly Insurance:** Industry standard estimates
   - <$300k: $800/year ($67/month)
   - $300k-$500k: $1200/year ($100/month)
   - >$500k: $1800/year ($150/month)

4. **Monthly HOA:** From property data (if available)

**Total Monthly Cost = Mortgage + Tax + Insurance + HOA**

## Seller Score Calculation

Since true seller ratings aren't publicly available, we use a composite score:

- **Days on Market:** Lower is better (exponential decay)
- **Price Stability:** Penalizes large price drops
- **Score Range:** 0-100 (higher is better)

## Data Sources

**Free Tier (Current Implementation):**
- Manual CSV uploads
- RentCast API (50 calls/month free)
- Salt Lake County Assessor (property tax data)
- U.S. Census Bureau API (market trends)

**Future Paid Options:**
- ATTOM Data API
- HouseCanary API
- Mashvisor API
- Full RentCast paid tier

The application uses an adapter pattern, making it easy to switch data sources by changing configuration.

## Development

### Running Tests

```bash
cd backend
pytest
```

### Building for Production

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run build
# Serve the dist/ folder with your preferred web server
```

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker ps

# Restart database
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### AI Assistant Not Working

1. Verify `ANTHROPIC_API_KEY` is set in `.env`
2. Ensure housing codes are populated in the database
3. Check API health: `curl http://localhost:8000/api/ai/health`

### CORS Errors

Update `CORS_ORIGINS` in `backend/.env`:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use this project for any purpose.

## Support

For issues or questions:
1. Check the API documentation at http://localhost:8000/docs
2. Review the troubleshooting section
3. Open an issue on GitHub

## Acknowledgments

- Built with FastAPI, React, and Claude AI
- Data sources: RentCast, Salt Lake County Assessor, U.S. Census Bureau
- Housing codes: Municode Library, UpCodes, Utah.gov

---

**Built for Salt Lake Valley homebuyers, developers, and real estate professionals.**
