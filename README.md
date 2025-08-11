
# ** Welcome to DXP-GEN-STUDIO! ** 🎉

# DXP-GEN-STUDIO - Project Overview

DXP-GEN-STUDIO is a comprehensive digital experience platform that combines AI-powered code generation for AEM Components with AEM development workflows. The project consists of multiple interconnected services working together to streamline component development and deployment.

This project contains three main components: a frontend application, a backend API, and an AEM Model Context Protocol (MCP) server. 

Each component serves a distinct purpose within the overall AEM component generation workflow.

## Service Architecture

### AEM MCP Server

Purpose: Bridge between AI generation and AEM deployment
Technology: Node.js/TypeScript with MCP protocol
Functions: Component generation, build automation, AEM deployment

### Backend Service

Purpose: AI-powered code generation API
Technology: FastAPI (Python)
Functions: Template processing, OpenAI integration, business logic

###  Frontend Application

Purpose: User interface for component design and management
Technology: React.js
Functions: Visual component builder, project management, deployment dashboard

### AEM Project Output

Purpose: Target AEM project structure for generated components
Technology: Adobe Experience Manager
Functions: Component hosting, content management, live deployment


## Prerequisites

Before setting up DXP-GEN-STUDIO, ensure you have the following installed:

Node.js (v18+ recommended) - Download
Python (v3.9+ recommended) - Download
Docker & Docker Compose - Download
Java JDK (v11+ for AEM) - Download
Apache Maven (v3.6+) - Download
Git - Download



## Folder Structure

