
# DXP Component Generator Studio

A comprehensive AI-powered component generation studio for Adobe Experience Manager (AEM) development. This tool provides an intuitive interface for creating, previewing, and managing AEM components with real-time visual feedback.

## 🚀 Features

### Core Capabilities
- **AI-Powered Component Generation**: Leverage advanced AI models to generate AEM components from natural language descriptions
- **Real-Time Preview**: Interactive component preview with placeholder image functionality
- **Comprehensive Output**: Generates HTL templates, CSS styling, Java Sling models, and dialog configurations
- **Docker Integration**: Complete containerized development environment
- **Enhanced CSS Processing**: Advanced CSS cleaning and scoping for better preview rendering

### Technical Stack
- **Frontend**: React-based interface with enhanced component preview
- **Backend**: FastAPI with AI-powered generation agents
- **Database**: MongoDB for component storage and management
- **Containerization**: Docker and Docker Compose for seamless deployment
- **AEM Integration**: Complete AEM project archetype with Maven structure

## 📋 Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Java 11+ (for AEM development)
- Maven 3.6+ (for AEM builds)

## 🛠️ Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/Vinodh-Projects/DXP-COMPONENT-GENERATOR.git
   cd DXP-COMPONENT-GENERATOR
   ```

2. **Set up environment variables**
   ```bash
   # Copy example environment files
   cp .env.example .env
   cp .env.example .env.docker
   
   # Edit .env files with your API keys
   # Required: OpenAI API key, Anthropic API key (optional)
   ```

3. **Start the application**
   ```bash
   # Windows
   ./start-docker.bat
   
   # Linux/Mac
   ./start-docker.sh
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup

Refer to `setup_instructions.md` for detailed manual installation steps.

## 🏗️ Architecture

```
DXP-COMPONENT-GENERATOR/
├── frontend/              # React application with component preview
├── backend/               # FastAPI server with AI agents
├── aem-mcp-server/       # Model Context Protocol server
├── project_code/         # Generated AEM project structure
├── docker-compose.yml    # Docker orchestration
└── .env.example         # Environment template
```

### AI Generation Agents
- **Context Agent**: Analyzes component requirements
- **Generation Agent**: Creates component code using AI models
- **Assembly Agent**: Combines generated files into complete components
- **Preprocessing Agent**: Optimizes and validates component structure

## 🎯 Usage

### Creating Components

1. **Open the Studio**: Navigate to http://localhost:3000
2. **Describe Your Component**: Enter a natural language description
3. **Configure Options**: Set component name, positioning, and styling preferences
4. **Generate**: Click generate to create your component
5. **Preview**: Review the component in the integrated preview panel
6. **Download**: Export the complete component package

### Component Types Supported
- **Content Components**: Text, images, cards, hero banners
- **Layout Components**: Containers, grids, sections
- **Form Components**: Input fields, buttons, form containers
- **Navigation Components**: Menus, breadcrumbs, pagination
- **Interactive Components**: Accordions, tabs, carousels

## 🔧 Configuration

### Environment Variables

```bash
# AI Configuration
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Application Settings
FRONTEND_PORT=3000
BACKEND_PORT=8000
MONGODB_PORT=27017

# Development Mode
NODE_ENV=development
DEBUG=true
```

### Docker Configuration

The application uses multi-container Docker setup:
- **Frontend Container**: React development server
- **Backend Container**: FastAPI with Python dependencies
- **MongoDB Container**: Database for component storage
- **Volume Mounts**: For development file synchronization

## 🎨 Preview Features

### Enhanced Visual Preview
- **Placeholder Images**: Automatic image replacement for better component visualization
- **CSS Scoping**: Isolated styling to prevent conflicts
- **Responsive Design**: Preview components across different screen sizes
- **Real-time Updates**: Instant preview updates as you modify components

### Supported Preview Types
- **HTL Templates**: Rendered component markup
- **CSS Styling**: Applied component styles
- **Layout Positioning**: Flexbox and grid layouts
- **Interactive Elements**: Buttons, forms, and navigation

## 🚀 Development

### Local Development Setup

1. **Backend Development**
   ```bash
   cd backend
   pip install -r requirements.txt
   python run.py
   ```

2. **Frontend Development**
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **AEM Project Development**
   ```bash
   cd project_code
   mvn clean install
   ```

### Adding New Component Types

1. **Update Prompts**: Modify generation prompts in `backend/app/prompts/aem/`
2. **Enhance Agents**: Extend AI agents in `backend/app/agents/`
3. **Update Frontend**: Add new component templates in `frontend/src/components/`

## 📚 Documentation

- **Setup Guide**: `setup_instructions.md`
- **Docker Guide**: `Docker_setup_readme.md`
- **API Documentation**: Available at `/docs` endpoint
- **Component Examples**: Check `frontend/src/components/` for implementation patterns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines
- Follow React best practices for frontend development
- Use FastAPI patterns for backend endpoints
- Maintain Docker compatibility for all changes
- Include tests for new features
- Update documentation for API changes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Adobe Experience Manager for the component framework
- OpenAI and Anthropic for AI model access
- React and FastAPI communities for excellent documentation
- Docker for containerization capabilities

## 📞 Support

For support and questions:
- Create an issue in this repository
- Check existing documentation
- Review the setup guides

---

**Built with ❤️ for the AEM development community**



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
