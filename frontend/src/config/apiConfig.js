// API Configuration
// This file contains all configurable API endpoints and settings

const getApiBaseUrl = () => {
  // Check for environment variable first
  if (process.env.REACT_APP_API_BASE_URL) {
    return process.env.REACT_APP_API_BASE_URL;
  }
  
  // Check for local storage override (useful for development)
  const localStorageUrl = localStorage.getItem('API_BASE_URL');
  if (localStorageUrl) {
    return localStorageUrl;
  }
  
  // Default to port 5001 (correct backend port)
  return 'http://localhost:5001';
};

const getAemBuilderUrl = () => {
  // Check for environment variable first
  if (process.env.REACT_APP_AEM_BUILDER_URL) {
    return process.env.REACT_APP_AEM_BUILDER_URL;
  }
  
  // Default AEM builder service
  return 'http://localhost:8080';
};

// Export configuration object
export const apiConfig = {
  // Base API URL for backend services
  baseUrl: getApiBaseUrl(),
  
  // AEM Builder service URL
  aemBuilderUrl: getAemBuilderUrl(),
  // Optional: Basic auth token (not used automatically; consumed by callers)
  // Set REACT_APP_AEM_BUILDER_BASIC_AUTH to either the base64 token or full "Basic <token>"
  aemBuilderBasicAuth: process.env.REACT_APP_AEM_BUILDER_BASIC_AUTH || null,
  
  // API endpoints
  endpoints: {
    // Component generation endpoints
    generateComponent: '/api/component/generate',
    generateAemComponent: '/api/component',
    generateEdsBlock: '/api/component/generate-eds-block',
    
    // Project endpoints
    generateProject: '/api/projects/generate',
    
    // AEM project build endpoint
    buildAemProject: '/api/build-aem-project',
    
    // EDS Git integration endpoints
    pushEdsToGit: '/api/eds/push-to-git',
    getGitConfig: '/api/eds/git-config'
  },
  
  // Request timeout in milliseconds
  timeout: 30000,
  
  // Helper method to get full URL
  getFullUrl: (endpoint) => {
    if (endpoint.startsWith('/api/build-aem-project')) {
      return `${apiConfig.aemBuilderUrl}${endpoint}`;
    }
    return `${apiConfig.baseUrl}${endpoint}`;
  }
};

// Helper function to update API base URL at runtime
export const updateApiBaseUrl = (newUrl) => {
  localStorage.setItem('API_BASE_URL', newUrl);
  // Force reload to apply changes
  window.location.reload();
};

// Helper function to get current API configuration
export const getApiConfig = () => {
  return {
    baseUrl: apiConfig.baseUrl,
    aemBuilderUrl: apiConfig.aemBuilderUrl,
  aemBuilderBasicAuth: apiConfig.aemBuilderBasicAuth,
    endpoints: apiConfig.endpoints
  };
};

export default apiConfig;