DXP-GEN-STUDIO/
├── 📋 README.md                          # Project documentation and setup guide
├── 🐳 docker-compose.yml                 # Multi-service Docker orchestration
├── ⚙️ .env.example                       # Example environment variables
├── 📄 .gitignore                         # Git ignore patterns
│
├── 🔧 aem-mcp-server/                    # AEM Model Context Protocol Server
│   ├── 📁 src/                           # Server source code
│   │   ├── 📄 index.ts                   # Main MCP server entry point
│   │   ├── 📄 tools/                     # MCP tool implementations
│   │   │   ├── 📄 component-generator.ts # AEM component generation logic
│   │   │   ├── 📄 build-deploy.ts        # Build and deployment tools
│   │   │   └── 📄 project-manager.ts     # Project structure management
│   │   ├── 📄 utils/                     # Utility functions
│   │   │   ├── 📄 aem-client.ts          # AEM instance communication
│   │   │   ├── 📄 file-system.ts         # File system operations
│   │   │   └── 📄 template-engine.ts     # Code template processing
│   │   └── 📄 types/                     # TypeScript type definitions
│   │       ├── 📄 aem-types.ts           # AEM-specific types
│   │       └── 📄 mcp-types.ts           # MCP protocol types
│   ├── 📁 templates/                     # AEM component templates
│   │   ├── 📁 components/                # Component scaffolding templates
│   │   │   ├── 📄 component.html         # HTL template
│   │   │   ├── 📄 dialog.xml             # Dialog configuration
│   │   │   ├── 📄 clientlib.js           # JavaScript template
│   │   │   └── 📄 styles.scss            # SCSS template
│   │   └── 📁 project/                   # Project structure templates
│   ├── 📄 package.json                   # Node.js dependencies
│   ├── 📄 tsconfig.json                  # TypeScript configuration
│   ├── 📄 .env                           # Environment variables
│   └── 📄 Dockerfile                     # Docker configuration
│
├── 🐍 backend/                           # FastAPI Backend Service
│   ├── 📁 app/                           # Main application package
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main.py                    # FastAPI application entry
│   │   ├── 📁 api/                       # API route definitions
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 v1/                    # API version 1
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 components.py      # Component generation endpoints
│   │   │   │   ├── 📄 projects.py        # Project management endpoints
│   │   │   │   └── 📄 deployment.py      # Deployment endpoints
│   │   │   └── 📄 deps.py                # API dependencies
│   │   ├── 📁 services/                  # Business logic services
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 ai_service.py          # AI/OpenAI integration
│   │   │   ├── 📄 component_service.py   # Component generation logic
│   │   │   ├── 📄 aem_service.py         # AEM integration service
│   │   │   └── 📄 project_service.py     # Project management service
│   │   ├── 📁 models/                    # Data models and schemas
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 component.py           # Component data models
│   │   │   ├── 📄 project.py             # Project data models
│   │   │   └── 📄 user.py                # User data models
│   │   ├── 📁 templates/                 # Jinja2 code generation templates
│   │   │   ├── 📁 aem/                   # AEM-specific templates
│   │   │   │   ├── 📄 component.html.j2  # HTL component template
│   │   │   │   ├── 📄 dialog.xml.j2      # Dialog configuration template
│   │   │   │   ├── 📄 model.java.j2      # Sling model template
│   │   │   │   └── 📄 clientlib.js.j2    # Client library template
│   │   │   └── 📁 common/                # Common templates
│   │   ├── 📁 core/                      # Core application logic
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 config.py              # Application configuration
│   │   │   ├── 📄 security.py            # Security utilities
│   │   │   └── 📄 exceptions.py          # Custom exceptions
│   │   └── 📁 utils/                     # Utility functions
│   │       ├── 📄 __init__.py
│   │       ├── 📄 file_utils.py          # File manipulation utilities
│   │       ├── 📄 template_utils.py      # Template processing utilities
│   │       └── 📄 validation.py          # Input validation utilities
│   ├── 📄 requirements.txt               # Python dependencies
│   ├── 📄 .env                           # Environment variables
│   ├── 📄 Dockerfile                     # Docker configuration
│   └── 📁 tests/                         # Test suite
│       ├── 📄 __init__.py
│       ├── 📄 test_components.py
│       └── 📄 test_services.py
│
├── ⚛️ frontend/                          # React Frontend Application
│   ├── 📁 public/                        # Static assets
│   │   ├── 📄 index.html                 # Main HTML template
│   │   ├── 📄 favicon.ico                # Application favicon
│   │   └── 📄 manifest.json              # PWA manifest
│   ├── 📁 src/                           # React source code
│   │   ├── 📄 index.js                   # Application entry point
│   │   ├── 📄 App.js                     # Main application component
│   │   ├── 📁 components/                # Reusable React components
│   │   │   ├── 📁 common/                # Common UI components
│   │   │   │   ├── 📄 Header.js          # Application header
│   │   │   │   ├── 📄 Sidebar.js         # Navigation sidebar
│   │   │   │   ├── 📄 Loading.js         # Loading spinner
│   │   │   │   └── 📄 Modal.js           # Modal dialog component
│   │   │   ├── 📁 forms/                 # Form components
│   │   │   │   ├── 📄 ComponentForm.js   # Component creation form
│   │   │   │   ├── 📄 ProjectForm.js     # Project setup form
│   │   │   │   └── 📄 DeploymentForm.js  # Deployment configuration
│   │   │   └── 📁 editors/               # Code editor components
│   │   │       ├── 📄 CodeEditor.js      # Code editing interface
│   │   │       ├── 📄 PreviewPane.js     # Live preview component
│   │   │       └── 📄 FileTree.js        # Project file explorer
│   │   ├── 📁 pages/                     # Application pages/views
│   │   │   ├── 📄 Dashboard.js           # Main dashboard
│   │   │   ├── 📄 ComponentGenerator.js  # Component generation page
│   │   │   ├── 📄 ProjectManager.js      # Project management page
│   │   │   ├── 📄 DeploymentCenter.js    # Deployment management
│   │   │   └── 📄 Settings.js            # Application settings
│   │   ├── 📁 hooks/                     # Custom React hooks
│   │   │   ├── 📄 useAPI.js              # API communication hook
│   │   │   ├── 📄 useWebSocket.js        # WebSocket connection hook
│   │   │   └── 📄 useLocalStorage.js     # Local storage management
│   │   ├── 📁 services/                  # API service functions
│   │   │   ├── 📄 api.js                 # Main API client
│   │   │   ├── 📄 componentService.js    # Component-related API calls
│   │   │   ├── 📄 projectService.js      # Project-related API calls
│   │   │   └── 📄 deploymentService.js   # Deployment API calls
│   │   ├── 📁 utils/                     # Utility functions
│   │   │   ├── 📄 constants.js           # Application constants
│   │   │   ├── 📄 helpers.js             # Helper functions
│   │   │   └── 📄 validators.js          # Input validation
│   │   └── 📁 styles/                    # CSS and styling
│   │       ├── 📄 index.css              # Global styles
│   │       ├── 📄 components.css         # Component-specific styles
│   │       └── 📄 variables.css          # CSS custom properties
│   ├── 📄 package.json                   # Node.js dependencies
│   ├── 📄 .env.development               # Development environment variables
│   ├── 📄 .env.production                # Production environment variables
│   └── 📄 Dockerfile                     # Docker configuration
│
├── 📁 aem-project/                       # Generated AEM Project Output
│   ├── 📁 core/                          # Java backend (Sling Models, Services)
│   │   ├── 📁 src/main/java/             # Java source code
│   │   └── 📄 pom.xml                    # Maven configuration
│   ├── 📁 ui.apps/                       # AEM application package
│   │   ├── 📁 src/main/content/          # AEM content and components
│   │   │   └── 📁 jcr_root/
│   │   │       └── 📁 apps/
│   │   │           └── 📁 myproject/
│   │   │               └── 📁 components/ # Generated components go here
│   │   └── 📄 pom.xml
│   ├── 📁 ui.frontend/                   # Frontend build (Webpack)
│   │   ├── 📁 src/                       # SCSS and JS source files
│   │   └── 📄 pom.xml
│   ├── 📁 ui.content/                    # Sample content package
│   └── 📄 pom.xml                        # Parent POM
│
├── 📁 docs/                              # Documentation
│   ├── 📄 setup.md                       # Setup and installation guide
│   ├── 📄 api.md                         # API documentation
│   ├── 📄 deployment.md                  # Deployment guidelines
│   └── 📄 troubleshooting.md             # Common issues and solutions
│
└── 📁 scripts/                           # Utility scripts
    ├── 📄 setup.sh                       # Environment setup script
    ├── 📄 deploy.sh                      # Deployment script
    └── 📄 cleanup.sh                     # Cleanup script

