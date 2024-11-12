# PDF Question-Answering System with Vector Search

A production-ready system that enables intelligent question-answering capabilities for PDF documents using OpenAI and vector search technology. Built with security and multi-tenancy in mind.

📖 [Read the detailed guide on Medium](https://codeglxy.medium.com/build-your-own-chatgpt-for-pdfs-a-complete-guide-to-ai-powered-document-intelligence-5ff086498f60)

## Features

- 🚀 Intelligent PDF document processing and analysis
- 🔍 Semantic search using vector embeddings
- 💬 AI-powered question answering using OpenAI
- 🔒 Multi-tenant architecture with team isolation
- 🎯 Production-ready with Docker support

## Quick Start

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- OpenAI API access (Azure or regular)
- Qdrant vector database

### Installation

1. Clone the repository:
```bash
git clone https://github.com/doganarif/pdf-gpt-vectordb-qa.git
cd pdf-gpt-vectordb-qa
```

2. Create and configure your environment file:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Start the services:
```bash
docker compose up --build
```

### Usage

1. Upload a PDF document:
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@/path/to/document.pdf" \
  -F "team_id=your_team_id" \
  -F "document_id=doc123"
```

2. Ask questions about the document:
```bash
curl -X POST http://localhost:8000/answer \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": "your_team_id",
    "question": "What is the main topic of the document?"
  }'
```

## Architecture

The system consists of several key components:

- **PDF Processing**: Extracts and chunks text from PDFs
- **Vector Search**: Enables semantic document search using Qdrant
- **Answer Generation**: Utilizes OpenAI for intelligent responses
- **API Layer**: Provides RESTful endpoints with security measures

## Configuration

Key environment variables:

```env
# OpenAI/Azure Configuration
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_key
AZURE_DEPLOYMENT_NAME=your_deployment

# Qdrant Configuration
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Application Configuration
DEBUG=false
ENABLE_HTTPS=true
MAX_UPLOAD_SIZE_MB=16
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload and process a PDF document |
| `/answer` | POST | Get answers to questions about documents |
| `/documents` | GET | List available documents for a team |
| `/health` | GET | Check system health status |

## Security Features

- Team-based isolation for multi-tenant setups
- Rate limiting per team
- Secure file handling
- Authorization middleware
- Input validation

## Development

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Deployment

The system is containerized and can be deployed using Docker Compose:

```bash
# Production deployment
docker compose -f docker-compose.prod.yml up -d
```

For production deployments, consider:
- Configuring proper authentication
- Implementing backup strategies
- Monitoring and logging


## Acknowledgments

- OpenAI for their powerful language models
- Qdrant team for the vector database
- All contributors and supporters

---
Built with ❤️ by [doganarif](https://github.com/doganarif)