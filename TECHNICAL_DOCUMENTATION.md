# DXP-GEN-STUDIO Technical Documentation

## System Overview

DXP-GEN-STUDIO is a comprehensive AI-powered Adobe Experience Manager (AEM) component generation platform built using a microservices architecture. The system orchestrates four interconnected services to automate AEM component development from design to deployment.

![System Architecture Overview](placeholder-system-architecture.png)
*Figure 1: DXP-GEN-STUDIO System Architecture*

### Core Services Architecture

| Service | Technology | Port | Purpose |
|---------|------------|------|---------|
| **Frontend** | React.js + Nginx | 3000 | User interface & component design |
| **Backend** | Python FastAPI | 5000 | AI orchestration & business logic |
| **AEM MCP Server** | Node.js/TypeScript | 8080 | AEM integration & deployment |
| **MongoDB** | MongoDB 7.0 | 27017 | Data persistence & chat history |

## Service Implementation Details

### 1. Frontend Service (React.js)

**Technology Stack:**
- React.js 18+ with functional components and hooks
- React Router for SPA navigation
- CSS-in-JS styling with responsive design
- Nginx for production serving

**Key Components:**
```javascript
// Core application structure
├── src/
│   ├── App.js                      // Main routing & navigation
│   ├── components/
│   │   ├── DXPComponentGeneratorPage.js  // Primary component builder
│   │   ├── EDSBlockGeneratorPage.js      // Edge Delivery Services
│   │   ├── ProjectGeneratorPage.js       // AEM project scaffolding
│   │   └── CodeOutputPanel.js            // Generated code display
│   └── config/
│       └── apiConfig.js            // Backend service configuration
```

**API Integration:**
- RESTful communication with Backend service on port 5000
- Real-time component generation status updates
- File download capabilities for generated AEM packages

![Frontend Interface](placeholder-frontend-interface.png)
*Figure 2: Component Generation Interface*

### 2. Backend Service (Python FastAPI)

**Technology Stack:**
- FastAPI framework with automatic OpenAPI documentation
- OpenAI GPT-4 integration for code generation
- LangChain for AI agent orchestration
- MongoDB for persistent storage
- Jinja2 for template processing

**Agent Architecture:**
```python
# AI Agent Pipeline
├── agents/
│   ├── preprocessor_agent.py    // Requirements analysis
│   ├── context_agent.py         // Component context generation
│   ├── extract_agent.py         // Sling Model generation
│   ├── assemble_agent.py        // HTL template creation
│   ├── generate_agent.py        // CSS/JS client library
│   └── generation_agent.py      // Complete component assembly
```

**Core API Endpoints:**
- `POST /api/component/generate` - Component generation
- `POST /api/component/refine` - Code refinement
- `GET /api/project/{id}` - Project management
- `POST /api/component/eds-blocks` - Edge Delivery Services

**AI Prompt Engineering:**
The system uses sophisticated prompt templates stored in `/prompts/aem/` for each generation phase:
- `agent_1.txt` - Sling Model requirements analysis
- `agent_2.txt` - HTL template generation with BEM methodology
- `agent_3.txt` - Dialog XML with Touch UI components
- `agent_4.txt` - Client library CSS/JS with responsive design

### 3. AEM MCP Server (TypeScript)

**Technology Stack:**
- Node.js with TypeScript for type safety
- Express.js REST API framework
- Model Context Protocol (MCP) for AEM integration
- Maven wrapper for AEM project builds
- Axios for HTTP client operations

**Core Functionality:**
```typescript
// Key endpoints and capabilities
├── /api/build-project         // Maven build execution
├── /api/deploy-package        // AEM package deployment
├── /api/packages              // Package management
├── /api/health                // Service health monitoring
└── /api/project-status        // Build status tracking
```

**AEM Integration:**
- Direct connection to AEM Author instance (default: localhost:4502)
- Package Manager API integration for deployment
- Maven lifecycle management (clean, compile, package, install)
- Build artifact management in `/project_code` volume

