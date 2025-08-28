import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  Upload,
  Image,
  Code2,
  Clock,
  ChevronLeft,
  ChevronRight,
  Copy,
  Check,
  X,
  FileCode,
  Layout,
  Component,
  Layers,
  Sparkles,
  ChevronDown,
  Cpu,
  Database,
  Search,
  Plus,
  Trash2,
  RefreshCw,
  MessageSquare,
  History
} from "lucide-react";
import axios from "axios";
import VisualCodeSandbox from "./VisualCodeSandbox";
import MkdTable from "./MarkdownTable";
import AEMRightPanel from "./AEMRightPanel";
import EDSRightPanel from "./EDSRightPanel";
import { downloadZipFromBase64 } from "../utils/zipdownload.js";
import { apiConfig } from '../config/apiConfig.js';

// API base URL for component endpoints (backward compatibility)
const API_BASE_URL = `${apiConfig.baseUrl}/api/component`;

// Custom scrollbar CSS
const customScrollbar = `
  .dxp-scrollbar::-webkit-scrollbar {
    height: 6px;
    width: 6px;
    background: transparent;
  }
  .dxp-scrollbar::-webkit-scrollbar-thumb {
    background: #d1d5db;
    border-radius: 4px;
  }
  .dxp-scrollbar::-webkit-scrollbar-track {
    background: transparent;
  }
  .dxp-scrollbar {
    scrollbar-width: thin;
    scrollbar-color: #d1d5db transparent;
  }
`;

