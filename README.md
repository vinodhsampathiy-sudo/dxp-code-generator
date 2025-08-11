
# DXP Component Generator Studio

A comprehensive AI-powered component generation studio for Adobe Experience Manager (AEM) development. This tool provides an intuitive interface for creating, previewing, and managing AEM components with real-time visual feedback.

## 🚀 Features

Refer [Technical_documenttaion.md](https://github.com/Vinodh-Projects/DXP-COMPONENT-GENERATOR/edit/main/TECHNICAL_DOCUMENTATION.md) for  detail tehcnical documentaion.

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

Refer to [setup_instructions.md](https://github.com/Vinodh-Projects/DXP-COMPONENT-GENERATOR/edit/main/setup_instructions.md.md) for detailed manual installation steps.

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

### Other Features

## 🔒 Security
- ✔️ Never commit .env to version control
- ✔️ Rotate OpenAI API keys periodically
- ✔️ For production, implement authentication middleware for backend endpoints


## 👨‍💻 Contributors

- ✔️ Vinodh Sampath
- ✔️ Narashiman N J
- ✔️ Nandlal Pandit
- ✔️ Guru
- ✔️ Varun