![MCP Server Architecture](placeholder-mcp-server.png)
*Figure 3: AEM MCP Server Integration Flow*

### 4. MongoDB Database

**Data Models:**
- **Chat History**: Stores AI conversation context for refinement
- **Project Metadata**: Component specifications and configurations
- **Generation Logs**: Audit trail of component generation activities
- **User Sessions**: State management for long-running operations

## Docker Orchestration

**Network Architecture:**
```yaml
# Docker Compose Service Mesh
networks:
  dxp-network:
    driver: bridge
    
volumes:
  mongodb_data:           # Persistent database storage
  aem-maven-cache:        # Maven dependency cache
  ./output:/app/output    # Generated component output
  ./project_code:/app/projects  # AEM project workspace
```

**Health Monitoring:**
Each service implements comprehensive health checks:
- **Frontend**: HTTP endpoint availability
- **Backend**: MongoDB connectivity + API responsiveness
- **AEM MCP**: Maven availability + AEM connection
- **MongoDB**: Database ping validation

## Component Generation Workflow

### 1. User Input Processing
```mermaid
Frontend → Backend → AI Agents → Component Generation
```

### 2. AI Agent Orchestration
The system employs a sequential agent pipeline:

1. **Preprocessor Agent**: Analyzes user requirements and technical specifications
2. **Context Agent**: Generates component context and architectural decisions
3. **Extract Agent**: Creates Sling Model with proper annotations and ArrayList imports
4. **Assemble Agent**: Generates HTL template with BEM methodology and responsive design
5. **Generate Agent**: Produces complete client library with CSS Grid/Flexbox and JavaScript

### 3. Code Output Structure
```
Generated AEM Component/
├── .content.xml              // Component definition
├── _cq_dialog.xml           // Author dialog configuration
├── component.html           // HTL template
├── ComponentModel.java      // Sling Model
└── clientlibs/
    ├── .content.xml         // Client library configuration
    ├── css/
    │   └── component.css    // Responsive CSS with BEM
    └── js/
        └── component.js     // ES6+ JavaScript
```

![Generation Workflow](placeholder-generation-workflow.png)
*Figure 4: Component Generation Pipeline*

## Deployment & Configuration

### Environment Variables
```bash
# Core API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# AEM Configuration
AEM_HOST=http://localhost:4502
AEM_SERVICE_USER=admin
AEM_SERVICE_PASSWORD=admin

# Database Configuration
MONGODB_URI=mongodb://admin:password123@mongodb:27017/aem_component_generator
```

### Production Deployment
```bash
# Complete system startup
docker-compose up -d

# Individual service management
docker-compose restart backend
docker-compose logs -f frontend
docker-compose down aem-mcp-server
```

### Monitoring & Observability
- **Health Endpoints**: `/health` on all services
- **Log Aggregation**: Centralized logging in `/logs` volumes
- **Performance Metrics**: Container resource monitoring
- **API Documentation**: FastAPI automatic OpenAPI at `localhost:5000/docs`

## Integration Points

### Frontend ↔ Backend
- **Protocol**: HTTP/REST
- **Data Format**: JSON
- **Authentication**: CORS-enabled public endpoints
- **File Transfer**: Multipart form data for large payloads

### Backend ↔ AEM MCP Server
- **Protocol**: HTTP/REST
- **Authentication**: Basic Auth with configurable credentials
- **Operations**: Build triggers, deployment commands, status polling

### Backend ↔ MongoDB
- **Driver**: PyMongo with connection pooling
- **Collections**: `chat_history`, `projects`, `generation_logs`
- **Indexing**: Optimized queries for chat retrieval and project lookup

### AEM MCP Server ↔ AEM Instance
- **Protocol**: AEM Package Manager API
- **Authentication**: Service user credentials
- **Operations**: Package upload, installation, activation

This architecture ensures scalable, maintainable, and production-ready AEM component generation with comprehensive AI-powered automation from requirements to deployment.
