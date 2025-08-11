import React from 'react';
import './VisualCodeSandbox.css';

const VisualCodeSandbox = ({ htmlNode, cssNode, view }) => {
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

  // Function to replace AEM image references with placeholder images
  const processHTMLForPreview = (htmlString) => {
    if (!htmlString) return '';
    
    let processedHTML = htmlString;
    
    // Replace AEM fileReference image sources with placeholder
    processedHTML = processedHTML.replace(
      /src="\$\{[^}]*fileReference[^}]*\}"/g,
      'src="/images/1709281520173.webp"'
    );
    
    // Replace AEM backgroundImage references in style attributes
    processedHTML = processedHTML.replace(
      /background-image:\s*url\('\$\{[^}]*backgroundImage[^}]*\}'\)/g,
      "background-image: url('/images/1730273650816.webp')"
    );
    
    // Handle any other img src patterns that might contain AEM expressions
    processedHTML = processedHTML.replace(
      /src="\$\{[^}]*image[^}]*\}"/g,
      'src="/images/1709281520173.webp"'
    );
    
    // Add missing positioning classes for better CSS compatibility
    // This helps ensure the CSS positioning works properly
    processedHTML = processedHTML.replace(
      /class="cmp-contentimagecomponent"/g,
      'class="cmp-contentimagecomponent cmp-contentimagecomponent--position-left"'
    );
    
    // Remove AEM expressions that won't work in preview
    processedHTML = processedHTML.replace(/\$\{[^}]*\}/g, '');
    
    return processedHTML;
  };

  // Simplified CSS processing - less aggressive scoping
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
    
    return processedCSS;
  };

  const processedHTML = processHTMLForPreview(htmlNode || '');
  const processedCSS = processCSS(cssNode || '');
  
  // Debug logging (remove in production)
  console.log('Preview HTML:', processedHTML);
  console.log('Preview CSS:', processedCSS);
  
  const combinedHTML = `
    <style>
      /* Ensure flexbox layouts work in preview */
      .cmp-contentimagecomponent {
        display: flex !important;
        flex-wrap: wrap !important;
        align-items: stretch !important;
        margin: 20px 0 !important;
      }
      .cmp-contentimagecomponent__container {
        display: flex !important;
        width: 100% !important;
      }
      .cmp-contentimagecomponent__text-section,
      .cmp-contentimagecomponent__image-section {
        flex: 1 !important;
        padding: 20px !important;
        box-sizing: border-box !important;
      }
      .cmp-contentimagecomponent__image-section {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
      }
      .cmp-contentimagecomponent__text-section {
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
      }
      .cmp-contentimagecomponent__image {
        max-width: 100% !important;
        height: auto !important;
        display: block !important;
      }
      
      /* Original component CSS */
      ${processedCSS}
    </style>
    ${processedHTML}
  `;

  return (
    <div className="visual-code-sandbox">
      <div 
        className="preview-container"
        dangerouslySetInnerHTML={{ __html: combinedHTML }}
        style={{ 
          overflow: 'auto', 
          height: '100%',
          paddingTop: '8px', // Extra space to avoid close button
          marginTop: '8px'
        }}
      />
    </div>
  );
};

export default VisualCodeSandbox;
