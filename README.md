
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


## 🙏 Acknowledgments

- Adobe Experience Manager for the component framework
- OpenAI, Gemini and Anthropic for AI model access
- React and FastAPI communities for excellent documentation
- Docker for containerization capabilities

## 📞 Support

For support and questions:
- Create an issue in this repository
- Check existing documentation
- Review the setup guides

---

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# 🔧 **Local Setup Instructions**

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


## 👨‍💻 Contributors

✔️ Vinodh Sampath
✔️ Narashiman N J
✔️ Nandlal Pandit
✔️ Guru
✔️ Varun
