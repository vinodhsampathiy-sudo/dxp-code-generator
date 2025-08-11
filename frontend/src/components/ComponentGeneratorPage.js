import React, { useState } from 'react';
import PromptInputPanel from './PromptInputPanel';
import CodeOutputPanel from './CodeOutputPanel';

export default function ComponentGeneratorPage() {
  const [output, setOutput] = useState({});

  return (
    <div style={{ display: 'flex', height: '100%' }}>
      <PromptInputPanel setOutput={setOutput} />
      <CodeOutputPanel output={output} />
    </div>
  );
}