const DXPComponentGeneratorInterface = () => {
  console.log("🚀 DXPComponentGeneratorInterface component loaded/rendered!");
  
  // Existing state
  const [leftPanelOpen, setLeftPanelOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [uploadedImage, setUploadedImage] = useState(null);
  const [generatedComponents, setGeneratedComponents] = useState([]);
  const [selectedComponent, setSelectedComponent] = useState(null);
  const [copiedCode, setCopiedCode] = useState(false);
  const [selectedLLM, setSelectedLLM] = useState("GPT-4");
  const [selectedCMS, setSelectedCMS] = useState("Adobe Experience Manager");
  const [showLLMDropdown, setShowLLMDropdown] = useState(false);
  const [showCMSDropdown, setShowCMSDropdown] = useState(false);
  
  const [activeCodeTab, setActiveCodeTab] = useState(
    selectedCMS === "Adobe EDS" ? "css" : "HTML"
  );
  const [copiedSection, setCopiedSection] = useState(null);
  const [tabs, setTabs] = useState(
    selectedCMS === "Adobe EDS" ? ["css", "js", "mkd_table"] : ["HTML", "Sling Model", "Dialog"]
  );
  const [isLoading, setIsLoading] = useState(false);
  const [loadingContext, setLoadingContext] = useState(null);
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [htmlNode, setHtmlNode] = useState("");
  const [cssNode, setCssNode] = useState("");
  
  // Error state for right panel
  const [errorMessage, setErrorMessage] = useState(null);
  const [errorContext, setErrorContext] = useState(null);
  
  // Success state for right panel
  const [successMessage, setSuccessMessage] = useState(null);
  const [successContext, setSuccessContext] = useState(null);

  // New state for chat history
  const [chatSessions, setChatSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [showNewSessionModal, setShowNewSessionModal] = useState(false);
  const [sessionTitle, setSessionTitle] = useState("");
  const [isRefining, setIsRefining] = useState(false);
  const [selectedComponentForRefinement, setSelectedComponentForRefinement] = useState(null);

  const llmButtonRef = useRef(null);
  const cmsButtonRef = useRef(null);

  const [edsOutput, setEdsOutput] = useState({});

  // Debug log after ALL state is initialized
  console.log("🔍 RENDER STATE:", { selectedCMS, rightPanelOpen, leftPanelOpen });

  // LLM and CMS options
  const llmOptions = ["GPT-4", "Gemini Pro", "Claude 3.5"];
  const cmsOptions = [
    "Adobe Experience Manager",
    "Adobe EDS",
    "Sitecore XP (Upcoming)",
    "Optimizely DXP (Upcoming)",
  ];

  // Load chat sessions on component mount
  useEffect(() => {
    loadChatSessions();
  }, []);

  useEffect(() => {
    console.log("🔄 CMS Change useEffect triggered! selectedCMS:", selectedCMS);
    
    if (selectedCMS === "Adobe EDS") {
      console.log("🟢 Switching to Adobe EDS - setting EDS tabs");
      setChatSessions([])
      setMessages([]);
      setGeneratedComponents([]);
      // Clear component selection when switching to EDS
      setSelectedComponent(null);
      setSelectedComponentForRefinement(null);
      // Keep right panel open for EDS
      // Clear errors
      setErrorMessage(null);
      setErrorContext(null);
      // Set EDS-specific tabs and default active tab
      setTabs(["css", "js", "mkd_table"]);
      setActiveCodeTab("css");
      console.log("✅ EDS tabs set: [css, js, mkd_table], activeTab: css");
    } else if (selectedCMS === "Adobe Experience Manager") {
      console.log("🔵 Switching to Adobe Experience Manager - setting AEM tabs");
      loadChatSessions();
      // Clear component selection when switching to AEM
      setSelectedComponent(null);
      setSelectedComponentForRefinement(null);
      // Keep right panel open for AEM
      // Clear errors
      setErrorMessage(null);
      setErrorContext(null);
      // Set AEM-specific tabs and default active tab
      setTabs(["HTML", "Sling Model", "Dialog"]);
      setActiveCodeTab("HTML");
      console.log("✅ AEM tabs set: [HTML, Sling Model, Dialog], activeTab: HTML");
    }
  }, [selectedCMS]);

  // Debug useEffect to monitor tabs changes
  useEffect(() => {
    console.log("🔍 TABS STATE CHANGED:", tabs);
    console.log("🔍 ACTIVE CODE TAB:", activeCodeTab);
    console.log("🔍 CURRENT CMS:", selectedCMS);
  }, [tabs, activeCodeTab, selectedCMS]);

  // Load current session when currentSessionId changes
  useEffect(() => {
    if (currentSessionId) {
      loadCurrentSession();
    }
  }, [currentSessionId]);

  // Monitor selectedComponent changes for debugging
  useEffect(() => {
    console.log("🔍 selectedComponent changed:", selectedComponent ? selectedComponent.name : "null");
    console.log("🔍 rightPanelOpen:", rightPanelOpen);
    console.log("🔍 generatedComponents length:", generatedComponents.length);
  }, [selectedComponent, rightPanelOpen, generatedComponents]);

  // Monitor tabs changes for debugging
  useEffect(() => {
    console.log("📋 Tabs changed:", tabs, "Active tab:", activeCodeTab);
  }, [tabs, activeCodeTab]);

  // Auto-select latest component when generatedComponents updates
  useEffect(() => {
    console.log("🔄 AUTO-SELECT useEffect triggered! generatedComponents length:", generatedComponents.length);
    console.log("🔍 Current selectedComponent:", selectedComponent ? selectedComponent.name : "null");
    console.log("🔍 Current rightPanelOpen:", rightPanelOpen);
    console.log("🔍 Current selectedCMS:", selectedCMS);
    
    if (generatedComponents.length > 0) {
      const latestComponent = generatedComponents[generatedComponents.length - 1];
      console.log("🎯 Latest component found:", latestComponent.name, "ID:", latestComponent.id);
      console.log("🎯 Latest component code structure:", Object.keys(latestComponent.code || {}));
      
      // Always select the latest component, regardless of current selection
      console.log("📱 FORCE-setting latest component and opening right panel");
      setSelectedComponent(latestComponent);
      setRightPanelOpen(true);
      
      // Set tabs and active tab based on CMS type
      if (selectedCMS === "Adobe EDS") {
        console.log("🟢 Setting EDS tabs: [css, js, mkd_table]");
        setTabs(["css", "js", "mkd_table"]);
        setActiveCodeTab("css");
      } else {
        // AEM tabs
        console.log("🔵 Setting AEM tabs");
        setActiveCodeTab("HTML");
        const tabsTemp = ["HTML", "Sling Model", "Dialog"];
        if (latestComponent.code.clientLib) {
          Object.keys(latestComponent.code.clientLib).forEach(item => {
            if (item !== "css.txt" && item !== "js.txt" && item !== ".content.xml") {
              tabsTemp.push(item);
            }
          });
        }
        setTabs(tabsTemp);
      }
      
      console.log("✅ Auto-selection complete - latest component should now be displayed");
    } else {
      console.log("⚠️ No components to auto-select");
    }
  }, [generatedComponents, selectedCMS]);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (llmButtonRef.current && !llmButtonRef.current.contains(event.target)) {
        setShowLLMDropdown(false);
      }
      if (cmsButtonRef.current && !cmsButtonRef.current.contains(event.target)) {
        setShowCMSDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const loadChatSessions = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/chat/sessions`);
      if (response.data.success) {
        setChatSessions(response.data.sessions);
      }
    } catch (error) {
      console.error("Failed to load chat sessions:", error);
    }
  };

  const loadCurrentSession = async () => {
    if (!currentSessionId) {
      console.warn("No current session ID to load");
      return;
    }

    try {
      const response = await axios.get(`${API_BASE_URL}/chat/sessions/${currentSessionId}`);

      if (response.data.success) {
        const session = response.data.session;

        // Convert messages to the format expected by the UI FIRST
        const formattedMessages = session.messages.map(msg => ({
          id: msg.id,
          text: msg.content,
          image: msg.image_data || null, // Use image_data directly since it already contains the full data URL
          sender: msg.message_type === "user" ? "user" : "ai",
          timestamp: new Date(msg.timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          }),
        }));

        console.log("🖼️ Image data check:", {
          totalMessages: formattedMessages.length,
          messagesWithImages: formattedMessages.filter(m => m.image).length,
          imageDataSamples: formattedMessages
            .filter(m => m.image)
            .map(m => ({
              id: m.id,
              hasImage: !!m.image,
              imagePrefix: m.image ? m.image.substring(0, 50) + "..." : null,
              isValidDataUrl: m.image ? m.image.startsWith("data:image/") : false
            }))
        });

        // Convert components to the format expected by the UI
        const formattedComponents = session.generated_components.map(comp => ({
          id: comp.component_id,
          name: comp.component_name,
          timestamp: new Date(comp.generation_timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          }),
          type: "component",
          code: {
            htl: comp.htl_code,
            slingModel: comp.sling_model_code,
            dialog: comp.dialog_code,
            content_xml: comp.content_xml,
            clientLib: comp.client_lib,
            componentName: comp.component_name,
            slingModelName: comp.sling_model_name
          }
        }));

        // Set the state with both messages and components
        console.log("🔄 Setting messages state with", formattedMessages.length, "messages");
        setMessages(formattedMessages);
        console.log("🔄 Setting generatedComponents state with", formattedComponents.length, "components");
        console.log("🔍 Components being set:", formattedComponents.map(c => ({ id: c.id, name: c.name })));
        setGeneratedComponents(formattedComponents);

        // Clear any previous errors on successful load
        setErrorMessage(null);
        setErrorContext(null);
        
        console.log("✅ Session data loaded, useEffect will handle component selection");
        
        // Add a small delay to ensure state has updated before the useEffect runs
        setTimeout(() => {
          console.log("⏰ Post-load check - generatedComponents length should be:", formattedComponents.length);
        }, 100);
      } else {
        console.error("Failed to load session:", response.data);
      }
    } catch (error) {
      console.error("Failed to load current session:", error);
      // If session doesn't exist, clear current session
      if (error.response?.status === 404) {
        setCurrentSessionId(null);
        setMessages([]);
        setGeneratedComponents([]);
        setSelectedComponent(null);
      }
    }
  };

  const createNewSession = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/chat/sessions`, {
        session_title: sessionTitle || `New Chat - ${new Date().toLocaleDateString()}`,
        user_id: "default_user"
      });

      if (response.data.success) {
        const newSessionId = response.data.session_id;
        setCurrentSessionId(newSessionId);
        setMessages([]);
        setGeneratedComponents([]);
        setSelectedComponent(null);
        setShowNewSessionModal(false);
        setSessionTitle("");

        // Wait a moment for state to update, then refresh sessions list
        setTimeout(() => {
          loadChatSessions();
        }, 100);
      } else {
        console.error("Failed to create session:", response.data);
      }
    } catch (error) {
      console.error("Failed to create new session:", error);
    }
  };

  const deleteSession = async (sessionId, event) => {
    event.stopPropagation(); // Prevent session selection when deleting
    try {
      const response = await axios.delete(`${API_BASE_URL}/chat/sessions/${sessionId}`);
      if (response.data.success) {
        if (currentSessionId === sessionId) {
          setCurrentSessionId(null);
          setMessages([]);
          setGeneratedComponents([]);
          setSelectedComponent(null);
        }
        loadChatSessions(); // Refresh the sessions list
      }
    } catch (error) {
      console.error("Failed to delete session:", error);
    }
  };

  const searchSessions = async () => {
    if (!searchTerm.trim()) {
      loadChatSessions();
      return;
    }

    try {
      const response = await axios.get(`${API_BASE_URL}/chat/sessions/search?q=${encodeURIComponent(searchTerm)}`);
      if (response.data.success) {
        setChatSessions(response.data.sessions);
      }
    } catch (error) {
      console.error("Failed to search sessions:", error);
    }
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setUploadedImage(reader.result);
        e.target.value = "";
      };
      reader.readAsDataURL(file);
    }
  };

  const generateAndPublish = async () => {
    // Open right panel to show build progress
    setRightPanelOpen(true);
    setSelectedComponent(null);
    setErrorMessage(null); // Clear any previous errors
    setErrorContext(null);
    setSuccessMessage(null); // Clear any previous success messages
    setSuccessContext(null);
    
    const reqObj = {
      projectPath: "/Users/vinodhsampath/Code/AI Final Demo/dxp-code-generator/project_code",
      mavenProfile: "autoInstallPackage",
      packagePath: "/Users/vinodhsampath/Code/AI Final Demo/dxp-code-generator/project_code/all/target/aem-guides-wknd.all-2.1.5-SNAPSHOT.zip",
      autoInstall: true,
    };
    setIsLoading(true);
    setLoadingContext("build");
    try {
      const response = await axios.post(apiConfig.getFullUrl(apiConfig.endpoints.buildAemProject), reqObj, {
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Basic bWNwLWFkbWluOkFJSGFja2F0aG9uMTIz",
        },
      });
      
      // Show success message
      console.log("Build completed successfully:", response.data);
      setSuccessMessage("Build and deployment completed successfully! Your components are now available in AEM.");
      setSuccessContext("build");
      
    } catch (error) {
      console.error("Build failed:", error);
      
      // Set error message for display in right panel
      let errorMsg = "Build failed. Please try again.";
      if (error.response?.status === 500) {
        errorMsg = "Internal server error during build. Please check AEM MCP server configuration.";
      } else if (error.response?.status === 404) {
        errorMsg = "Build endpoint not found. Please ensure AEM MCP server is running.";
      } else if (error.response?.data?.message) {
        errorMsg = error.response.data.message;
      } else if (error.message) {
        errorMsg = `Build error: ${error.message}`;
      }
      
      setErrorMessage(errorMsg);
      setErrorContext("build");
      
    } finally {
      setIsLoading(false);
      setLoadingContext(null);
    }
  };

  const handleDownload = () => {
    downloadZipFromBase64(
        selectedComponent?.code?.zip_base64,
        selectedComponent?.code?.file_name
    );
  };

  const handleEdsSendMessage = async () => {
    setLoadingContext("analyze");
    const newMessage = {
      id: Date.now(),
      text: inputMessage,
      image: uploadedImage,
      sender: "user",
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    setMessages([...messages, newMessage]);
    const reqObj = {
      description: inputMessage,
    };
    setIsLoading(true);
    const response = await axios.post(
        apiConfig.getFullUrl(apiConfig.endpoints.generateEdsBlock),
        reqObj
    );
    if (Object.keys(response.data).length === 0) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 2,
          text: "Something went wrong. Please try again.",
          sender: "ai",
          timestamp: new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          }),
        },
      ]);
      setIsLoading(false);
      return;
    }
    const aiResponse = {
      id: Date.now() + 1,
      text: "Here's your generated component.",
      sender: "ai",
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
    setMessages((prev) => [...prev, aiResponse]);
    console.log("response", response);
    setTabs(["css", "js", "mkd_table"]);
    const newComponent = {
      id: Date.now(),
      name:
          response.data.name ||
          `Generated Component ${generatedComponents.length + 1}`,
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
      type: "component",
      code: response.data || "",
    };
    console.log("EDS Response:", response.data);
    setEdsOutput(response.data);
    setGeneratedComponents([newComponent]);

    setSelectedComponent(newComponent);
    setActiveCodeTab("css"); // Set default active tab for EDS
    setInputMessage("");
    setIsLoading(false);
  };

  const handleSendMessage = async () => {
    console.log("🚀 handleSendMessage CALLED!");
    console.log("📝 Input Message Length:", inputMessage.trim().length);
    console.log("🖼️ Has Uploaded Image:", !!uploadedImage);
    
    if (inputMessage.trim() || uploadedImage) {
      console.log("✅ Message validation passed - proceeding...");
      
      // Clear right panel selection when starting new generation (will be restored after generation)
      setSelectedComponent(null);
      setRightPanelOpen(true); // Keep panel open to show progress/results
      // Clear any previous errors
      setErrorMessage(null);
      setErrorContext(null);
      // Clear any previous success messages
      setSuccessMessage(null);
      setSuccessContext(null);
      
      // Create new session if none exists
      if (!currentSessionId) {
        console.log("🆕 No current session - creating new session...");
        setLoadingContext("analyze");
        setIsLoading(true);

        try {
          const tempTitle = inputMessage.substring(0, 50) + (inputMessage.length > 50 ? "..." : "");
          console.log("📡 Making POST request to create session with title:", tempTitle);
          
          const response = await axios.post(`${API_BASE_URL}/chat/sessions`, {
            session_title: tempTitle || `New Chat - ${new Date().toLocaleDateString()}`,
            user_id: "default_user"
          });

          console.log("📨 Session creation response:", response.data);

          if (response.data.success) {
            const newSessionId = response.data.session_id;
            console.log("✅ New session created with ID:", newSessionId);
            setCurrentSessionId(newSessionId);

            // Now send the message with the new session ID
            console.log("📤 Sending message to new session...");
            await sendMessageToSession(newSessionId);

            // Refresh sessions list
            console.log("🔄 Refreshing sessions list...");
            loadChatSessions();
          }
        } catch (error) {
          console.error("❌ Failed to create new session:", error);
          setIsLoading(false);
          setLoadingContext(null);
        }
        return; // Exit here after handling new session creation
      }

      // Send message to existing session
      console.log("📤 Sending message to existing session:", currentSessionId);
      await sendMessageToSession(currentSessionId);
    } else {
      console.log("❌ Message validation failed - no input message or image");
    }
  };

  // Extract the message sending logic into a separate function
  const sendMessageToSession = async (sessionId) => {
    console.log("📡 sendMessageToSession CALLED with sessionId:", sessionId);
    setLoadingContext('analyze');
    setIsLoading(true);

    const formData = new FormData();
    formData.append("componentDesc", inputMessage);
    formData.append("sessionId", sessionId);
    formData.append("userId", "default_user");

    console.log("📝 FormData being sent:");
    console.log("- componentDesc:", inputMessage);
    console.log("- sessionId:", sessionId);
    console.log("- userId: default_user");

    if (uploadedImage) {
      console.log("🖼️ Processing uploaded image...");
      if (typeof uploadedImage === "string" && uploadedImage.startsWith("data:")) {
        const res = await fetch(uploadedImage);
        const blob = await res.blob();
        formData.append("file", blob, "upload.png");
        console.log("✅ Image converted to blob and added to FormData");
      } else {
        formData.append("file", uploadedImage);
        console.log("✅ Image file added to FormData");
      }
    }

    try {
      console.log("📡 Making POST request to:", `${API_BASE_URL}/generate`);
      console.log("🔗 Full URL:", `${API_BASE_URL}/generate`);
      
      const response = await axios.post(`${API_BASE_URL}/generate`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      console.log("📨 Generate response received:", response.data);

      if (response.data.success) {
        console.log("✅ Component generation successful!");
        
        // Reload the current session to get updated messages and components
        console.log("🔄 Reloading current session...");
        await loadCurrentSession();
        
        console.log("🔄 Updating chat sessions list...");
        loadChatSessions(); // Update session list with new timestamp
        
        // Force right panel to open and ensure latest component is selected
        console.log("🎯 FORCE-opening right panel after component generation");
        setRightPanelOpen(true);
        
        // Clear any previous errors
        setErrorMessage(null);
        setErrorContext(null);
      } else {
        console.error("❌ Component generation failed:", response.data);
        setErrorMessage("Component generation failed. Please try again.");
        setErrorContext("generate");
      }

      console.log("🧹 Clearing input fields...");
      setInputMessage("");
      setUploadedImage(null);
    } catch (error) {
      console.error("❌ Error generating component:", error);
      console.error("❌ Error details:", {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        url: error.config?.url
      });
      
      // Set error message for display in right panel
      let errorMsg = "Failed to generate component. Please try again.";
      if (error.response?.status === 500) {
        errorMsg = "Internal server error. Please check the backend service.";
      } else if (error.response?.status === 404) {
        errorMsg = "Service not found. Please ensure the backend is running.";
      } else if (error.response?.data?.message) {
        errorMsg = error.response.data.message;
      } else if (error.message) {
        errorMsg = `Generation error: ${error.message}`;
      }
      
      setErrorMessage(errorMsg);
      setErrorContext("generate");
      
    } finally {
      console.log("🏁 Setting loading states to false...");
      setIsLoading(false);
      setLoadingContext(null);
    }
  };


  const handleRefineComponent = async () => {
    if (!selectedComponentForRefinement || !inputMessage.trim()) return;

    // Clear any previous messages
    setErrorMessage(null);
    setErrorContext(null);
    setSuccessMessage(null);
    setSuccessContext(null);

    setIsRefining(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/refine`, {
        session_id: currentSessionId,
        component_id: selectedComponentForRefinement.id,
        refinement_prompt: inputMessage,
        user_id: "default_user"
      });

      if (response.data.success) {
        // Reload the current session to get the refined component
        await loadCurrentSession();
        loadChatSessions(); // Update session list
        setSelectedComponentForRefinement(null);
      }

      setInputMessage("");
    } catch (error) {
      console.error("Error refining component:", error);
    } finally {
      setIsRefining(false);
    }
  };

  const handleCopyCodeSection = (section) => {
    if (selectedComponent) {
      const code = selectedCMS === "Adobe EDS" 
        ? getCodeForEdsSelection(section, selectedComponent)
        : getCodeForSection(section, selectedComponent);
      navigator.clipboard.writeText(code);
      setCopiedSection(section);
      setTimeout(() => setCopiedSection(null), 2000);
    }
  };

  const getCodeForEdsSelection = (section, component) => {
    if (!component) return "";
    
    const codeData = component.code;
    if (!codeData) return "";
    
    console.log("🔍 EDS Code Selection - Section:", section);
    console.log("🔍 EDS Code Data:", codeData);
    
    switch (section) {
      case "css":
        return codeData.css || "";
      case "js":
        return codeData.js || "";
      case "mkd_table":
        return codeData.mkd_table || "";
      default:
        return "";
    }
  };

  const getCodeForSection = (section, component) => {

    if (!component) return "";

    const codeData = component.code;
    if (!codeData) return "";

    switch (section) {
      case "HTML":
        return codeData.htl || "";
      case "Sling Model":
        return codeData.slingModel || "";
      case "Dialog":
        return codeData.dialog || "";
      default:
        const clientLibSection = codeData.clientLib?.[section];
        return clientLibSection?.fileContents?.replace("\\n", "\n") || clientLibSection || "";
    }
  };

  const handlePreview = () => {
    if (!selectedComponent) return;
    setPreviewNodesFromCodeData(selectedComponent);
  };

  // EDS-specific handlers
  const handleEDSPushToGit = async () => {
    if (!selectedComponent) return;
    
    console.log("🚀 Pushing EDS component to Git:", selectedComponent.name);
    
    // Set loading state for Git push
    setIsLoading(true);
    setLoadingContext("git_push");
    
    try {
      const pushUrl = apiConfig.getFullUrl(apiConfig.endpoints.pushEdsToGit);
      console.log("📡 Making request to Git push service:", pushUrl);
      
      const requestData = {
        block_name: selectedComponent.name,
        files: {
          html: selectedComponent.code?.mkd_table || '', // EDS uses markdown table as HTML structure
          css: selectedComponent.code?.css || '',
          js: selectedComponent.code?.js || ''
        },
        metadata: {
          sessionId: currentSessionId,
          author: "DXP Component Generator",
          description: `EDS block generated for ${selectedComponent.name}`,
          generated_at: new Date().toISOString()
        },
        create_pr: true
      };
      
      const response = await axios.post(pushUrl, requestData, {
        headers: { 
          "Content-Type": "application/json",
        },
        timeout: 60000 // 60 second timeout for Git operations
      });
      
      if (response.data.success) {
        const result = response.data;
        let successMsg = `EDS block '${result.block_name}' successfully pushed to Git!`;
        
        if (result.pull_request_url) {
          successMsg += ` Pull Request created: #${result.pull_request_number}`;
        }
        
        setSuccessMessage(successMsg);
        setSuccessContext("git_push");
        
        // Log useful URLs for debugging
        console.log("🎉 Git push successful!");
        console.log("📄 Commit URL:", result.commit_url);
        console.log("🌿 Branch URL:", result.branch_url);
        if (result.pull_request_url) {
          console.log("🔀 Pull Request URL:", result.pull_request_url);
        }
        
        // Reload session to get updated messages if needed
        if (currentSessionId) {
          await loadCurrentSession();
        }
        
        setTimeout(() => {
          setSuccessMessage(null);
          setSuccessContext(null);
        }, 10000); // Show success for 10 seconds for Git operations
      } else {
        setErrorMessage(response.data.message || "Git push failed");
        setErrorContext("git_push");
        
        setTimeout(() => {
          setErrorMessage(null);
          setErrorContext(null);
        }, 5000);
      }
    } catch (error) {
      console.error("❌ Error pushing EDS component to Git:", error);
      
      let errorMsg = "Failed to push EDS component to Git. Please try again.";
      if (error.code === 'ECONNREFUSED') {
        errorMsg = "Git service is not available. Please check backend configuration.";
      } else if (error.response?.status === 500) {
        errorMsg = "Git service error. Please check GitHub token and repository configuration.";
      } else if (error.response?.status === 400) {
        errorMsg = "Invalid request data. Please check component files.";
      } else if (error.response?.data?.detail) {
        errorMsg = typeof error.response.data.detail === 'string' 
          ? error.response.data.detail 
          : error.response.data.detail.message || "Git push failed";
      } else if (error.response?.data?.message) {
        errorMsg = error.response.data.message;
      } else if (error.message) {
        errorMsg = `Git error: ${error.message}`;
      }
      
      setErrorMessage(errorMsg);
      setErrorContext("git_push");
      
      setTimeout(() => {
        setErrorMessage(null);
        setErrorContext(null);
      }, 5000);
    } finally {
      setIsLoading(false);
      setLoadingContext(null);
    }
  };

  const handleEDSPreview = () => {
    if (!selectedComponent) return;
    
    // For EDS, create a simple HTML preview with CSS and JS
    console.log("👀 Opening EDS preview for:", selectedComponent.name);
    
    // Create a preview blob with EDS content
    const css = selectedComponent.code?.css || '';
    const js = selectedComponent.code?.js || '';
    const mkdTable = selectedComponent.code?.mkd_table || '';
    
    // Create a simple HTML preview
    const htmlContent = `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EDS Preview - ${selectedComponent.name}</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          .preview-section { margin-bottom: 30px; padding: 15px; border: 1px solid #ddd; border-radius: 8px; }
          .preview-title { font-weight: bold; margin-bottom: 10px; color: #333; }
          pre { background: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; }
          ${css}
        </style>
      </head>
      <body>
        <h1>EDS Block Preview: ${selectedComponent.name}</h1>
        
        ${mkdTable ? `
          <div class="preview-section">
            <div class="preview-title">Markdown Table:</div>
            <pre>${mkdTable}</pre>
          </div>
        ` : ''}
        
        ${css ? `
          <div class="preview-section">
            <div class="preview-title">CSS Styles:</div>
            <pre>${css}</pre>
          </div>
        ` : ''}
        
        ${js ? `
          <div class="preview-section">
            <div class="preview-title">JavaScript:</div>
            <pre>${js}</pre>
          </div>
        ` : ''}
        
        <script>
          ${js}
        </script>
      </body>
      </html>
    `;
    
    // Create blob and open in new window
    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank');
    
    // Clean up the URL after a delay
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  // AEM Handler Functions
  const handleAEMBuildDeploy = async () => {
    if (!selectedComponent) return;
    
    console.log("🔨 Building and deploying AEM component:", selectedComponent.name);
    
    // Set loading state for build & deploy
    setIsLoading(true);
    setLoadingContext("build");
    
    try {
      // Use the buildAemProject endpoint from apiConfig
      const buildUrl = apiConfig.getFullUrl(apiConfig.endpoints.buildAemProject);
      console.log("📡 Making request to AEM Builder service:", buildUrl);
      
      const requestData = {
        session_id: currentSessionId,
        component_id: selectedComponent.id,
        component_name: selectedComponent.name,
        component_code: {
          htl: selectedComponent.code?.htl,
          slingModel: selectedComponent.code?.slingModel,
          dialog: selectedComponent.code?.dialog,
          clientLib: selectedComponent.code?.clientLib,
          content_xml: selectedComponent.code?.content_xml
        },
        target_environment: "development",
        user_id: "default_user",
        // Add project path information for AEM Builder
        projectPath: "/Users/vinodhsampath/Code/AI Final Demo/dxp-code-generator/project_code",
        mavenProfile: "autoInstallPackage",
        packagePath: "/Users/vinodhsampath/Code/AI Final Demo/dxp-code-generator/project_code/all/target/aem-guides-wknd.all-2.1.5-SNAPSHOT.zip",
        autoInstall: true
      };
      
      // Prepare headers with optional Basic Auth
      const headers = { "Content-Type": "application/json" };
      try {
        const envAuth = process.env.REACT_APP_AEM_BUILDER_BASIC_AUTH;
        const lsAuth = typeof window !== 'undefined' ? localStorage.getItem('AEM_BUILDER_BASIC_AUTH') : null;
        const raw = envAuth || lsAuth;
        if (raw) {
          // Accept either the base64 token or full "Basic <token>"
          headers["Authorization"] = raw.startsWith("Basic ") ? raw : `Basic ${raw}`;
        }
      } catch (_) {
        // no-op if localStorage is unavailable
      }

      const response = await axios.post(buildUrl, requestData, {
        headers,
        timeout: 60000 // 60 second timeout for build process
      });
      
      if (response.data.success) {
        setSuccessMessage(response.data.message || "AEM component built and deployed successfully!");
        setSuccessContext("aem_build_deploy");
        
        // If there's a deployment URL or log, you could show it
        if (response.data.deployment_url) {
          console.log("🚀 Deployment URL:", response.data.deployment_url);
        }
        
        // Reload session to get updated messages if needed
        if (currentSessionId) {
          await loadCurrentSession();
        }
        
        setTimeout(() => {
          setSuccessMessage(null);
          setSuccessContext(null);
        }, 5000);
      } else {
        setErrorMessage(response.data.error || "AEM build and deployment failed");
        setErrorContext("aem_build_deploy");
        
        setTimeout(() => {
          setErrorMessage(null);
          setErrorContext(null);
        }, 5000);
      }
    } catch (error) {
      console.error("❌ Error building/deploying AEM component:", error);
      
      let errorMsg = "Failed to build and deploy AEM component. Please try again.";
      if (error.code === 'ECONNREFUSED') {
        errorMsg = "AEM Builder service is not running. Please start the AEM Builder service on port 8080.";
      } else if (error.response?.status === 500) {
        errorMsg = "AEM Builder service error. Please check the service logs.";
      } else if (error.response?.status === 404) {
        errorMsg = "AEM Builder endpoint not found. Please check service configuration.";
      } else if (error.response?.data?.detail) {
        errorMsg = typeof error.response.data.detail === 'string' 
          ? error.response.data.detail 
          : error.response.data.detail.error || "Build and deployment failed";
      } else if (error.response?.data?.message) {
        errorMsg = error.response.data.message;
      } else if (error.message) {
        errorMsg = `Build error: ${error.message}`;
      }
      
      setErrorMessage(errorMsg);
      setErrorContext("aem_build_deploy");
      
      setTimeout(() => {
        setErrorMessage(null);
        setErrorContext(null);
      }, 5000);
    } finally {
      setIsLoading(false);
      setLoadingContext(null);
    }
  };

  const handleAEMPreview = () => {
    if (!selectedComponent) return;
    
    // Use the existing preview modal functionality
    console.log("👀 Opening AEM preview for:", selectedComponent.name);
    setPreviewNodesFromCodeData(selectedComponent);
  };

  const handleAEMRefine = () => {
    if (!selectedComponent) return;
    
    // Set the current component for refinement (this will trigger the chat interface)
    console.log("✨ Setting component for refinement:", selectedComponent.name);
    setSelectedComponentForRefinement(selectedComponent);
    
    // Clear right panel to focus on chat refinement
    setSelectedComponent(null);
    setRightPanelOpen(false);
  };

  const setPreviewNodesFromCodeData = (codeData) => {
    // Prioritize image analysis generated HTML/CSS over AEM-specific code
    console.log("🎨 Preview - checking for image analysis code:", {
      hasHtmlCode: !!codeData?.code?.htmlCode,
      hasCssCode: !!codeData?.code?.cssCode,
      hasDesignAnalysis: !!codeData?.code?.designAnalysis,
      hasHtl: !!codeData?.code?.htl,
      hasClientLib: !!codeData?.code?.clientLib
    });

    // Check if we have image-analysis generated HTML/CSS
    if (codeData?.code?.htmlCode && codeData?.code?.cssCode) {
      console.log("✅ Using image analysis generated HTML and CSS for preview");
      setHtmlNode(codeData.code.htmlCode);
      setCssNode(codeData.code.cssCode);
    } else {
      console.log("⚪ No image analysis code found, falling back to AEM HTL/CSS");
      // Fallback to existing AEM HTL/CSS logic
      setHtmlNode(codeData?.code?.htl || "");

      const cssFiles = Object.keys(codeData.code?.clientLib || {}).filter((key) =>
          key.startsWith("css/")
      );
      if (cssFiles.length > 0) {
        const cssFileContent = codeData.code.clientLib[cssFiles[0]].fileContents || codeData.code.clientLib[cssFiles[0]] || "";
        setCssNode(cssFileContent);
      } else {
        setCssNode("");
      }
    }
    
    setShowPreviewModal(true);
  };

  const getComponentIcon = (type) => {
    switch (type) {
      case "form":
        return <FileCode className="w-4 h-4" />;
      case "layout":
        return <Layout className="w-4 h-4" />;
      case "component":
        return <Component className="w-4 h-4" />;
      default:
        return <Layers className="w-4 h-4" />;
    }
  };

  // Styles object
  const styles = {
    wrapper: {
      display: "flex",
      flexDirection: "column",
      height: "100vh",
      backgroundColor: "#f9fafb",
    },
    header: {
      background: "linear-gradient(135deg, rgba(40, 40, 40) 0%, rgb(0, 0, 0) 100%",
      padding: "8px 16px",
      boxShadow: "0 2px 4px -1px rgba(0, 0, 0, 0.1)",
      position: "relative",
      overflow: "hidden",
    },
    headerContent: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      position: "relative",
      zIndex: 1,
    },
    headerLeft: {
      display: "flex",
      alignItems: "center",
      gap: "16px",
    },
    headerTitle: {
      fontSize: "22px",
      fontWeight: "600",
      color: "white",
      letterSpacing: "-0.3px",
      textShadow: "0 1px 2px rgba(0,0,0,0.1)",
    },
    headerSubtitle: {
      fontSize: "12px",
      color: "#e0e7ff",
      marginTop: "2px",
    },
    headerOptions: {
      display: "flex",
      gap: "12px",
      alignItems: "center",
    },
    dropdown: {
      position: "relative",
    },
    dropdownButton: {
            background: "linear-gradient(40deg, rgba(40, 40, 40) 0%, rgb(0, 0, 0) 100%",
                  border: "1px solid #374151",
      borderRadius: "6px",
      padding: "8px 12px",
      color: "white",
      display: "flex",
      alignItems: "center",
      gap: "8px",
      cursor: "pointer",
      fontSize: "14px",
      fontWeight: "500",
      transition: "all 0.2s",
    },
    dropdownMenu: {
      position: "absolute",
      top: "100%",
      right: 0,
      marginTop: "8px",
      background: "linear-gradient(135deg, #18181b 0%, #000000 100%)",
      borderRadius: "8px",
      boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
      border: "1px solid #1f2937",
      minWidth: "200px",
      zIndex: 50,
    },
    dropdownItem: {
      padding: "10px 16px",
      cursor: "pointer",
      fontSize: "14px",
      color: "#f3f4f6",
      transition: "background 0.2s",
      borderBottom: "1px solid #4b5563",
      backgroundColor: "transparent",
    },
    sparkleAnimation: {
      position: "absolute",
      top: "20px",
      right: "20px",
      opacity: 0.1,
      animation: "sparkle 3s ease-in-out infinite",
      stroke: "#ffffff",
    },
    mainContent: {
      display: "flex",
      flex: 1,
      overflow: "hidden",
    },
    leftPanel: {
      width: leftPanelOpen ? "25%" : "48px",
      minWidth: leftPanelOpen ? "200px" : "48px",
      maxWidth: leftPanelOpen ? "400px" : "48px",
      backgroundColor: "white",
      borderRight: "1px solid #e5e7eb",
      transition: "all 0.3s ease",
      display: "flex",
      flexDirection: "column",
      flexBasis: leftPanelOpen ? "25%" : "48px",
      flexGrow: 0,
      flexShrink: 0,
    },
    panelHeader: {
      padding: "10px",
      borderBottom: "1px solid #e5e7eb",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
    },
    headerTitleSection: {
      display: "flex",
      alignItems: "center",
      gap: "8px",
    },
    toggleButton: {
      padding: "4px",
      background: "transparent",
      border: "none",
      borderRadius: "4px",
      cursor: "pointer",
      transition: "background 0.2s",
    },
    searchContainer: {
      padding: "6px 12px",
      borderBottom: "1px solid #e5e7eb",
    },
    searchInput: {
      width: "100%",
      maxWidth: "100%",
      boxSizing: "border-box",
      padding: "6px 10px",
      border: "1px solid #d1d5db",
      borderRadius: "6px",
      fontSize: "14px",
      outline: "none",
    },
    sessionsList: {
      flex: 1,
      overflowY: "auto",
      padding: "8px",
      display: "flex",
      flexDirection: "column",
      gap: "4px",
    },
    sessionItem: {
      padding: "10px",
      borderRadius: "8px",
      cursor: "pointer",
      transition: "all 0.2s",
      border: "1px solid transparent",
      position: "relative",
    },
    sessionItemSelected: {
      backgroundColor: "#dbeafe",
      border: "1px solid #93c5fd",
    },
    sessionTitle: {
      fontWeight: "500",
      color: "#1f2937",
      fontSize: "14px",
      marginBottom: "4px",
    },
    sessionMeta: {
      fontSize: "12px",
      color: "#6b7280",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
    },
    deleteButton: {
      position: "absolute",
      top: "8px",
      right: "8px",
      background: "transparent",
      border: "none",
      color: "#ef4444",
      cursor: "pointer",
      padding: "4px",
      borderRadius: "4px",
      opacity: 0,
      transition: "opacity 0.2s",
    },
    newSessionButton: {
      margin: "10px",
      padding: "10px",
      backgroundColor: "#3b82f6",
      color: "white",
      border: "none",
      borderRadius: "8px",
      cursor: "pointer",
      display: "flex",
      alignItems: "center",
      gap: "8px",
      fontSize: "14px",
      fontWeight: "500",
    },
    middlePanel: {
      flex: 1,
      display: "flex",
      flexDirection: "column",
      minWidth: 0,
    },
    chatHeader: {
      padding: "12px",
      borderBottom: "1px solid #e5e7eb",
      backgroundColor: "white",
    },
    chatArea: {
      flex: 1,
      overflowY: "auto",
      padding: "12px",
      display: "flex",
      flexDirection: "column",
      gap: "12px",
    },
    emptyState: {
      textAlign: "center",
      color: "#6b7280",
      marginTop: "40px",
    },
    inputArea: {
      padding: "12px",
      backgroundColor: "white",
      borderTop: "1px solid #e5e7eb",
    },
    inputContainer: {
      display: "flex",
      gap: "6px",
      alignItems: "center",
    },
    inputWrapper: {
      flex: 1,
      display: "flex",
      gap: "6px",
      alignItems: "center",
    },
    textInput: {
      flex: 1,
      padding: "12px 16px",
      border: "none",
      borderRadius: "999px",
      fontSize: "15px",
      background: "#f3f4f6",
      color: "#1f2937",
      outline: "none",
      boxShadow: "0 1px 4px rgba(0,0,0,0.04)",
      fontWeight: 500,
      letterSpacing: "0.01em",
      transition: "box-shadow 0.2s, background 0.2s, border 0.2s",
      marginRight: 6,
    },
    uploadButton: {
      width: 36,
      height: 36,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: "#f3f4f6",
      borderRadius: "50%",
      cursor: "pointer",
      border: "none",
      transition: "background 0.2s, box-shadow 0.2s, transform 0.1s",
      marginRight: 6,
      outline: "none",
      boxShadow: "0 1px 4px rgba(0,0,0,0.04)",
    },
    sendButton: {
      padding: "8px 14px 8px 10px",
      background: "linear-gradient(90deg, #2563eb 0%, #3b82f6 100%)",
      color: "#fff",
      border: "none",
      borderRadius: "999px",
      cursor: "pointer",
      display: "flex",
      alignItems: "center",
      gap: "6px",
      fontWeight: 700,
      fontSize: "14px",
      boxShadow: "0 2px 8px rgba(59,130,246,0.10)",
      letterSpacing: "0.02em",
      transition: "background 0.2s, box-shadow 0.2s, transform 0.1s",
      outline: "none",
    },
    rightPanel: {
      flexBasis: "50%",
      flexGrow: 1,
      flexShrink: 1,
      maxWidth: "40%",
      backgroundColor: "#ffffff",
      flex: 1, // Make right panel take equal space as middle
      background: "linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)",
      color: "#1f2937",
      transition: "all 0.3s ease",
      display: "flex",
      flexDirection: "column",
      minWidth: 0,
      borderLeft: "1px solid #e5e7eb",
    },
    buildDeployButton: {
      padding: "8px 12px",
      color: "white",
      border: "none",
      borderRadius: "6px",
      cursor: "pointer",
      display: "flex",
      alignItems: "center",
      gap: "6px",
      fontSize: "13px",
      fontWeight: "500",
      transition: "background 0.2s",
    },
    codeTabs: {
      display: "flex",
      borderBottom: "1px solid #e5e7eb",
      backgroundColor: "#f8fafc",
      padding: "0 16px",
      overflow: "auto",
    },
    codeTab: {
      padding: "12px 16px",
      background: "transparent",
      border: "none",
      color: "#6b7280",
      cursor: "pointer",
      fontSize: "14px",
      fontWeight: "500",
      borderBottom: "3px solid transparent",
      transition: "all 0.2s ease",
      whiteSpace: "nowrap",
      minWidth: "fit-content",
      borderRadius: "6px 6px 0 0",
      marginRight: "4px",
    },
    codeTabActive: {
      color: "#1f2937",
      borderBottomColor: "#3b82f6",
      backgroundColor: "#ffffff",
      boxShadow: "0 -2px 8px rgba(0,0,0,0.1)",
      zIndex: 1,
      fontWeight: "600",
    },
    codeDisplay: {
      flex: 1,
      overflowY: "auto",
      padding: "16px",
      width: "100%",
      maxWidth: "100%",
      boxSizing: "border-box",
      wordBreak: "break-word",
      whiteSpace: "pre-wrap",
      backgroundColor: "#ffffff",
      color: "#1f2937",
    },
    codeBlock: {
      fontSize: "14px",
      lineHeight: "1.6",
      fontFamily: "'Fira Code', 'Monaco', 'Consolas', monospace",
      whiteSpace: "pre-wrap",
      wordBreak: "break-word",
      width: "100%",
      maxWidth: "100%",
      boxSizing: "border-box",
      backgroundColor: "#f8fafc",
      padding: "16px",
      borderRadius: "8px",
      border: "1px solid #e5e7eb",
      color: "#374151",
    },
    copyButton: {
      padding: "8px 12px",
      background: "#f3f4f6",
      border: "1px solid #d1d5db",
      borderRadius: "6px",
      cursor: "pointer",
      color: "#374151",
      display: "flex",
      alignItems: "center",
      gap: "8px",
      transition: "all 0.2s",
      fontSize: "12px",
      fontWeight: "500",
    },
    imagePreview: {
      marginBottom: "12px",
      position: "relative",
      display: "inline-block",
    },
    removeImageButton: {
      position: "absolute",
      top: "-8px",
      right: "-8px",
      backgroundColor: "#ef4444",
      color: "white",
      borderRadius: "50%",
      padding: "4px",
      border: "none",
      cursor: "pointer",
    },
    refinementBanner: {
      backgroundColor: "#fef3c7",
      border: "1px solid #f59e0b",
      borderRadius: "8px",
      padding: "12px",
      margin: "0 0 12px 0",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
    },
    refinementText: {
      color: "#92400e",
      fontSize: "14px",
      fontWeight: "500",
    },
    refinementButton: {
      background: "transparent",
      border: "none",
      color: "#92400e",
      cursor: "pointer",
      padding: "4px",
    },
    // Modal styles
    modal: {
      position: "fixed",
      top: 0,
      left: 0,
      width: "100vw",
      height: "100vh",
      backgroundColor: "rgba(0,0,0,0.5)",
      zIndex: 1000,
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
    },
    modalContent: {
      backgroundColor: "white",
      borderRadius: "12px",
      padding: "24px",
      maxWidth: "400px",
      width: "90%",
      overflow: "auto",
    },
    modalHeader: {
      fontSize: "18px",
      fontWeight: "600",
      marginBottom: "16px",
    },
    modalInput: {
      width: "100%",
      maxWidth: "100%",
      boxSizing: "border-box",
      padding: "12px",
      border: "1px solid #d1d5db",
      borderRadius: "8px",
      fontSize: "14px",
      marginBottom: "16px",
      outline: "none",
    },
    modalButtons: {
      display: "flex",
      gap: "8px",
      justifyContent: "flex-end",
    },
    modalButton: {
      padding: "8px 16px",
      border: "none",
      borderRadius: "6px",
      cursor: "pointer",
      fontSize: "14px",
      fontWeight: "500",
    },
    modalButtonPrimary: {
      backgroundColor: "#3b82f6",
      color: "white",
    },
    modalButtonSecondary: {
      backgroundColor: "#e5e7eb",
      color: "#374151",
    },
  };

  const sparkleStyle = `
    @keyframes sparkle {
      0%, 100% { transform: scale(1) rotate(0deg); opacity: 0.1; }
      50% { transform: scale(1.2) rotate(180deg); opacity: 0.3; }
    }
  `;

  return (
      <>
        {(isLoading || isRefining) && (
            <div
                style={{
                  position: "fixed",
                  top: 0,
                  left: rightPanelOpen ? "60%" : 0, // Leave space for right panel if open
                  width: rightPanelOpen ? "40%" : "100vw", // Adjust width based on panel state
                  height: "100vh",
                  backgroundColor: "rgba(0, 0, 0, 0.5)",
                  zIndex: 1000,
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center",
                  alignItems: "center",
                }}
            >
              <div
                  style={{
                    width: "64px",
                    height: "64px",
                    border: "6px solid #e5e7eb",
                    borderTop: "6px solid #3b82f6",
                    borderRadius: "50%",
                    animation: "spin 1s linear infinite",
                    marginBottom: "16px",
                  }}
              ></div>
              <p
                  style={{
                    color: "#fff",
                    fontSize: "16px",
                    fontWeight: "500",
                    fontFamily: "sans-serif",
                    letterSpacing: "0.5px",
                  }}
              >
                {loadingContext === 'build'
                    ? 'Your code is being built & deploying to AEM...'
                    : isRefining
                        ? 'Refining your component...'
                        : loadingContext === 'analyze' && selectedCMS === 'Adobe EDS'
                        ? 'Generating EDS block. Please wait...'
                        : loadingContext === 'analyze' && selectedCMS === 'Adobe Experience Manager'
                        ? 'Generating AEM component. Please wait...'
                        : 'Analyzing your request. Please wait...'}
              </p>
              <style>
                {`@keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }`}
              </style>
            </div>
        )}

        <style>{sparkleStyle}</style>
        <style>{customScrollbar}</style>

        <div style={styles.wrapper}>
          {/* Fancy Header with LLM and CMS Dropdowns */}
          <header style={styles.header}>
            <div style={styles.headerContent}>
              <div style={styles.headerLeft}>
                <Component size={32} color="white" />
                <div>
                  <h1 style={styles.headerTitle}>DXP Component Generator</h1>
                  <p style={styles.headerSubtitle}>
                    AI-Powered Component Creation with Chat History
                  </p>
                </div>
              </div>
            </div>
          </header>

          {/* Main Content */}
          <div style={styles.mainContent}>
            {/* Left Panel - Chat History */}
            <div style={styles.leftPanel}>
              <div style={styles.panelHeader}>
                {leftPanelOpen && (
                    <div style={styles.headerTitleSection}>
                      <History className="w-5 h-5" style={{ color: "#4b5563" }} />
                      <h2 style={{ fontWeight: "600", color: "#1f2937" }}>
                        Chat History
                      </h2>
                    </div>
                )}
                <button
                    onClick={() => setLeftPanelOpen(!leftPanelOpen)}
                    style={styles.toggleButton}
                    onMouseEnter={(e) => (e.target.style.backgroundColor = "#f3f4f6")}
                    onMouseLeave={(e) => (e.target.style.backgroundColor = "transparent")}
                >
                  {leftPanelOpen ? (
                      <ChevronLeft className="w-5 h-5" />
                  ) : (
                      <ChevronRight className="w-5 h-5" />
                  )}
                </button>
              </div>

              {leftPanelOpen && (
                  <>
                    {/* Search */}
                    <div style={styles.searchContainer}>
                      <div style={{ position: "relative" }}>
                        <input
                            type="text"
                            placeholder="Search sessions..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            onKeyPress={(e) => e.key === "Enter" && searchSessions()}
                            style={styles.searchInput}
                        />
                        <button
                            onClick={searchSessions}
                            style={{
                              position: "absolute",
                              right: "8px",
                              top: "50%",
                              transform: "translateY(-50%)",
                              background: "transparent",
                              border: "none",
                              cursor: "pointer",
                            }}
                        >
                          <Search className="w-4 h-4" style={{ color: "#6b7280" }} />
                        </button>
                      </div>
                    </div>

                    {/* New Session Button */}
                    <div>
                      <button
                          onClick={() => setShowNewSessionModal(true)}
                          style={styles.newSessionButton}
                          onMouseEnter={(e) => (e.target.style.backgroundColor = "#2563eb")}
                          onMouseLeave={(e) => (e.target.style.backgroundColor = "#3b82f6")}
                      >
                        <Plus className="w-4 h-4" />
                        New Chat
                      </button>
                    </div>

                    {/* Sessions List */}
                    <div style={styles.sessionsList} className="dxp-scrollbar">
                      {chatSessions.map((session) => (
                          <div
                              key={session.session_id}
                              onClick={() => {
                                setCurrentSessionId(session.session_id);
                                setErrorMessage(null);
                                setErrorContext(null);
                              }}
                              style={{
                                ...styles.sessionItem,
                                ...(currentSessionId === session.session_id
                                    ? styles.sessionItemSelected
                                    : {}),
                                backgroundColor:
                                    currentSessionId === session.session_id
                                        ? "#dbeafe"
                                        : "#f9fafb",
                              }}
                              onMouseEnter={(e) => {
                                if (currentSessionId !== session.session_id) {
                                  e.target.style.backgroundColor = "#f3f4f6";
                                }
                                const deleteBtn = e.currentTarget.querySelector('.delete-btn');
                                if (deleteBtn) deleteBtn.style.opacity = '1';
                              }}
                              onMouseLeave={(e) => {
                                if (currentSessionId !== session.session_id) {
                                  e.target.style.backgroundColor = "#f9fafb";
                                }
                                const deleteBtn = e.currentTarget.querySelector('.delete-btn');
                                if (deleteBtn) deleteBtn.style.opacity = '0';
                              }}
                          >
                            <button
                                className="delete-btn"
                                onClick={(e) => deleteSession(session.session_id, e)}
                                style={styles.deleteButton}
                            >
                              <Trash2 className="w-3 h-3" />
                            </button>

                            <div style={styles.sessionTitle}>
                              {session.session_title}
                            </div>
                            <div style={styles.sessionMeta}>
                        <span>
                          {session.message_count} messages, {session.component_count} components
                        </span>
                              <span>
                          {new Date(session.updated_at).toLocaleDateString()}
                        </span>
                            </div>
                          </div>
                      ))}

                      {chatSessions.length === 0 && (
                          <div style={{
                            textAlign: "center",
                            color: "#6b7280",
                            fontSize: "14px",
                            padding: "20px",
                          }}>
                            {searchTerm ? "No sessions found" : "No chat sessions yet"}
                          </div>
                      )}
                    </div>
                  </>
              )}
            </div>

            {/* Middle Panel - Chat Interface */}
            <div style={styles.middlePanel}>
              {/* Chat Header */}
              <div style={styles.chatHeader}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <div>
                    <h1 style={{ fontSize: "20px", fontWeight: "600", color: "#1f2937" }}>
                      {currentSessionId ?
                          chatSessions.find(s => s.session_id === currentSessionId)?.session_title || "Chat Session"
                          : "Select or Create a Chat Session"
                      }
                    </h1>
                    <p style={{ fontSize: "14px", color: "#6b7280", marginTop: "4px" }}>
                      Using {selectedLLM} for {selectedCMS}
                    </p>
                    {/* LLM and CMS Selection Dropdowns */}
                    <div style={styles.headerOptions}>
                      {/* LLM Dropdown */}
                      <div style={styles.dropdown} ref={llmButtonRef}>
                        <button
                            style={styles.dropdownButton}
                            onClick={() => {
                              setShowLLMDropdown(!showLLMDropdown);
                              setShowCMSDropdown(false);
                            }}
                            onMouseEnter={(e) => (e.target.style.backgroundColor = "#374151")}
                            onMouseLeave={(e) => (e.target.style.backgroundColor = "#1f2937")}
                        >
                          <Cpu size={16} />
                          {selectedLLM}
                          <ChevronDown size={16} />
                        </button>
                        {showLLMDropdown && (
                            <div style={styles.dropdownMenu}>
                              {llmOptions.map((llm, index) => (
                                  <div
                                      key={llm}
                                      style={{
                                        ...styles.dropdownItem,
                                        borderBottom:
                                            index === llmOptions.length - 1
                                                ? "none"
                                                : "1px solid #4b5563",
                                        backgroundColor:
                                            selectedLLM === llm
                                                ? "#4b5563"
                                                : "transparent",
                                      }}
                                      onClick={() => {
                                        setSelectedLLM(llm);
                                        setShowLLMDropdown(false);
                                      }}
                                      onMouseEnter={(e) => {
                                        if (selectedLLM !== llm) {
                                          e.currentTarget.style.backgroundColor = "#4b5563";
                                        }
                                      }}
                                      onMouseLeave={(e) => {
                                        if (selectedLLM !== llm) {
                                          e.currentTarget.style.backgroundColor = "transparent";
                                        }
                                      }}
                                  >
                                    {llm}
                                  </div>
                              ))}
                            </div>
                        )}
                      </div>

                      {/* CMS Dropdown */}
                      <div style={styles.dropdown} ref={cmsButtonRef}>
                        <button
                            style={styles.dropdownButton}
                            onClick={() => {
                              setShowCMSDropdown(!showCMSDropdown);
                              setShowLLMDropdown(false);
                            }}
                            onMouseEnter={(e) => (e.target.style.backgroundColor = "#374151")}
                            onMouseLeave={(e) => (e.target.style.backgroundColor = "#1f2937")}
                        >
                          <Database size={16} />
                          {selectedCMS}
                          <ChevronDown size={16} />
                        </button>
                        {showCMSDropdown && (
                            <div style={styles.dropdownMenu}>
                              {cmsOptions.map((cms, index) => (
                                  <div
                                      key={cms}
                                      style={{
                                        ...styles.dropdownItem,
                                        borderBottom:
                                            index === cmsOptions.length - 1
                                                ? "none"
                                                : "1px solid #4b5563",
                                        backgroundColor:
                                            selectedCMS === cms
                                                ? "#4b5563"
                                                : "transparent",
                                      }}
                                      onClick={() => {
                                        setSelectedCMS(cms);
                                        setShowCMSDropdown(false);
                                      }}
                                      onMouseEnter={(e) => {
                                        if (selectedCMS !== cms) {
                                          e.currentTarget.style.backgroundColor = "#4b5563";
                                        }
                                      }}
                                      onMouseLeave={(e) => {
                                        if (selectedCMS !== cms) {
                                          e.currentTarget.style.backgroundColor = "transparent";
                                        }
                                      }}
                                  >
                                    {cms}
                                  </div>
                              ))}
                            </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Component Refinement Banner */}
                {selectedComponentForRefinement && (
                    <div style={styles.refinementBanner}>
                  <span style={styles.refinementText}>
                    Refining: {selectedComponentForRefinement.name}
                  </span>
                      <button
                          onClick={() => setSelectedComponentForRefinement(null)}
                          style={styles.refinementButton}
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                )}
              </div>

              {/* Chat Area */}
              <div style={styles.chatArea} className="dxp-scrollbar">
                {!currentSessionId && (
                    <div style={styles.emptyState}>
                      <MessageSquare
                          className="w-16 h-16"
                          style={{ margin: "0 auto 16px", color: "#d1d5db" }}
                      />
                      <p style={{ fontSize: "18px" }}>
                        Create a new chat session to start generating components
                      </p>
                      <p style={{ fontSize: "14px", marginTop: "8px" }}>
                        You can describe what you need or upload an image reference
                      </p>
                    </div>
                )}

                {currentSessionId && messages.length === 0 && (
                    <div style={styles.emptyState}>
                      <Component
                          className="w-16 h-16"
                          style={{ margin: "0 auto 16px", color: "#d1d5db" }}
                      />
                      <p style={{ fontSize: "18px" }}>
                        Start a conversation to generate components
                      </p>
                      <p style={{ fontSize: "14px", marginTop: "8px" }}>
                        You can describe what you need or upload an image reference
                      </p>
                    </div>
                )}

                {messages.map((message) => {
                  const isUser = message.sender === "user";
                  return (
                      <div
                          key={message.id}
                          style={{
                            display: "flex",
                            flexDirection: isUser ? "row-reverse" : "row",
                            alignItems: "flex-end",
                            marginBottom: "8px",
                          }}
                      >
                        {/* Avatar */}
                        <div
                            style={{
                              width: 36,
                              height: 36,
                              borderRadius: "50%",
                              background: isUser ? "#3b82f6" : "#e0e7ef",
                              color: isUser ? "#fff" : "#6366f1",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              fontWeight: 700,
                              fontSize: 16,
                              margin: isUser ? "0 0 0 12px" : "0 12px 0 0",
                              flexShrink: 0,
                            }}
                        >
                          {isUser ? <span>U</span> : <span>AI</span>}
                        </div>

                        {/* Message Bubble */}
                        <div
                            style={{
                              background: isUser ? "#3b82f6" : "#fff",
                              color: isUser ? "#fff" : "#1f2937",
                              border: isUser ? "none" : "1px solid #e5e7eb",
                              borderRadius: isUser
                                  ? "16px 16px 4px 16px"
                                  : "16px 16px 16px 4px",
                              padding: "14px 18px",
                              maxWidth: "70%",
                              minWidth: 0,
                              boxShadow: isUser
                                  ? "0 2px 8px rgba(59,130,246,0.08)"
                                  : "0 2px 8px rgba(0,0,0,0.04)",
                              marginLeft: isUser ? 0 : 4,
                              marginRight: isUser ? 4 : 0,
                              wordBreak: "break-word",
                              position: "relative",
                            }}
                        >
                          {message.image && (
                              <div style={{ marginBottom: "8px" }}>
                                <img
                                    src={message.image}
                                    alt="Uploaded reference"
                                    style={{
                                      width: "100%",
                                      maxWidth: "220px",
                                      borderRadius: "8px",
                                      display: "block",
                                    }}
                                    onLoad={() => {
                                      console.log("✅ Image loaded successfully:", message.image?.substring(0, 50) + "...");
                                    }}
                                    onError={(e) => {
                                      console.error("Failed to load image:", {
                                        src: message.image,
                                        srcLength: message.image?.length,
                                        isValidDataUrl: message.image?.startsWith("data:image/"),
                                        messageId: message.id,
                                        error: e.type
                                      });
                                      e.target.style.display = 'none';
                                      // Create a placeholder element
                                      const placeholder = document.createElement('div');
                                      placeholder.style.cssText = `
                                        width: 220px;
                                        height: 120px;
                                        background: #f3f4f6;
                                        border: 2px dashed #d1d5db;
                                        border-radius: 8px;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        color: #6b7280;
                                        font-size: 14px;
                                        margin-bottom: 8px;
                                      `;
                                      placeholder.textContent = '📷 Image not available';
                                      e.target.parentNode.insertBefore(placeholder, e.target);
                                    }}
                                />
                              </div>
                          )}
                          <div style={{ fontSize: 15 }}>{message.text}</div>
                          <div
                              style={{
                                fontSize: 11,
                                color: isUser ? "#bfdbfe" : "#6b7280",
                                marginTop: 8,
                                textAlign: isUser ? "right" : "left",
                              }}
                          >
                            {message.timestamp}
                          </div>
                        </div>
                      </div>
                  );
                })}
              </div>

              {/* Input Area */}
              <div style={styles.inputArea}>
                {uploadedImage && (
                    <div style={styles.imagePreview}>
                      <img
                          src={uploadedImage}
                          alt="Upload preview"
                          style={{ height: "80px", borderRadius: "6px" }}
                      />
                      <button
                          onClick={() => setUploadedImage(null)}
                          style={styles.removeImageButton}
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                )}

                <div style={styles.inputContainer}>
                  <div style={styles.inputWrapper}>
                    <textarea
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                          e.preventDefault();
                          handleSendMessage();
                        }
                      }}
                      placeholder="Describe the component you want to generate..."
                      style={{
                        ...styles.textInput,
                        minHeight: 60,
                        maxHeight: 120,
                        resize: "vertical",
                        lineHeight: 1.5,
                        overflow: inputMessage.length === 0 ? "hidden" : undefined,
                      }}
                      className={inputMessage.length === 0 ? "hide-scrollbar" : ""}
                      onFocus={(e) => {
                        e.target.style.borderColor = "#3b82f6";
                        e.target.style.boxShadow =
                          "0 0 0 3px rgba(59, 130, 246, 0.1)";
                      }}
                      onBlur={(e) => {
                        e.target.style.borderColor = "#d1d5db";
                        e.target.style.boxShadow = "none";
                      }}
                      rows={1}
                    />
      {/* Hide textarea scrollbar when empty */}
      <style>{`
        .hide-scrollbar::-webkit-scrollbar { display: none; }
        .hide-scrollbar { scrollbar-width: none; }
      `}</style>

                    {!selectedComponentForRefinement && (
                        <label
                            style={styles.uploadButton}
                            tabIndex={0}
                            onMouseEnter={(e) => {
                              e.currentTarget.style.background = "#e0e7ef";
                              e.currentTarget.style.transform = "scale(1.08)";
                              e.currentTarget.style.boxShadow = "0 2px 8px rgba(59,130,246,0.10)";
                            }}
                            onMouseLeave={(e) => {
                              e.currentTarget.style.background = "#f3f4f6";
                              e.currentTarget.style.transform = "none";
                              e.currentTarget.style.boxShadow = "0 1px 4px rgba(0,0,0,0.04)";
                            }}
                        >
                          <input
                              disabled={selectedCMS === "Adobe EDS"}
                              type="file"
                              accept="image/*"
                              onChange={handleImageUpload}
                              style={{ display: "none" }}
                          />
                          <Image className="w-5 h-5" style={{ color: "#4b5563" }} />
                        </label>
                    )}
                  </div>

                  {console.log("🔧 Rendering Send button with state:", { selectedCMS, isLoading, isRefining, inputMessage: inputMessage.length, hasUploadedImage: !!uploadedImage })}
                  <button
                      onClick={(e) => {
                        console.log("🔥 SEND BUTTON CLICKED!");
                        console.log("📊 Event object:", e);
                        console.log("📊 Selected CMS:", selectedCMS);
                        console.log("🔄 Is Loading:", isLoading);
                        console.log("🔄 Is Refining:", isRefining);
                        console.log("📝 Input Message:", inputMessage);
                        console.log("🖼️ Uploaded Image:", uploadedImage);
                        console.log("🎯 Selected Component for Refinement:", selectedComponentForRefinement);
                        console.log("📍 Current Session ID:", currentSessionId);
                        
                        // Prevent any default behavior
                        e.preventDefault();
                        e.stopPropagation();
                        
                        if (selectedCMS === "Adobe EDS") {
                          console.log("📈 Calling handleEdsSendMessage");
                          handleEdsSendMessage();
                        } else {
                          if (selectedComponentForRefinement) {
                            console.log("🔧 Calling handleRefineComponent");
                            handleRefineComponent();
                          } else {
                            console.log("📤 Calling handleSendMessage");
                            handleSendMessage();
                          }
                        }
                      }}
                      disabled={isLoading || isRefining}
                      style={{
                        ...styles.sendButton,
                        background: selectedComponentForRefinement
                            ? "linear-gradient(90deg, #059669 0%, #10b981 100%)"
                            : "linear-gradient(90deg, #2563eb 0%, #3b82f6 100%)",
                        opacity: (isLoading || isRefining) ? 0.6 : 1,
                        cursor: (isLoading || isRefining) ? "not-allowed" : "pointer",
                      }}
                      onMouseEnter={(e) => {
                        console.log("🖱️ Mouse entered Send button");
                        if (!isLoading && !isRefining) {
                          e.target.style.background = selectedComponentForRefinement
                              ? "linear-gradient(90deg, #047857 0%, #059669 100%)"
                              : "linear-gradient(90deg, #1d4ed8 0%, #2563eb 100%)";
                          e.target.style.boxShadow = "0 4px 16px rgba(59,130,246,0.18)";
                          e.target.style.transform = "translateY(-2px) scale(1.03)";
                        }
                      }}
                      onMouseLeave={(e) => {
                        console.log("🖱️ Mouse left Send button");
                        if (!isLoading && !isRefining) {
                          e.target.style.background = selectedComponentForRefinement
                              ? "linear-gradient(90deg, #059669 0%, #10b981 100%)"
                              : "linear-gradient(90deg, #2563eb 0%, #3b82f6 100%)";
                          e.target.style.boxShadow = "0 2px 8px rgba(59,130,246,0.10)";
                          e.target.style.transform = "none";
                        }
                      }}
                  >
                  <span style={{ fontWeight: 700, fontSize: 14, letterSpacing: "0.02em" }}>
                    {selectedComponentForRefinement ? "Refine" : "Send"}
                  </span>
                    {selectedComponentForRefinement ? (
                        <RefreshCw className="w-4 h-4" style={{ marginLeft: 2 }} />
                    ) : (
                        <Send className="w-4 h-4" style={{ marginLeft: 2 }} />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Right Panel - Conditional AEM/EDS Rendering */}
            {rightPanelOpen && selectedCMS === "Adobe Experience Manager" && (
              <AEMRightPanel
                selectedComponent={selectedComponent}
                tabs={tabs}
                activeCodeTab={activeCodeTab}
                setActiveCodeTab={setActiveCodeTab}
                handleCopyCodeSection={handleCopyCodeSection}
                copiedSection={copiedSection}
                handleAEMBuildDeploy={handleAEMBuildDeploy}
                handleAEMPreview={handleAEMPreview}
                handleAEMRefine={handleAEMRefine}
                isLoading={isLoading}
                loadingContext={loadingContext}
                errorMessage={errorMessage}
                errorContext={errorContext}
                successMessage={successMessage}
                successContext={successContext}
                setRightPanelOpen={setRightPanelOpen}
                setSelectedComponent={setSelectedComponent}
                setSelectedComponentForRefinement={setSelectedComponentForRefinement}
              />
            )}

            {rightPanelOpen && selectedCMS === "Adobe EDS" && (
              <EDSRightPanel
                selectedComponent={selectedComponent}
                tabs={tabs}
                activeCodeTab={activeCodeTab}
                setActiveCodeTab={setActiveCodeTab}
                handleCopyCodeSection={handleCopyCodeSection}
                copiedSection={copiedSection}
                handleDownload={handleDownload}
                handleEDSPushToGit={handleEDSPushToGit}
                handleEDSPreview={handleEDSPreview}
                isLoading={isLoading}
                loadingContext={loadingContext}
                errorMessage={errorMessage}
                errorContext={errorContext}
                successMessage={successMessage}
                successContext={successContext}
                setSelectedComponent={setSelectedComponent}
              />
            )}

            {/* Right Panel Toggle Button (when closed) */}
            {!rightPanelOpen && (
              <div style={{ 
                width: "48px", 
                minWidth: "48px", 
                backgroundColor: "#ffffff", 
                borderLeft: "1px solid #e5e7eb",
                display: "flex",
                alignItems: "flex-start",
                padding: "10px"
              }}>
                <button
                    onClick={() => setRightPanelOpen(!rightPanelOpen)}
                    style={{
                      padding: "4px",
                      background: "transparent",
                      border: "none",
                      borderRadius: "4px",
                      cursor: "pointer",
                      color: "#374151",
                      transition: "background 0.2s"
                    }}
                    onMouseEnter={(e) => (e.target.style.backgroundColor = "#f3f4f6")}
                    onMouseLeave={(e) => (e.target.style.backgroundColor = "transparent")}
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
              </div>
            )}
          </div>
        </div>

        {/* New Session Modal */}
        {showNewSessionModal && (
            <div style={styles.modal}>
              <div style={styles.modalContent}>
                <h2 style={styles.modalHeader}>Create New Chat Session</h2>
                <input
                    type="text"
                    placeholder="Enter session title (optional)"
                    value={sessionTitle}
                    onChange={(e) => setSessionTitle(e.target.value)}
                    style={styles.modalInput}
                    onKeyPress={(e) => e.key === "Enter" && createNewSession()}
                />
                <div style={styles.modalButtons}>
                  <button
                      onClick={() => {
                        setShowNewSessionModal(false);
                        setSessionTitle("");
                      }}
                      style={{ ...styles.modalButton, ...styles.modalButtonSecondary }}
                  >
                    Cancel
                  </button>
                  <button
                      onClick={createNewSession}
                      style={{ ...styles.modalButton, ...styles.modalButtonPrimary }}
                  >
                    Create Session
                  </button>
                </div>
              </div>
            </div>
        )}

        {/* Preview Modal */}
        {showPreviewModal && htmlNode && cssNode && (
            <div
                style={{
                  position: "fixed",
                  top: 0,
                  left: 0,
                  width: "100vw",
                  height: "100vh",
                  backgroundColor: "rgba(0,0,0,0.85)",
                  zIndex: 9999,
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  padding: "20px",
                }}
            >
              <div
                  style={{
                    backgroundColor: "white",
                    width: "100%",
                    height: "100%",
                    maxWidth: "1400px",
                    maxHeight: "95vh",
                    borderRadius: "16px",
                    position: "relative",
                    display: "flex",
                    flexDirection: "column",
                    boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.5)",
                  }}
              >
                {/* Header with Close Button */}
                <div style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "20px 24px 16px 24px",
                  borderBottom: "1px solid #e5e7eb",
                  borderRadius: "16px 16px 0 0",
                  backgroundColor: "#f9fafb"
                }}>
                  <h3 style={{
                    margin: 0,
                    fontSize: "18px",
                    fontWeight: "600",
                    color: "#1f2937"
                  }}>
                    Component Preview
                  </h3>
                  <button
                      onClick={() => setShowPreviewModal(false)}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        width: "40px",
                        height: "40px",
                        background: "#ef4444",
                        color: "white",
                        border: "none",
                        borderRadius: "50%",
                        cursor: "pointer",
                        fontSize: "18px",
                        fontWeight: "bold",
                        transition: "background-color 0.2s, transform 0.1s",
                        boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.backgroundColor = "#dc2626";
                        e.target.style.transform = "scale(1.05)";
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.backgroundColor = "#ef4444";
                        e.target.style.transform = "scale(1)";
                      }}
                  >
                    <X size={20} />
                  </button>
                </div>

                {/* Preview Content */}
                <div style={{
                  flex: 1,
                  overflow: "auto",
                  padding: "24px",
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "flex-start",
                  backgroundColor: "#ffffff"
                }}>
                  <div style={{
                    width: "100%",
                    maxWidth: "100%",
                    minHeight: "400px"
                  }}>
                    <VisualCodeSandbox
                        view={"preview"}
                        htmlNode={htmlNode}
                        cssNode={cssNode}
                    />
                  </div>
                </div>
              </div>
            </div>
        )}
      </>
  );
};

export default DXPComponentGeneratorInterface;
