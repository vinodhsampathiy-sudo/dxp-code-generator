import React from 'react';

export default function CodeOutputPanel({ output }) {
  const { htl, slingModel, dialog, clientLib } = output;

  const files = [
    {
      name: 'component.html',
      path: 'ui.apps/src/main/content/jcr_root/apps/{appId}/components/{componentName}/component.html',
      content: htl || '// HTL will appear here'
    },
    {
      name: '_cq_dialog.xml',
      path: 'ui.apps/src/main/content/jcr_root/apps/{appId}/components/{componentName}/_cq_dialog.xml',
      content: dialog || '// Dialog XML will appear here'
    },
    {
      name: 'SlingModel.java',
      path: 'core/src/main/java/{package path}/{componentName}/models/SlingModel.java',
      content: slingModel || '// Sling Model will appear here'
    },
    {
      name: 'clientLib',
      path: 'ui.apps/src/main/content/jcr_root/apps/{appId}/components/{componentName}/clientlib/',
      content: clientLib || '// Clientlib will appear here'
    }
  ];

  return (
    <div style={{ flex: 1, padding: 20, background: '#f5f5f5', overflowY: 'auto' }}>
      <h2>Generated Project Structure</h2>
      
      <div style={{ fontFamily: 'monospace', fontSize: 14 }}>
        <div>
          <span style={{ fontWeight: 'bold' }}>output/</span>
          <div style={{ paddingLeft: 20 }}>
            <div><span style={{ fontWeight: 'bold' }}>core/</span></div>
            <div style={{ paddingLeft: 20 }}>
              <div><span style={{ fontWeight: 'bold' }}>src/main/java/</span></div>
              <div style={{ paddingLeft: 20 }}>
                <div><span style={{ fontWeight: 'bold' }}>{'{package path}'}/</span></div>
                <div style={{ paddingLeft: 20 }}>
                  <div style={{ paddingLeft: 20 }}>
                    <span style={{ fontWeight: 'bold' }}>models/</span>
                  </div>
                  <FileDisplay file={files[2]} />
                </div>
              </div>
            </div>
            <div><span style={{ fontWeight: 'bold' }}>ui.apps/</span></div>
            <div style={{ paddingLeft: 20 }}>
              <div><span style={{ fontWeight: 'bold' }}>src/main/content/jcr_root/apps/{'{appId}'}/components/{'{componentName}'}/</span></div>
              <div style={{ paddingLeft: 20 }}>
                <FileDisplay file={files[0]} />
                <FileDisplay file={files[1]} />
              </div>
            </div>
            <div style={{ paddingLeft: 20 }}>
              <div><span style={{ fontWeight: 'bold' }}>src/main/content/jcr_root/apps/{'{appId}'}/components/{'{componentName}'}/</span></div>
              <div style={{ paddingLeft: 20 }}>
                <span style={{ fontWeight: 'bold' }}>clientlib/</span>
                <FileDisplay file={files[3]} />
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}

function FileDisplay({ file }) {
  const [showContent, setShowContent] = React.useState(false);

  return (
    <div>
      <div
        style={{ cursor: 'pointer', color: '#007acc' }}
        onClick={() => setShowContent(!showContent)}
      >
        📄 {file.name}
      </div>
      {showContent && (
        <pre
          style={{
            background: '#1e1e1e',
            color: '#d4d4d4',
            padding: 10,
            overflowX: 'auto',
            borderRadius: 4
          }}
        >
          {file.content}
        </pre>
      )}
    </div>
  );
}
