import React from 'react';
import { Copy, Download, Eye, GitBranch, X } from 'lucide-react';

const EDSRightPanel = ({
  selectedComponent,
  tabs,
  activeCodeTab,
  setActiveCodeTab,
  handleCopyCodeSection,
  copiedSection,
  handleDownload,
  handleEDSPushToGit,
  handleEDSPreview,
  isLoading,
  loadingContext,
  errorMessage,
  errorContext,
  successMessage,
  successContext,
  setSelectedComponent
}) => {
  console.log("🟢 EDSRightPanel RENDERED");
  console.log("🟢 EDS selectedComponent:", selectedComponent ? selectedComponent.name : "null");
  console.log("🟢 EDS tabs:", tabs);
  console.log("🟢 EDS activeCodeTab:", activeCodeTab);

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

  const styles = {
    rightPanel: {
      flexBasis: "40%",
      flexGrow: 1,
      flexShrink: 1,
      maxWidth: "40%",
      backgroundColor: "#ffffff",
      background: "linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%)", // Slightly different gradient for EDS
      color: "#1f2937",
      transition: "all 0.3s ease",
      display: "flex",
      flexDirection: "column",
      minWidth: 0,
      borderLeft: "1px solid #e5e7eb",
    },
    panelHeader: {
      padding: "16px",
      borderBottom: "1px solid #e5e7eb",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      backgroundColor: "#f0f9ff", // EDS-specific background
    },
    headerTitle: {
      fontSize: "16px",
      fontWeight: "600",
      color: "#1f2937",
    },
    headerSubtitle: {
      fontSize: "12px",
      color: "#6b7280",
      marginTop: "2px",
    },
    closeButton: {
      padding: "6px",
      background: "transparent",
      border: "none",
      borderRadius: "4px",
      cursor: "pointer",
      color: "#6b7280",
      transition: "background 0.2s",
    },
    actionButtons: {
      padding: "12px 16px",
      borderBottom: "1px solid #e5e7eb",
      display: "flex",
      gap: "8px",
      flexWrap: "wrap",
      backgroundColor: "#ffffff",
    },
    actionButton: {
      padding: "8px 12px",
      border: "none",
      borderRadius: "6px",
      cursor: "pointer",
      display: "flex",
      alignItems: "center",
      gap: "6px",
      fontSize: "13px",
      fontWeight: "500",
      transition: "all 0.2s",
    },
    downloadButton: {
      backgroundColor: "#06b6d4", // Cyan for download
      color: "white",
    },
    gitButton: {
      backgroundColor: "#8b5cf6", // Purple for Git
      color: "white",
    },
    previewButton: {
      backgroundColor: "#10b981", // Green for EDS preview
      color: "white",
    },
    codeTabs: {
      display: "flex",
      borderBottom: "1px solid #e5e7eb",
      backgroundColor: "#f0f9ff", // EDS-specific tab background
      padding: "0 16px",
      overflowX: "auto", // Allow horizontal scrolling if needed
      overflowY: "hidden",
      minHeight: "fit-content",
      flexShrink: 0, // Prevent the tabs container from shrinking
    },
    codeTab: {
      padding: "8px 12px", // Reduced padding to fit more tabs
      background: "transparent",
      border: "none",
      color: "#6b7280",
      cursor: "pointer",
      fontSize: "13px", // Slightly smaller font
      fontWeight: "500",
      borderBottom: "3px solid transparent",
      transition: "all 0.2s ease",
      whiteSpace: "nowrap",
      minWidth: "fit-content",
      borderRadius: "6px 6px 0 0",
      marginRight: "2px", // Reduced margin
      flexShrink: 0, // Prevent individual tabs from shrinking
    },
    codeTabActive: {
      color: "#1f2937",
      borderBottomColor: "#06b6d4", // Cyan accent for EDS
      backgroundColor: "#ffffff",
      boxShadow: "0 -2px 8px rgba(0,0,0,0.1)",
      zIndex: 1,
      fontWeight: "600",
    },
    codeContent: {
      flex: 1,
      display: "flex",
      flexDirection: "column",
    },
    codeHeader: {
      padding: "12px 16px",
      borderBottom: "1px solid #e5e7eb",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      backgroundColor: "#ffffff",
    },
    codeTitle: {
      fontSize: "14px",
      fontWeight: "500",
      color: "#374151",
    },
    copyButton: {
      padding: "6px 10px",
      background: "#f0f9ff",
      border: "1px solid #06b6d4",
      borderRadius: "6px",
      cursor: "pointer",
      color: "#0891b2",
      display: "flex",
      alignItems: "center",
      gap: "6px",
      transition: "all 0.2s",
      fontSize: "12px",
      fontWeight: "500",
    },
    codeDisplay: {
      flex: 1,
      overflowY: "auto",
      padding: "16px",
      backgroundColor: "#ffffff",
      maxHeight: "400px", // Set max height to enable scrolling
    },
    codeBlock: {
      fontSize: "14px",
      lineHeight: "1.6",
      fontFamily: "'Fira Code', 'Monaco', 'Consolas', monospace",
      whiteSpace: "pre-wrap",
      wordBreak: "break-word",
      backgroundColor: "#f0f9ff",
      padding: "16px",
      borderRadius: "8px",
      border: "1px solid #e0f2fe",
      color: "#374151",
      maxHeight: "none", // Allow code block to expand
      overflow: "visible", // Let parent handle scrolling
    },
    messageContainer: {
      padding: "16px",
      margin: "16px",
      borderRadius: "8px",
      display: "flex",
      alignItems: "center",
      gap: "12px",
    },
    errorContainer: {
      backgroundColor: "#fef2f2",
      border: "1px solid #fecaca",
      color: "#dc2626",
    },
    successContainer: {
      backgroundColor: "#f0fdf4",
      border: "1px solid #bbf7d0",
      color: "#16a34a",
    },
    loadingContainer: {
      backgroundColor: "#eff6ff",
      border: "1px solid #bfdbfe",
      color: "#2563eb",
    },
    emptyState: {
      padding: "40px 20px",
      textAlign: "center",
      color: "#6b7280",
      fontSize: "14px",
    }
  };

  if (!selectedComponent && !errorMessage && !successMessage && !isLoading) {
    return (
      <div style={styles.rightPanel}>
        <div style={styles.panelHeader}>
          <div>
            <div style={styles.headerTitle}>EDS Block Code</div>
            <div style={styles.headerSubtitle}>Select a block to view code</div>
          </div>
        </div>
        <div style={styles.emptyState}>
          <div>No EDS block selected</div>
          <div style={{ marginTop: "8px", fontSize: "12px" }}>
            Generate an EDS block to see the code here
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.rightPanel}>
      {/* Header */}
      <div style={styles.panelHeader}>
        <div>
          <div style={styles.headerTitle}>
            {selectedComponent ? selectedComponent.name : "EDS Block"}
          </div>
          <div style={styles.headerSubtitle}>
            {selectedComponent ? selectedComponent.timestamp : "Adobe Edge Delivery Services"}
          </div>
        </div>
        <button
          style={styles.closeButton}
          onClick={() => setSelectedComponent(null)}
        >
          <X size={16} />
        </button>
      </div>

      {/* Action Buttons */}
      {selectedComponent && (
        <div style={styles.actionButtons}>
          <button
            style={{ ...styles.actionButton, ...styles.downloadButton }}
            onClick={handleDownload}
          >
            <Download size={14} />
            Download Zip
          </button>
          <button
            style={{ ...styles.actionButton, ...styles.gitButton }}
            onClick={handleEDSPushToGit}
          >
            <GitBranch size={14} />
            Push to Git
          </button>
          <button
            style={{ ...styles.actionButton, ...styles.previewButton }}
            onClick={handleEDSPreview}
          >
            <Eye size={14} />
            Preview EDS
          </button>
        </div>
      )}

      {/* Loading/Error/Success Messages */}
      {isLoading && loadingContext === "analyze" && (
        <div style={{ ...styles.messageContainer, ...styles.loadingContainer }}>
          <div>Generating EDS block...</div>
        </div>
      )}

      {isLoading && loadingContext === "build" && (
        <div style={{ ...styles.messageContainer, ...styles.loadingContainer }}>
          <div>Building EDS block...</div>
        </div>
      )}

      {isLoading && loadingContext === "refine" && (
        <div style={{ ...styles.messageContainer, ...styles.loadingContainer }}>
          <div>Refining EDS block...</div>
        </div>
      )}

      {errorMessage && (
        <div style={{ ...styles.messageContainer, ...styles.errorContainer }}>
          <div>{errorMessage}</div>
        </div>
      )}

      {successMessage && (
        <div style={{ ...styles.messageContainer, ...styles.successContainer }}>
          <div>{successMessage}</div>
        </div>
      )}

      {/* Code Tabs and Content */}
      {selectedComponent && (
        <>
          <div style={styles.codeTabs}>
            {tabs.map((tab, index) => (
              <button
                key={tab}
                style={{
                  ...styles.codeTab,
                  ...(activeCodeTab === tab ? styles.codeTabActive : {}),
                }}
                onClick={() => setActiveCodeTab(tab)}
              >
                {tab}
              </button>
            ))}
          </div>

          <div style={styles.codeContent}>
            <div style={styles.codeHeader}>
              <div style={styles.codeTitle}>{activeCodeTab}</div>
              <button
                style={styles.copyButton}
                onClick={() => handleCopyCodeSection(activeCodeTab)}
              >
                <Copy size={12} />
                {copiedSection === activeCodeTab ? "Copied!" : "Copy"}
              </button>
            </div>
            <div style={styles.codeDisplay}>
              <pre style={styles.codeBlock}>
                {getCodeForEdsSelection(activeCodeTab, selectedComponent)}
              </pre>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default EDSRightPanel;
