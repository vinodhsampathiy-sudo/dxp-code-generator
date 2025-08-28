import React, { useState } from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';
import './VisualCodeSandbox.css';

const VisualCodeSandbox = ({ htmlNode, cssNode, view }) => {
  const [theme, setTheme] = useState('dark');

  const themes = {
    light: {
      name: 'Light',
      icon: Sun,
      backgroundColor: '#ffffff',
      textColor: '#1f2937',
      cardBackground: '#f8fafc',
      borderColor: '#e5e7eb',
      headingColor: '#111827',
      linkColor: '#3b82f6'
    },
    dark: {
      name: 'Dark', 
      icon: Moon,
      backgroundColor: '#1f2937',
      textColor: '#f9fafb',
      cardBackground: '#374151',
      borderColor: '#4b5563',
      headingColor: '#ffffff',
      linkColor: '#60a5fa'
    },
    auto: {
      name: 'Auto',
      icon: Monitor,
      backgroundColor: '#f3f4f6',
      textColor: '#374151',
      cardBackground: '#ffffff',
      borderColor: '#d1d5db',
      headingColor: '#1f2937',
      linkColor: '#2563eb'
    }
  };

  const currentTheme = themes[theme];
  const cleanCSS = (cssString) => {
    if (!cssString) return '';
    
    // More careful CSS cleaning that preserves important formatting
    return cssString
      .replace(/\/\*[\s\S]*?\*\//g, '') // Remove comments
      .replace(/\s+/g, ' ') // Replace multiple whitespace with single space
      .replace(/;\s*}/g, ';}') // Clean up before closing braces
      .replace(/{\s+/g, '{') // Clean up after opening braces
      .replace(/;\s+/g, ';') // Clean up after semicolons
      .trim();
  };

  // Available images in the public folder
  const availableImages = [
    '/images/1709281520173.webp',
    '/images/1730273650816.webp', 
    '/images/1730273651115.webp',
    '/images/1750146694280.webp'
  ];

  // Function to get a random image from available images
  const getRandomImage = () => {
    return availableImages[Math.floor(Math.random() * availableImages.length)];
  };

  // Function to get contextual image based on component type or class
  const getContextualImage = (context = '') => {
    // For hero/banner components, we might want specific images
    if (context.includes('hero') || context.includes('banner')) {
      // Use landscape-oriented images for heroes
      return availableImages[Math.floor(Math.random() * availableImages.length)];
    }
    
    // For cards or thumbnails, any image works
    return getRandomImage();
  };

  // Function to replace various image placeholders with actual images and enhance HTML structure
  const processHTMLForPreview = (htmlString) => {
    if (!htmlString) return '<div class="no-content">No content available for preview</div>';
    
    let processedHTML = htmlString;
    
    // Replace AEM fileReference image sources with random images
    processedHTML = processedHTML.replace(
      /src="\$\{[^}]*fileReference[^}]*\}"/g,
      () => `src="${getRandomImage()}"`
    );
    
    // Replace AEM backgroundImage references in style attributes
    processedHTML = processedHTML.replace(
      /background-image:\s*url\('\$\{[^}]*backgroundImage[^}]*\}'\)/g,
      () => `background-image: url('${getRandomImage()}')`
    );
    
    // Handle any other img src patterns that might contain AEM expressions
    processedHTML = processedHTML.replace(
      /src="\$\{[^}]*image[^}]*\}"/g,
      () => `src="${getRandomImage()}"`
    );

    // Replace common placeholder image services with actual images
    processedHTML = processedHTML.replace(
      /src="https?:\/\/[^"]*placeholder[^"]*"/gi,
      () => `src="${getRandomImage()}"`
    );
    
    // Replace fpoimg.com placeholders
    processedHTML = processedHTML.replace(
      /src="https?:\/\/[^"]*fpoimg\.com[^"]*"/gi,
      () => `src="${getRandomImage()}"`
    );
    
    // Replace fillmurray.com placeholders
    processedHTML = processedHTML.replace(
      /src="https?:\/\/[^"]*fillmurray\.com[^"]*"/gi,
      () => `src="${getRandomImage()}"`
    );
    
    // Replace any generic placeholder.com images
    processedHTML = processedHTML.replace(
      /src="[^"]*placeholder[^"]*\.(?:jpg|jpeg|png|webp|gif)"/gi,
      () => `src="${getRandomImage()}"`
    );

    // Replace background-image URLs in CSS style attributes with random images
    processedHTML = processedHTML.replace(
      /background-image:\s*url\(['"]?[^'")]*placeholder[^'")]*['"]?\)/gi,
      () => `background-image: url('${getRandomImage()}')`
    );

    // Add missing positioning classes for better CSS compatibility
    processedHTML = processedHTML.replace(
      /class="cmp-contentimagecomponent"/g,
      'class="cmp-contentimagecomponent cmp-contentimagecomponent--position-left"'
    );
    
    // Remove AEM expressions that won't work in preview
    processedHTML = processedHTML.replace(/\$\{[^}]*\}/g, '');
    
    // Clean up any empty attributes
    processedHTML = processedHTML.replace(/\s+src=""\s*/g, '');
    processedHTML = processedHTML.replace(/\s+alt=""\s*/g, '');
    
    // Add alt attributes to images that don't have them for accessibility
    processedHTML = processedHTML.replace(
      /<img([^>]*src="[^"]*"[^>]*)(?![^>]*alt=)([^>]*>)/gi,
      '<img$1 alt="Component preview image"$2'
    );
    
    // Wrap content in a semantic structure if it's not already wrapped
    if (!processedHTML.includes('<main') && !processedHTML.includes('<section') && 
        !processedHTML.includes('<article') && !processedHTML.includes('<div class="component')) {
      processedHTML = `
        <main class="component-preview" role="main">
          <section class="component-section">
            ${processedHTML}
          </section>
        </main>
      `;
    }
    
    // Ensure proper content hierarchy
    if (processedHTML.includes('<h1') || processedHTML.includes('<h2') || processedHTML.includes('<h3')) {
      // Content has headings, good structure
    } else if (processedHTML.includes('title') || processedHTML.includes('Title')) {
      // Add a heading for better structure
      processedHTML = `<h2>Component Preview</h2>\n${processedHTML}`;
    }
    
    return processedHTML;
  };

  // Enhanced CSS processing to replace placeholder images and integrate with theme system
  const processCSS = (cssString) => {
    if (!cssString) return '';
    
    // Clean the CSS but preserve structure better
    let processedCSS = cssString
      .replace(/\/\*[\s\S]*?\*\//g, '') // Remove comments
      .replace(/\s+/g, ' ') // Replace multiple whitespace with single space
      .replace(/{\s+/g, ' { ') // Clean up after opening braces
      .replace(/;\s+/g, '; ') // Clean up after semicolons
      .replace(/}\s+/g, ' } ') // Clean up after closing braces
      .trim();
    
    // Replace background-image placeholder URLs with actual images
    processedCSS = processedCSS.replace(
      /background-image:\s*url\(['"]?[^'")]*placeholder[^'")]*['"]?\)/gi,
      () => `background-image: url('${getRandomImage()}')`
    );
    
    // Replace fpoimg.com background images
    processedCSS = processedCSS.replace(
      /background-image:\s*url\(['"]?https?:\/\/[^'")]*fpoimg\.com[^'")]*['"]?\)/gi,
      () => `background-image: url('${getRandomImage()}')`
    );
    
    // Replace fillmurray.com background images
    processedCSS = processedCSS.replace(
      /background-image:\s*url\(['"]?https?:\/\/[^'")]*fillmurray\.com[^'")]*['"]?\)/gi,
      () => `background-image: url('${getRandomImage()}')`
    );
    
    // Replace any generic placeholder URLs in CSS
    processedCSS = processedCSS.replace(
      /url\(['"]?[^'")]*placeholder[^'")]*\.(?:jpg|jpeg|png|webp|gif)['"]?\)/gi,
      () => `url('${getRandomImage()}')`
    );
    
    // Enhance the CSS for better theme integration
    // Add theme-aware color variables where appropriate
    processedCSS = processedCSS.replace(
      /(color\s*:\s*)(#000000|#000|black|rgb\(0,\s*0,\s*0\))/gi,
      `$1${currentTheme.textColor}`
    );
    
    processedCSS = processedCSS.replace(
      /(color\s*:\s*)(#ffffff|#fff|white|rgb\(255,\s*255,\s*255\))/gi,
      `$1${currentTheme.textColor}`
    );
    
    // Replace common background colors with theme-appropriate ones
    processedCSS = processedCSS.replace(
      /(background-color\s*:\s*)(#ffffff|#fff|white|rgb\(255,\s*255,\s*255\))/gi,
      `$1${currentTheme.backgroundColor}`
    );
    
    processedCSS = processedCSS.replace(
      /(background-color\s*:\s*)(#f5f5f5|#f0f0f0|#fafafa)/gi,
      `$1${currentTheme.cardBackground}`
    );
    
    // Add CSS specificity reducer for better integration
    // Wrap original CSS in a lower-specificity container
    if (processedCSS.trim()) {
      processedCSS = `
        /* Image Analysis Generated CSS - with theme integration */
        .preview-wrapper {
          ${processedCSS}
        }
        
        /* Additional integration styles */
        .preview-wrapper * {
          box-sizing: border-box;
        }
      `;
    }
    
    return processedCSS;
  };

  const processedHTML = processHTMLForPreview(htmlNode || '');
  const processedCSS = processCSS(cssNode || '');
  
  // Enhanced debug logging to track image replacements and theme integration
  console.log('🎨 Enhanced Preview Processing:', {
    theme: theme,
    themeColors: {
      background: currentTheme.backgroundColor,
      text: currentTheme.textColor,
      heading: currentTheme.headingColor,
      card: currentTheme.cardBackground
    },
    content: {
      originalHTMLLength: htmlNode?.length || 0,
      processedHTMLLength: processedHTML.length,
      originalCSSLength: cssNode?.length || 0, 
      processedCSSLength: processedCSS.length,
      hasHTMLContent: processedHTML.length > 100,
      hasCSSContent: processedCSS.length > 50
    },
    images: {
      availableImages: availableImages.length,
      hasImages: processedHTML.includes('/images/') || processedCSS.includes('/images/')
    },
    structure: {
      hasHeadings: processedHTML.includes('<h'),
      hasImages: processedHTML.includes('<img'),
      hasButtons: processedHTML.includes('button') || processedHTML.includes('btn'),
      hasCards: processedHTML.includes('card'),
      hasFlexbox: processedHTML.includes('flex') || processedCSS.includes('flex')
    }
  });
  
  // Additional image debugging
  const imageMatches = (processedHTML + processedCSS).match(/\/images\/[^'")]+/g);
  if (imageMatches) {
    console.log('🖼️ Images used in preview:', [...new Set(imageMatches)]);
  }
  
  // CSS theme integration check
  const themeColors = [currentTheme.backgroundColor, currentTheme.textColor, currentTheme.headingColor];
  const hasThemeIntegration = themeColors.some(color => processedCSS.includes(color));
  console.log('🎨 Theme integration:', { 
    hasThemeIntegration,
    cssLength: processedCSS.length,
    htmlLength: processedHTML.length
  });
  
  const combinedHTML = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Component Preview</title>
      <style>
        /* Modern CSS Reset */
        *, *::before, *::after {
          box-sizing: border-box;
          margin: 0;
          padding: 0;
        }
        
        /* Base HTML/Body styling with theme support */
        html {
          font-size: 16px;
          line-height: 1.5;
          background-color: ${currentTheme.backgroundColor} !important;
          color: ${currentTheme.textColor} !important;
        }
        
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
          background-color: ${currentTheme.backgroundColor} !important;
          color: ${currentTheme.textColor} !important;
          padding: 24px !important;
          min-height: 100vh;
          overflow-x: hidden;
        }

        /* Universal text color enforcement with theme awareness */
        * {
          color: ${currentTheme.textColor} !important;
        }

        /* Container for all content with proper padding */
        .preview-wrapper {
          max-width: 1200px;
          margin: 0 auto;
          background-color: ${currentTheme.backgroundColor};
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, ${theme === 'dark' ? '0.25' : '0.1'});
        }

        /* Enhanced typography with proper spacing */
        h1, h2, h3, h4, h5, h6 {
          color: ${currentTheme.headingColor} !important;
          font-weight: 600 !important;
          line-height: 1.2 !important;
          margin-bottom: 16px !important;
          margin-top: 0 !important;
        }

        h1 { font-size: 2.5rem; margin-bottom: 24px !important; }
        h2 { font-size: 2rem; margin-bottom: 20px !important; }
        h3 { font-size: 1.5rem; margin-bottom: 18px !important; }
        h4 { font-size: 1.25rem; margin-bottom: 16px !important; }
        h5 { font-size: 1.125rem; margin-bottom: 14px !important; }
        h6 { font-size: 1rem; margin-bottom: 12px !important; }

        /* Paragraph styling with proper spacing */
        p {
          color: ${currentTheme.textColor} !important;
          line-height: 1.7 !important;
          margin-bottom: 16px !important;
          max-width: none;
        }

        /* Enhanced link styling */
        a, a:visited {
          color: ${currentTheme.linkColor} !important;
          text-decoration: none !important;
          font-weight: 500 !important;
          transition: all 0.2s ease !important;
        }

        a:hover, a:focus {
          opacity: 0.8 !important;
          text-decoration: underline !important;
        }

        /* Button enhancements with proper spacing */
        .cmp-button, .btn, button, [class*="button"] {
          display: inline-block !important;
          padding: 14px 28px !important;
          margin: 12px 8px 12px 0 !important;
          border-radius: 8px !important;
          text-decoration: none !important;
          font-weight: 600 !important;
          font-size: 16px !important;
          transition: all 0.3s ease !important;
          border: none !important;
          cursor: pointer !important;
          min-width: 120px !important;
          text-align: center !important;
        }

        .cmp-button--primary, .btn-primary, [class*="primary"] {
          background-color: ${currentTheme.linkColor} !important;
          color: #ffffff !important;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        }

        .cmp-button--secondary, .btn-secondary, [class*="secondary"] {
          background-color: ${currentTheme.cardBackground} !important;
          color: ${currentTheme.textColor} !important;
          border: 2px solid ${currentTheme.borderColor} !important;
        }

        .cmp-button:hover, .btn:hover, button:hover {
          transform: translateY(-2px) !important;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15) !important;
        }

        /* Enhanced card styling with better padding */
        .cmp-card, .card, [class*="card"] {
          background-color: ${currentTheme.cardBackground} !important;
          border: 1px solid ${currentTheme.borderColor} !important;
          border-radius: 12px !important;
          padding: 32px !important;
          margin: 24px 0 !important;
          box-shadow: 0 2px 4px rgba(0, 0, 0, ${theme === 'dark' ? '0.2' : '0.05'}) !important;
          transition: box-shadow 0.3s ease !important;
        }

        .cmp-card:hover, .card:hover {
          box-shadow: 0 8px 16px rgba(0, 0, 0, ${theme === 'dark' ? '0.3' : '0.1'}) !important;
        }

        /* Enhanced image styling */
        img {
          max-width: 100% !important;
          height: auto !important;
          border-radius: 8px !important;
          box-shadow: 0 4px 8px rgba(0, 0, 0, ${theme === 'dark' ? '0.3' : '0.1'}) !important;
          display: block !important;
        }

        /* Flexbox layouts with proper spacing */
        .cmp-contentimagecomponent, [class*="content-image"], .hero, .banner {
          display: flex !important;
          flex-wrap: wrap !important;
          align-items: center !important;
          margin: 32px 0 !important;
          padding: 32px !important;
          background-color: ${currentTheme.cardBackground} !important;
          border-radius: 12px !important;
          border: 1px solid ${currentTheme.borderColor} !important;
          min-height: 300px !important;
        }
        
        .cmp-contentimagecomponent__container {
          display: flex !important;
          width: 100% !important;
          gap: 32px !important;
          align-items: center !important;
        }
        
        .cmp-contentimagecomponent__text-section,
        .cmp-contentimagecomponent__image-section {
          flex: 1 !important;
          padding: 24px !important;
          min-width: 0 !important;
        }
        
        .cmp-contentimagecomponent__text-section {
          display: flex !important;
          flex-direction: column !important;
          justify-content: center !important;
        }
        
        .cmp-contentimagecomponent__image-section {
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
        }

        /* List styling with proper spacing */
        ul, ol {
          color: ${currentTheme.textColor} !important;
          padding-left: 24px !important;
          margin-bottom: 20px !important;
        }

        li {
          color: ${currentTheme.textColor} !important;
          margin-bottom: 8px !important;
          line-height: 1.6 !important;
        }

        /* Table styling with enhanced appearance */
        table {
          width: 100% !important;
          border-collapse: collapse !important;
          margin: 24px 0 !important;
          background-color: ${currentTheme.cardBackground} !important;
          border-radius: 8px !important;
          overflow: hidden !important;
          box-shadow: 0 2px 4px rgba(0, 0, 0, ${theme === 'dark' ? '0.2' : '0.05'}) !important;
        }

        th, td {
          padding: 16px !important;
          text-align: left !important;
          border-bottom: 1px solid ${currentTheme.borderColor} !important;
          color: ${currentTheme.textColor} !important;
        }

        th {
          background-color: ${theme === 'dark' ? currentTheme.cardBackground : currentTheme.backgroundColor} !important;
          font-weight: 600 !important;
          color: ${currentTheme.headingColor} !important;
        }

        /* Form elements with better styling */
        input, textarea, select {
          background-color: ${currentTheme.cardBackground} !important;
          border: 2px solid ${currentTheme.borderColor} !important;
          color: ${currentTheme.textColor} !important;
          border-radius: 8px !important;
          padding: 12px 16px !important;
          font-size: 16px !important;
          transition: border-color 0.2s ease !important;
          margin: 8px 0 !important;
          width: 100% !important;
          max-width: 400px !important;
        }

        input:focus, textarea:focus, select:focus {
          outline: none !important;
          border-color: ${currentTheme.linkColor} !important;
          box-shadow: 0 0 0 3px ${currentTheme.linkColor}33 !important;
        }

        /* Responsive design enhancements */
        @media (max-width: 768px) {
          body {
            padding: 16px !important;
          }
          
          .cmp-contentimagecomponent__container {
            flex-direction: column !important;
            gap: 20px !important;
          }
          
          .cmp-contentimagecomponent,
          .cmp-card, .card {
            padding: 20px !important;
          }
          
          h1 { font-size: 2rem; }
          h2 { font-size: 1.75rem; }
          h3 { font-size: 1.5rem; }
        }

        /* Section spacing */
        section, .section, [class*="section"] {
          margin: 40px 0 !important;
          padding: 32px 0 !important;
        }

        /* Content spacing wrapper */
        .content, .main-content, [class*="content"]:not([class*="image"]) {
          padding: 24px !important;
        }

        /* Override any conflicting inline styles */
        [style*="color"]:not(a) {
          color: ${currentTheme.textColor} !important;
        }

        [style*="background-color"] {
          background-color: ${currentTheme.backgroundColor} !important;
        }
        
        /* Original component CSS (with lower specificity to allow overrides above) */
        ${processedCSS}
      </style>
    </head>
    <body>
      <div class="preview-wrapper">
        ${processedHTML}
      </div>
    </body>
    </html>
  `;

  return (
    <div className="visual-code-sandbox" style={{
      width: "100%",
      height: "100%",
      display: "flex",
      flexDirection: "column",
      backgroundColor: currentTheme.backgroundColor
    }}>
      {/* Theme Selector */}
      <div style={{
        display: "flex",
        justifyContent: "flex-end",
        alignItems: "center",
        padding: "12px 16px",
        backgroundColor: currentTheme.cardBackground,
        borderBottom: `1px solid ${currentTheme.borderColor}`,
        gap: "8px"
      }}>
        <span style={{
          fontSize: "14px",
          fontWeight: "500",
          color: currentTheme.textColor,
          marginRight: "8px"
        }}>
          Theme:
        </span>
        {Object.entries(themes).map(([key, themeConfig]) => {
          const IconComponent = themeConfig.icon;
          return (
            <button
              key={key}
              onClick={() => setTheme(key)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "6px",
                padding: "8px 12px",
                border: `1px solid ${theme === key ? currentTheme.linkColor : currentTheme.borderColor}`,
                borderRadius: "6px",
                backgroundColor: theme === key ? currentTheme.linkColor : 'transparent',
                color: theme === key ? '#ffffff' : currentTheme.textColor,
                cursor: "pointer",
                fontSize: "12px",
                fontWeight: "500",
                transition: "all 0.2s",
                outline: "none"
              }}
              onMouseEnter={(e) => {
                if (theme !== key) {
                  e.target.style.backgroundColor = currentTheme.cardBackground;
                }
              }}
              onMouseLeave={(e) => {
                if (theme !== key) {
                  e.target.style.backgroundColor = 'transparent';
                }
              }}
            >
              <IconComponent size={14} />
              {themeConfig.name}
            </button>
          );
        })}
      </div>

      {/* Preview Content */}
      <div 
        className="preview-container"
        dangerouslySetInnerHTML={{ __html: combinedHTML }}
        style={{ 
          flex: 1,
          overflow: "auto",
          width: "100%",
          backgroundColor: currentTheme.backgroundColor,
          borderRadius: "0 0 8px 8px",
          border: "none"
        }}
      />
    </div>
  );
};

export default VisualCodeSandbox;
