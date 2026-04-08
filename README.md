# LLMVerse

A production-ready FastAPI application demonstrating best practices for LLM API integrations with OpenAI.

## Features

✅ **Production-Ready Architecture**
- Proper dependency injection
- Connection pooling for HTTP clients
- Comprehensive error handling
- Structured logging with request tracking
- Health check endpoints

✅ **Clean Code Principles**
- Type hints throughout
- Comprehensive docstrings
- Separation of concerns
- SOLID principles
- DRY (Don't Repeat Yourself)

✅ **Robust Error Handling**
- Custom exception hierarchy
- Specific error types (rate limit, timeout, auth, etc.)
- Automatic retry logic for transient errors
- Detailed error responses with request IDs

✅ **Security & Validation**
- Input validation with Pydantic
- Environment-based configuration
- No hardcoded secrets
- CORS configuration
- Request ID tracking

✅ **Observability**
- Structured JSON logging
- Request/response logging
- Error tracking with stack traces
- Health check endpoints (liveness, readiness)

## Project Structure

```
LLMVerse/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── router.py          # API router aggregation
│   │   ├── chat.py            # Chat endpoints
│   │   └── health.py          # Health check endpoints
│   ├── clients/
│   │   └── openai_client.py   # OpenAI API client with connection pooling
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   ├── exceptions.py      # Custom exceptions
│   │   ├── logging_config.py  # Logging configuration
│   │   └── middleware.py      # Custom middleware
│   ├── schemas/
│   │   └── chat.py            # Pydantic models
│   └── services/
│       └── llm_service.py     # Business logic layer
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.11 or higher
- OpenAI API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LLMVerse
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Chat

**POST** `/api/v1/chat`

Send a message to the LLM and receive a response.

**Request:**
```json
{
  "message": "What is the capital of France?"
}
```

**Response:**
```json
{
  "response": "The capital of France is Paris.",
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Health Checks

**GET** `/api/v1/health` - Comprehensive health check with component status

**GET** `/api/v1/health/ready` - Kubernetes readiness probe

**GET** `/api/v1/health/live` - Kubernetes liveness probe

## Configuration

All configuration is managed through environment variables. See `.env.example` for available options:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `OPENAI_BASE_URL` | OpenAI API base URL | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | Model to use | `gpt-4o-mini` |
| `OPENAI_TIMEOUT` | Request timeout in seconds | `30` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DEBUG` | Debug mode | `False` |

## Error Handling

The application provides detailed error responses with appropriate HTTP status codes:

- **400** - Validation errors
- **401** - Authentication errors
- **429** - Rate limit exceeded
- **500** - Internal server errors
- **503** - Service unavailable
- **504** - Request timeout

All errors include a `request_id` for tracking and debugging.

## Logging

The application uses structured logging with the following features:

- JSON formatted logs for production
- Human-readable console logs for development
- Request ID tracking across all logs
- Automatic error stack traces
- Configurable log levels

## Best Practices Implemented

### 1. **Configuration Management**
- Environment-based configuration
- Type-safe settings with Pydantic
- No hardcoded values
- Sensible defaults

### 2. **Dependency Injection**
- Proper use of FastAPI's `Depends()`
- Singleton pattern for shared resources
- No misuse of `lru_cache` with dependencies

### 3. **HTTP Client Lifecycle**
- Connection pooling
- Reusable client instances
- Proper cleanup on shutdown

### 4. **Error Handling**
- Custom exception hierarchy
- Specific error types
- Automatic retry for transient errors
- No exposure of internal errors to clients

### 5. **Input Validation**
- Pydantic models with validators
- Min/max length constraints
- Whitespace handling
- Type safety

### 6. **Code Quality**
- Comprehensive docstrings
- Type hints throughout
- Consistent formatting
- Meaningful variable names

## Development

### Running Tests
```bash
# Tests to be implemented
pytest
```

### Code Formatting
```bash
# Format code with black
black app/

# Sort imports
isort app/

# Type checking
mypy app/
```

### Linting
```bash
# Run flake8
flake8 app/

# Run pylint
pylint app/
```

## Production Deployment

### Docker (Recommended)

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t llmverse .
docker run -p 8000:8000 --env-file .env llmverse
```

### Environment Variables

Ensure all required environment variables are set in your production environment.

### Monitoring

- Use the `/api/v1/health` endpoint for health checks
- Monitor logs for errors and performance metrics
- Set up alerts for error rates and response times

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Acknowledgments

This project demonstrates best practices for:
- FastAPI application architecture
- LLM API integration
- Production-ready Python services
- Clean code principles
