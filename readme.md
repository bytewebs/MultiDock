# MultiDock

A comprehensive Docker automation platform featuring dynamic microservice orchestration and an AI-powered government schemes chatbot using RAG (Retrieval-Augmented Generation) technology.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [RAG Chatbot](#rag-chatbot)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Contributing](#contributing)

## Overview

MultiDock is a multi-user containerization platform that enables seamless Docker orchestration through an intuitive web interface. The platform features Role-Based Access Control (RBAC) with differentiated user and admin experiences, where regular users can deploy containerized microservices without authentication, while administrators require secure sign-in for comprehensive system management.

The system generates unique session-based Docker Compose configurations for each user, ensuring isolated deployments and preventing resource conflicts. Each deployment receives a unique UUID, enabling secure multi-tenant container orchestration where users can only view and manage their own containers, while administrators have system-wide visibility and control over all running containers.

A key microservice offering is an intelligent RAG-powered government schemes chatbot that leverages semantic search with Pinecone vector database and Google Gemini AI to provide comprehensive information about Indian government programs and policies.

## Features

### Core Platform
- **Multi-User Containerization Tool**: Supports concurrent users with isolated container deployments
- **Role-Based Access Control (RBAC)**: 
  - **Regular Users**: No authentication required, can deploy and manage personal containers
  - **Admin Users**: Secure sign-in required, system-wide container visibility and management
- **Session-Based UUID Management**: Each user deployment receives unique identifiers for secure isolation
- **Dynamic Docker Compose Generation**: Automatically generates compose files based on selected microservices
- **Intelligent Port Management**: Prevents conflicts through automatic free port allocation
- **Multi-Service Support**: API services, PostgreSQL, Redis, and specialized microservices
- **Granular Container Visibility**: Users view only their containers, admins see all system containers
- **Comprehensive Lifecycle Management**: Deploy, monitor, and terminate containers through REST API

### Government Schemes RAG Chatbot
- **Comprehensive Policy Database**: Extensive information on Indian government schemes and programs
- **Semantic Search**: Vector-based similarity search using sentence transformers for accurate information retrieval
- **Intelligent Query Processing**: Handles multiple query types including:
  - **Scheme Eligibility Criteria**: Detailed qualification requirements for beneficiaries
  - **Application Processes**: Step-by-step procedures for scheme enrollment
  - **Required Documents**: Complete documentation requirements and submission guidelines
  - **Benefits and Advantages**: Comprehensive coverage of scheme benefits and monetary assistance
  - **Target Beneficiaries**: Specific demographic and economic criteria for applicants
  - **Ministry Information**: Departmental details and administrative contact information
- **Context-Aware Responses**: Field-specific search optimization with Google Gemini AI integration
- **Real-Time Processing**: FastAPI-based microservice for instant query responses

### Supported Services
- **API Microservice**: Custom Flask-based API service
- **PostgreSQL Database**: Containerized database with custom port assignment
- **Redis Cache**: In-memory data structure store
- **RAG Chatbot**: AI-powered government schemes information system

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                       │
│  ┌───────────────┐              ┌──────────────────────────┐│
│  │ Regular User  │              │     Admin Dashboard      ││
│  │ (No Auth)     │              │   (Secure Sign-in)       ││
│  │ - Deploy Own  │              │ - View All Containers    ││
│  │ - View Own    │              │ - System-wide Control    ││
│  └───────────────┘              └──────────────────────────┘│
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
            ┌──────────────────┐
            │  Flask Backend   │
            │   (Port 5050)    │
            │ ┌──────────────┐ │
            │ │ UUID Session │ │
            │ │  Management  │ │
            │ └──────────────┘ │
            └────────┬─────────┘
                     │
                     ▼
    ┌─────────────────────────────────────┐
    │         Docker Containers           │
    │  ┌─────────────┐ ┌─────────────────┐│
    │  │    User A   │ │    User B       ││
    │  │  (UUID-1)   │ │   (UUID-2)      ││
    │  │ ┌─────────┐ │ │ ┌─────────────┐ ││
    │  │ │   API   │ │ │ │ PostgreSQL  │ ││
    │  │ │ Service │ │ │ │   + Redis   │ ││
    │  │ └─────────┘ │ │ └─────────────┘ ││
    │  └─────────────┘ └─────────────────┘│
    │  ┌─────────────────────────────────┐│
    │  │       RAG Chatbot Service       ││
    │  │  ┌─────────────┐ ┌────────────┐ ││
    │  │  │  Pinecone   │ │   Google   │ ││
    │  │  │  Vector DB  │ │  Gemini AI │ ││
    │  │  └─────────────┘ └────────────┘ ││
    │  └─────────────────────────────────┘│
    └─────────────────────────────────────┘
```

## Prerequisites

- Python 3.13 or higher
- Docker Desktop
- Git
- Active internet connection for AI services

### Required API Keys
- Google Gemini API Key
- Pinecone API Key

## Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd multidock_final
```

2. **Create and activate virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
Create a `.env` file in the project root:
```env
API_KEY=your_secure_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_index_name
GEMINI_API_KEY=your_gemini_api_key
```

5. **Start Docker Desktop** and ensure it's running:
```bash
docker ps
```

6. **Prepare RAG data (if using chatbot):**
```bash
python rag-chatbot/process_and_ingest.py
```

## Usage

### Start the Backend Server

**Development Mode:**
```bash
python backend/app.py
```

**Production Mode:**
```bash
./venv/bin/gunicorn -w 4 -b 0.0.0.0:5050 backend.app:app
```

### Launch the Dashboard

```bash
streamlit run streamlit_final.py
```

Access the dashboard at `http://localhost:8501`

### Basic Workflow

**For Regular Users (No Authentication Required):**
1. **Access Dashboard**: Open Streamlit interface without sign-in
2. **Select Microservices**: Choose from available containerized services
3. **Generate Configuration**: System creates Docker Compose with unique UUID
4. **Deploy Containers**: Launch selected services in isolated environment
5. **Monitor Personal Deployment**: View and manage only your containers
6. **Interact with Services**: Test deployed microservices including RAG chatbot
7. **Terminate Session**: Clean shutdown of your container group

**For Admin Users (Secure Access):**
1. **Authenticate**: Sign in with admin credentials (username: admin, password: admin)
2. **System Overview**: View all running containers across all users
3. **Selective Management**: Terminate specific containers or user sessions
4. **Resource Monitoring**: Track system-wide container resource usage
5. **Bulk Operations**: Manage multiple container groups simultaneously

## API Documentation

### Authentication
All API endpoints require the `x-api-key` header with your configured API key.

### Core Endpoints

#### POST /generate_compose
Generates Docker Compose configuration based on selected services.

**Request Body:**
```json
{
  "include_api": true,
  "include_db": false,
  "include_redis": true,
  "include_ragchatbot": true
}
```

**Response:**
```json
{
  "compose": "version: '3'\nservices:\n...",
  "compose_path": "/path/to/docker-compose.generated.abc123.yml",
  "ports": {
    "api": 5001,
    "redis": 6380,
    "ragchatbot": 5002
  },
  "user_id": "abc123def456"
}
```

#### POST /deploy
Deploys containers using generated compose file.

**Request Body:**
```json
{
  "user_id": "abc123def456"
}
```

#### POST /terminate
Terminates all containers for a specific user session.

#### GET /status
Returns deployment status and service health information.

#### GET /admin/containers
Lists all Docker containers (admin only).

#### POST /admin/terminate
Terminates selected containers by ID (admin only).

### RAG Chatbot Endpoints

#### POST /ask
Queries the government schemes chatbot.

**Request Body:**
```json
{
  "query": "What are the eligibility criteria for PMAY scheme?"
}
```

**Response:**
```json
{
  "query": "What are the eligibility criteria for PMAY scheme?",
  "answer": "The eligibility criteria for Pradhan Mantri Awas Yojana include..."
}
```

## RAG Chatbot

### Data Processing Pipeline

1. **Text Chunking**: Intelligent segmentation of government scheme documents
2. **Embedding Generation**: Converts text chunks to 384-dimensional vectors using sentence transformers
3. **Vector Storage**: Stores embeddings in Pinecone with metadata
4. **Semantic Retrieval**: Finds relevant context using cosine similarity
5. **AI Generation**: Uses Google Gemini to generate natural language responses

### Supported Query Types

- Scheme eligibility criteria
- Application processes
- Required documents
- Benefits and advantages
- Target beneficiaries
- Ministry information

### Example Queries

- "How to apply for PM-KISAN scheme?"
- "What documents are required for Ayushman Bharat?"
- "Eligibility criteria for housing schemes"
- "Benefits of digital India initiative"

## Project Structure

```
multidock_final/
├── backend/
│   ├── app.py                    # Main Flask application
│   └── requirements.txt          # Python dependencies
├── api/
│   ├── app.py                    # Simple API microservice
│   └── Dockerfile               # API container configuration
├── rag-chatbot/
│   ├── main.py                   # FastAPI chatbot server
│   ├── chunking.py              # Text processing and chunking
│   ├── embedder.py              # Text embedding generation
│   ├── pinecone_push.py         # Vector database operations
│   ├── process_and_ingest.py    # Data pipeline runner
│   ├── data/
│   │   ├── schemes.json         # Government schemes dataset
│   │   └── chunked_output.json  # Processed chunks
│   ├── .env                     # Environment variables
│   └── Dockerfile               # Chatbot container configuration
├── streamlit_final.py           # Web dashboard interface
├── .env                         # Global environment variables
└── requirements.txt             # Main dependencies
```

## Configuration

### Environment Variables

- `API_KEY`: Authentication key for API access
- `PINECONE_API_KEY`: Pinecone vector database API key
- `PINECONE_INDEX_NAME`: Name of the Pinecone index
- `GEMINI_API_KEY`: Google Gemini AI API key

### Port Configuration

The system automatically assigns ports in these ranges:
- API Services: 5001-6000
- Database Services: 5433-6000
- Redis: 6380-7000

### Admin Access and RBAC

**Regular User Access:**
- No authentication required for basic functionality
- Can deploy and manage personal containers only
- Limited visibility to own deployments and sessions
- Full access to RAG chatbot and basic microservices

**Admin Access Requirements:**
- Secure sign-in required (Credentials in Configuration section)
- System-wide container visibility and control
- Can terminate any user's containers or sessions
- Complete administrative control over the platform

**Session Isolation:**
- Each user deployment receives a unique UUID identifier
- Container namespacing prevents cross-user interference
- Secure multi-tenant environment with resource isolation

## Development

### Adding New Services

1. Create service configuration in `generate_compose()` function
2. Add port allocation logic
3. Update Streamlit interface checkboxes
4. Test deployment and termination

### Extending RAG Capabilities

1. Add new data sources to `data/schemes.json`
2. Modify chunking strategy in `chunking.py` if needed
3. Update retrieval logic in `main.py`
4. Retrain embeddings with `process_and_ingest.py`

## Troubleshooting

### Common Issues

**Docker Connection Error:**
```
docker.errors.DockerException: Error while fetching server API version
```
**Solution:** Ensure Docker Desktop is running and accessible.

**Port Already in Use:**
```
Port 5050 is already in use
```
**Solution:** Kill existing processes or modify port configuration.

**Pinecone Connection Issues:**
```
PineconeException: Invalid API key
```
**Solution:** Verify PINECONE_API_KEY in environment variables.

**RAG Chatbot Not Responding:**
```
Connection error. Could not connect to the backend.
```
**Solution:** Ensure the RAG chatbot container is running and accessible.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhancement`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/enhancement`)
5. Open a Pull Request