# 🔧 **Setup Instructions**

##  **1. AEM MCPserver Setup**

### Description
The AEM MCP Server is a Node.js application that provides REST API endpoints for building and deploying Adobe Experience Manager (AEM) projects using Maven. It acts as a bridge between the frontend and the AEM environment, automating build and deployment tasks.

### Key Features
-   **Build Automation:** Triggers Maven builds for AEM projects via REST API.
-   **Package Deployment:** Deploys AEM packages to author instances.
-   **Authentication:** Implements basic authentication for API security.
-   **Package Management:** Enables listing and managing installed packages.
-   **Docker Support:** Offers containerized deployment option using Docker.

### Technologies

-   Node.js
-   Express
-   Maven
-   Docker

### Configuration

Configuration is managed via environment variables.  See `.env.example` for the required variables.

### Getting Started

1.  **Install Dependencies:**

    ```bash
    cd aem-mcp-server
    npm install
    ```

2.  **Configure Environment:**

    Create a `.env` file based on `.env.example` and update the values.

3.  **Start the Server:**

    ```bash
    npm run dev # Development mode
    npm run build && npm start # Production mode
    ```

### Docker Deployment

```bash
cd aem-mcp-server
docker-compose up -d
```

### **2. Backend Setup**

## Description
The backend is a Python-based FastAPI application that serves as the core logic for generating AEM components. It leverages OpenAI's GPT models to generate code snippets for HTL, Sling Models, and dialog XML based on user prompts.

## Key Features

AEM Component Generation: Generates AEM component code using AI.
REST API: Provides endpoints for component generation.
Templating: Uses Jinja2 templates for code generation.
OpenAI Integration: Integrates with OpenAI's GPT models for code synthesis.
   Technologies
   Python
   FastAPI
   OpenAI API
   Jinja2

## Configuration
Configuration is managed via environment variables. See .env for the required variables, especially the OPENAI_API_KEY.

Configure .env
Create backend/.env with:
OPENAI_API_KEY=your_openai_api_key_here
PORT=5000

### 1. Getting Started

cd backend
pip install -r requirements.txt

### 2. Configure Environment:

Create a .env file and set the OPENAI_API_KEY.

### 3. Run the Application:

python run.py

### API Endpoints

/api/component/generate: Generates AEM component code based on a prompt.

## **3. Frontend Setup**

### Description
The frontend is a React application that provides a user interface for interacting with the backend API and generating AEM components. It allows users to input prompts, configure component parameters, and view the generated code.

### Key Features
User Interface: Provides a user-friendly interface for AEM component generation.
Component Preview: Displays the generated code in a structured format.
Project Generation: Supports generating entire AEM projects.

### Technologies
   React
   React Router
   Axios

## Getting Started

### **1. Install Dependencies:**

cd frontend
npm install
### **2. Start the Application:**

npm start

The application will be accessible at http://localhost:3000.

### Other Features

## 🔒 Security
✔️ Never commit .env to version control
✔️ Rotate OpenAI API keys periodically
✔️ For production, implement authentication middleware for backend endpoints

## 🔮 Future Enhancements
✅ Download generated files as zip
✅ Syntax highlighting in output panel
✅ Docker Compose for single-command local setup
✅ CI/CD pipeline integration with AEM Cloud Manager

## 👨‍💻 Contributors

Vinodh Sampath
Narashiman N J
Nandlal Pandit
Guru
Varun
