import React, { useState, useEffect } from 'react';
import { Clock, Loader, CheckCircle, AlertCircle } from 'lucide-react';

const ProgressLoader = ({ 
  isLoading, 
  loadingContext, 
  onCancel, 
  estimatedTime = 30,
  steps = [],
  actualProgress = null, // New prop for actual progress from backend
  isCompleted = false    // New prop to indicate completion
}) => {
  const [elapsedTime, setElapsedTime] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [displayProgress, setDisplayProgress] = useState(0);

  // Default steps for different contexts
  const defaultSteps = {
    analyze: [
      { label: "🔍 Analyzing component requirements", duration: 2 },
      { label: "🖼️ Processing image/text input", duration: 3 },
      { label: "🧠 Agent 1: Requirements & Sling Model", duration: 4 },
      { label: "⚡ Agents 2&3: HTL & Dialog (parallel)", duration: 5 },
      { label: "🎨 Agent 4: Client Libraries", duration: 3 },
      { label: "📁 Creating component files", duration: 2 },
      { label: "✅ Component generation complete", duration: 1 }
    ],
    build: [
      { label: "Preparing component files", duration: 2 },
      { label: "Validating XML structure", duration: 3 },
      { label: "Compiling Java sources", duration: 8 },
      { label: "Building Maven project", duration: 12 },
      { label: "Creating AEM package", duration: 4 },
      { label: "Deploying to AEM instance", duration: 6 },
      { label: "Verifying deployment", duration: 3 }
    ],
    refine: [
      { label: "Processing refinement request", duration: 2 },
      { label: "Analyzing changes", duration: 4 },
      { label: "Updating component code", duration: 6 },
      { label: "Validating modifications", duration: 3 },
      { label: "Applying refinements", duration: 5 }
    ]
  };

  const currentSteps = steps.length > 0 ? steps : (defaultSteps[loadingContext] || defaultSteps.analyze);

  useEffect(() => {
    if (!isLoading) {
      setElapsedTime(0);
      setCurrentStep(0);
      setProgress(0);
      setDisplayProgress(0);
      return;
    }

    const timer = setInterval(() => {
      setElapsedTime(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [isLoading]);

  // Calculate progress and current step
  useEffect(() => {
    if (!isLoading) return;

    // Use actual progress if provided, otherwise calculate from elapsed time
    if (actualProgress !== null) {
      setProgress(actualProgress);
      setDisplayProgress(actualProgress);
      
      // Calculate current step based on actual progress
      let progressPerStep = 100 / currentSteps.length;
      let stepIndex = Math.floor(actualProgress / progressPerStep);
      setCurrentStep(Math.min(stepIndex, currentSteps.length - 1));
    } else {
      // Fallback to time-based calculation
      let totalDuration = currentSteps.reduce((sum, step) => sum + step.duration, 0);
      let currentDuration = 0;
      let stepIndex = 0;

      for (let i = 0; i < currentSteps.length; i++) {
        if (elapsedTime <= currentDuration + currentSteps[i].duration) {
          stepIndex = i;
          break;
        }
        currentDuration += currentSteps[i].duration;
        stepIndex = i + 1;
      }

      setCurrentStep(stepIndex);
      let calculatedProgress = Math.min((elapsedTime / totalDuration) * 100, 95);
      setProgress(calculatedProgress);
      setDisplayProgress(calculatedProgress);
    }

    // If completed, show 100%
    if (isCompleted) {
      setProgress(100);
      setDisplayProgress(100);
      setCurrentStep(currentSteps.length);
    }
  }, [elapsedTime, isLoading, currentSteps, actualProgress, isCompleted]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getContextTitle = (context) => {
    switch (context) {
      case 'analyze': return 'Generating Component';
      case 'build': return 'Building & Deploying';
      case 'refine': return 'Refining Component';
      default: return 'Processing';
    }
  };

  const getContextColor = (context) => {
    switch (context) {
      case 'analyze': return '#3b82f6'; // blue
      case 'build': return '#f59e0b'; // amber
      case 'refine': return '#8b5cf6'; // purple
      default: return '#6b7280'; // gray
    }
  };

  if (!isLoading) return null;

  return (
    <div style={styles.overlay}>
      <div style={styles.container}>
        <div style={styles.header}>
          <div style={styles.titleSection}>
            <Loader style={{...styles.spinnerIcon, color: getContextColor(loadingContext)}} />
            <h3 style={styles.title}>{getContextTitle(loadingContext)}</h3>
          </div>
          <div style={styles.timeSection}>
            <Clock style={styles.clockIcon} />
            <span style={styles.timeText}>{formatTime(elapsedTime)}</span>
          </div>
        </div>

        <div style={styles.progressSection}>
          <div style={styles.progressBar}>
            <div 
              style={{
                ...styles.progressFill,
                width: `${displayProgress}%`,
                backgroundColor: getContextColor(loadingContext)
              }} 
            />
          </div>
          <div style={styles.progressText}>{Math.round(displayProgress)}%</div>
        </div>

        <div style={styles.stepsSection}>
          {currentSteps.map((step, index) => (
            <div key={index} style={styles.stepItem}>
              <div style={styles.stepIcon}>
                {index < currentStep ? (
                  <CheckCircle style={styles.completedIcon} />
                ) : index === currentStep ? (
                  <Loader style={{...styles.currentIcon, color: getContextColor(loadingContext)}} />
                ) : (
                  <div style={styles.pendingIcon} />
                )}
              </div>
              <span style={{
                ...styles.stepLabel,
                color: index <= currentStep ? '#1f2937' : '#9ca3af',
                fontWeight: index === currentStep ? 'bold' : 'normal'
              }}>
                {step.label}
              </span>
            </div>
          ))}
        </div>

        <div style={styles.footer}>
          <div style={styles.estimateText}>
            {isCompleted ? "Completed!" : `Estimated time remaining: ${Math.max(0, estimatedTime - elapsedTime)}s`}
          </div>
          {onCancel && !isCompleted && (
            <button style={styles.cancelButton} onClick={onCancel}>
              Cancel
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

const styles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  container: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '24px',
    maxWidth: '500px',
    width: '90%',
    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
  },
  titleSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  spinnerIcon: {
    width: '24px',
    height: '24px',
    animation: 'spin 1s linear infinite',
  },
  title: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: '#1f2937',
    margin: 0,
  },
  timeSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    backgroundColor: '#f3f4f6',
    padding: '8px 12px',
    borderRadius: '6px',
  },
  clockIcon: {
    width: '16px',
    height: '16px',
    color: '#6b7280',
  },
  timeText: {
    fontSize: '14px',
    fontWeight: 'bold',
    color: '#374151',
    fontFamily: 'monospace',
  },
  progressSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '24px',
  },
  progressBar: {
    flex: 1,
    height: '8px',
    backgroundColor: '#e5e7eb',
    borderRadius: '4px',
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    transition: 'width 0.3s ease',
    borderRadius: '4px',
  },
  progressText: {
    fontSize: '14px',
    fontWeight: 'bold',
    color: '#374151',
    minWidth: '40px',
    textAlign: 'right',
  },
  stepsSection: {
    marginBottom: '20px',
    maxHeight: '200px',
    overflowY: 'auto',
  },
  stepItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '8px 0',
  },
  stepIcon: {
    width: '20px',
    height: '20px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  completedIcon: {
    width: '16px',
    height: '16px',
    color: '#10b981',
  },
  currentIcon: {
    width: '16px',
    height: '16px',
    animation: 'spin 1s linear infinite',
  },
  pendingIcon: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    backgroundColor: '#d1d5db',
  },
  stepLabel: {
    fontSize: '14px',
    flex: 1,
  },
  footer: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  estimateText: {
    fontSize: '12px',
    color: '#6b7280',
  },
  cancelButton: {
    padding: '8px 16px',
    backgroundColor: '#dc2626',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '14px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  }
};

// Add CSS animation for spinner
const styleSheet = document.createElement("style");
styleSheet.type = "text/css";
styleSheet.innerText = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;
document.head.appendChild(styleSheet);

export default ProgressLoader;
