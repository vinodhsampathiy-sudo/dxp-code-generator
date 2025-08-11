import express from 'express';
import { exec } from 'child_process';
import dotenv from 'dotenv';
import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';
import path from 'path';
import { promisify } from 'util';
import cors from 'cors';

// Load environment variables
dotenv.config();

const app = express();
const execAsync = promisify(exec);

// CORS configuration
const corsOptions = {
  origin: ['http://localhost:3000','http://localhost:3001'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
};

// Middleware
app.use(cors(corsOptions));
app.use(express.json());

// Basic authentication middleware
const authenticate = (req: express.Request, res: express.Response, next: express.NextFunction) => {
  const auth = req.headers.authorization;
  
  if (!auth || !auth.startsWith('Basic ')) {
    return res.status(401).json({ error: 'Authentication required' });
  }
  
  const credentials = Buffer.from(auth.split(' ')[1], 'base64').toString('utf-8');
  const [username, password] = credentials.split(':');
  
  if (username === process.env.MCP_USERNAME && password === process.env.MCP_PASSWORD) {
    return next();
  } else {
    return res.status(401).json({ error: 'Invalid credentials' });
  }
};

// Configuration interface
interface BuildConfig {
  projectPath: string;
  mavenProfile?: string;
  packagePath?: string;
  autoInstall?: boolean;
}

// Health check endpoint
app.get('/api/health', (_req, res) => {
  res.json({ 
    status: 'healthy', 
    server: 'AEM MCP Server',
    timestamp: new Date().toISOString()
  });
});

// Build AEM project endpoint
app.post('/api/build-aem-project', authenticate, async (req, res): Promise<any> => {
  console.log('Received request to build AEM project.');
  
  const config: BuildConfig = {
    projectPath: req.body.projectPath || process.env.AEM_PROJECT_PATH || '/path/to/your/aem/project',
    mavenProfile: req.body.mavenProfile || 'autoInstallPackage',
    packagePath: req.body.packagePath,
    autoInstall: req.body.autoInstall !== false
  };

  try {
    // Validate project path
    if (!fs.existsSync(config.projectPath)) {
      return res.status(400).json({ error: 'Project path does not exist' });
    }

    // Build Maven command
    const mavenCommand = config.mavenProfile 
      ? `mvn clean install -P${config.mavenProfile} -Pclassic -Padobe-public -DskipTests -Dmaven.javadoc.skip=true`
      : 'mvn clean install';

    // Execute Maven build
    console.log(`Executing: ${mavenCommand} in ${config.projectPath}`);
    const { stdout, stderr } = await execAsync(mavenCommand, {
      cwd: config.projectPath,
      maxBuffer: 1024 * 1024 * 10 // 10MB buffer
    });

    console.log('Build output:', stdout);
    if (stderr) console.error('Build warnings/errors:', stderr);

    // If autoInstall is disabled or package deployment is handled by Maven profile
    if (!config.autoInstall || config.mavenProfile?.includes('autoInstall')) {
      return res.json({
        status: 'success',
        message: 'Build completed successfully',
        output: stdout
      });
    }

    // Deploy package if path is provided
    if (config.packagePath) {
      const deployResult = await deployPackage(config.packagePath);
      return res.json({
        status: 'success',
        message: 'Build and deployment completed successfully',
        buildOutput: stdout,
        deploymentResult: deployResult
      });
    }

    res.json({
      status: 'success',
      message: 'Build completed successfully',
      output: stdout
    });

  } catch (error: any) {
    console.error('Build failed:', error);
    res.status(500).json({
      status: 'error',
      message: 'Build failed',
      error: error.message,
      details: error.stderr || error.toString()
    });
  }
});

// Deploy package endpoint
app.post('/api/deploy-package', authenticate, async (req, res): Promise<any> => {
  const { packagePath, packageName, force = true } = req.body;

  if (!packagePath) {
    return res.status(400).json({ error: 'Package path is required' });
  }

  try {
    const result = await deployPackage(packagePath, packageName, force);
    return res.json(result);
  } catch (error: any) {
    return res.status(500).json({
      status: 'error',
      message: 'Deployment failed',
      error: error.message
    });
  }
});

// List packages endpoint
app.get('/api/packages', authenticate, async (_req, res): Promise<any> => {
  try {
    const response = await axios.get(
      `${process.env.AEM_HOST}/crx/packmgr/service.jsp?cmd=ls`,
      {
        auth: {
          username: process.env.AEM_SERVICE_USER!,
          password: process.env.AEM_SERVICE_PASSWORD!
        }
      }
    );

    return res.json({
      status: 'success',
      packages: response.data
    });
  } catch (error: any) {
    return res.status(500).json({
      status: 'error',
      message: 'Failed to list packages',
      error: error.message
    });
  }
});

// Get build status endpoint
app.get('/api/build-status/:buildId', authenticate, async (req, res): Promise<any> => {
  // This would typically check a build queue or process manager
  // For now, return a mock response
  return res.json({
    buildId: req.params.buildId,
    status: 'completed',
    message: 'Build status tracking not yet implemented'
  });
});

// Helper function to deploy package to AEM
async function deployPackage(packagePath: string, packageName?: string, force: boolean = true) {
  if (!fs.existsSync(packagePath)) {
    throw new Error(`Package file not found: ${packagePath}`);
  }

  const fileName = packageName || path.basename(packagePath);
  const formData = new FormData();
  formData.append('file', fs.createReadStream(packagePath));
  formData.append('name', fileName);
  formData.append('force', force.toString());

  console.log(`Uploading package: ${fileName}`);

  // Upload package
  const uploadResponse = await axios.post(
    `${process.env.AEM_HOST}/crx/packmgr/service.jsp`,
    formData,
    {
      auth: {
        username: process.env.AEM_SERVICE_USER!,
        password: process.env.AEM_SERVICE_PASSWORD!
      },
      headers: formData.getHeaders()
    }
  );

  console.log('Package uploaded successfully');

  // Install package
  const installResponse = await axios.post(
    `${process.env.AEM_HOST}/crx/packmgr/service/exec.json?cmd=install`,
    null,
    {
      auth: {
        username: process.env.AEM_SERVICE_USER!,
        password: process.env.AEM_SERVICE_PASSWORD!
      },
      params: {
        path: `/etc/packages/my_packages/${fileName}`
      }
    }
  );

  return {
    status: 'success',
    message: 'Package deployed successfully',
    uploadResponse: uploadResponse.data,
    installResponse: installResponse.data
  };
}

// Error handling middleware
app.use((err: any, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  console.error('Server error:', err);
  res.status(500).json({
    status: 'error',
    message: 'Internal server error',
    error: err.message
  });
});

// Start server
const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`AEM MCP Server running on port ${PORT}`);
  console.log('Configuration:');
  console.log(`- AEM Host: ${process.env.AEM_HOST}`);
  console.log(`- MCP Username: ${process.env.MCP_USERNAME}`);
  console.log('Ready to accept requests...');
});

export default app;
