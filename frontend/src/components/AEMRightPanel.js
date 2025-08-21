import React from 'react';
import { Copy, Download, Eye, Wrench, X } from 'lucide-react';
import ProgressLoader from './ProgressLoader';

const AEMRightPanel = ({
  selectedComponent,
  tabs,
  activeCodeTab,
  setActiveCodeTab,
  handleCopyCodeSection,
  copiedSection,
  handleAEMBuildDeploy,
  handleAEMPreview,
  isLoading,
  loadingContext,
  errorMessage,
  errorContext,
  successMessage,
  successContext,
  setSelectedComponent,
  selectedComponentForRefinement,
  setSelectedComponentForRefinement,
  loadingStartTime,
  loadingDuration
}) => {
  console.log("🔵 AEMRightPanel RENDERED");
  console.log("🔵 AEM selectedComponent:", selectedComponent ? selectedComponent.name : "null");
  console.log("🔵 AEM tabs:", tabs);
  console.log("🔵 AEM activeCodeTab:", activeCodeTab);

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

  const styles = {
    rightPanel: {
      flexBasis: "40%",
      flexGrow: 1,
      flexShrink: 1,
      maxWidth: "40%",
      backgroundColor: "#ffffff",
      background: "linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)",
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
      backgroundColor: "#f8fafc",
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
    buildButton: {
      backgroundColor: "#10b981",
      color: "white",
    },
    previewButton: {
      backgroundColor: "#3b82f6",
      color: "white",
    },
    refineButton: {
      backgroundColor: "#f59e0b",
      color: "white",
    },
    codeTabs: {
      display: "flex",
      borderBottom: "1px solid #e5e7eb",
      backgroundColor: "#f8fafc",
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
      borderBottomColor: "#3b82f6",
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
      background: "#f3f4f6",
      border: "1px solid #d1d5db",
      borderRadius: "6px",
      cursor: "pointer",
      color: "#374151",
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
      backgroundColor: "#f8fafc",
      padding: "16px",
      borderRadius: "8px",
      border: "1px solid #e5e7eb",
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
            <div style={styles.headerTitle}>AEM Component Code</div>
            <div style={styles.headerSubtitle}>Select a component to view code</div>
          </div>
        </div>
        <div style={styles.emptyState}>
          <div>No component selected</div>
          <div style={{ marginTop: "8px", fontSize: "12px" }}>
            Generate a component to see the code here
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
            {selectedComponent ? selectedComponent.name : "AEM Component"}
          </div>
          <div style={styles.headerSubtitle}>
            {selectedComponent ? selectedComponent.timestamp : "Adobe Experience Manager"}
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
            style={{ ...styles.actionButton, ...styles.buildButton }}
            onClick={handleAEMBuildDeploy}
            disabled={isLoading && loadingContext === "build"}
          >
            <Wrench size={14} />
            {isLoading && loadingContext === "build" ? "Building..." : "Build & Deploy"}
          </button>
          <button
            style={{ ...styles.actionButton, ...styles.previewButton }}
            onClick={handleAEMPreview}
          >
            <Eye size={14} />
            Preview
          </button>
          <button
            style={{ ...styles.actionButton, ...styles.refineButton }}
            onClick={() => setSelectedComponentForRefinement(selectedComponent)}
          >
            <Wrench size={14} />
            Refine
          </button>
        </div>
      )}

      {/* Enhanced Progress Loader */}
      <ProgressLoader 
        isLoading={isLoading}
        loadingContext={loadingContext}
        estimatedTime={loadingContext === 'build' ? 45 : loadingContext === 'analyze' ? 35 : 25}
      />

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
            {tabs.map((tab) => (
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
                {getCodeForSection(activeCodeTab, selectedComponent)}
              </pre>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default AEMRightPanel;
