SYSTEM_PROMPT_GENERATE_AGENT = """You are an expert AEM Edge Delivery Services block generator following Adobe's official standards and best practices.

**Core Principles:**
1. Content-driven development: The markdown table is the contract between authors and developers
2. Progressive enhancement: Build for performance with three-phase loading in mind
3. Accessibility-first: WCAG 2.1 AA compliance with keyboard navigation and screen readers
4. Mobile-first responsive design with breakpoints at 600px, 900px, and 1200px

**Your Role:**
Generate clean, standards-compliant EDS blocks that:
- Follow Adobe's decoration patterns and DOM manipulation best practices
- Use ES6+ JavaScript with proper imports (always include .js extensions)
- Implement mobile-first CSS with block-scoped selectors
- Support accessibility features including keyboard navigation
- Provide clear authoring guidance through markdown tables

**Quality Standards:**
- Code must pass ESLint (Airbnb) and Stylelint (standard config)
- All functionality must be testable and maintainable
- Performance-optimized with minimal DOM manipulation
- Semantic HTML5 with proper ARIA attributes
"""

SYSTEM_PROMPT_EXTRACT_AGENT = """You are an expert AI assistant specialized in extracting structured information from natural language descriptions of AEM Edge Delivery Services blocks.

**Your Goal:**
Accurately identify and categorize:
- Block name (lowercase, kebab-case)
- Block style/variant
- Block type category
- Detailed functionality description

**Standards:**
- Follow Adobe's EDS naming conventions
- Infer reasonable defaults based on common patterns
- Provide comprehensive functionality descriptions including accessibility and responsive behavior
- Output only valid JSON

**Quality:**
- Be specific and detailed in descriptions
- Include accessibility features (keyboard navigation, screen reader support)
- Describe responsive behavior across breakpoints
- Mention author customization options
"""

SAMPLE_ASSISTANT_OUTPUT = {
    "tree": {
        "name": "tabs",
        "type": "directory",
        "children": [
            {
                "name": "tabs.js",
                "type": "file",
            },
            {
                "name": "tabs.css",
                "type": "file",
            },
        ],
    },
    "files": [
        {
            "type": "javascript",
            "path": "blocks/tabs/tabs.js",
            "content": """
      function hasWrapper(el) {
        return !!el.firstElementChild && window.getComputedStyle(el.firstElementChild).display === 'block';
      }
      export default async function decorate(block) {
        const tablist = document.createElement('div');
        tablist.className = 'tabs-list';
        const tabs = [...block.children].map((child) => child.firstElementChild);
        tabs.forEach((tab, i) => {
          const id = "tab-" + i;
          const tabpanel = block.children[i];
          tabpanel.className = 'tabs-panel';
          tabpanel.id = `tabpanel-${id}`;
          const button = document.createElement('button');
          button.className = 'tabs-tab';
          button.innerHTML = tab.innerHTML;
          button.setAttribute('type', 'button');
          button.addEventListener('click', () => {
            block.querySelectorAll('[role=tabpanel]').forEach((panel) => {
              panel.setAttribute('aria-hidden', true);
            });
            tablist.querySelectorAll('button').forEach((btn) => {
              btn.setAttribute('aria-selected', false);
            });
          });
          tablist.append(button);
          tab.remove();
        });
        block.prepend(tablist);
      }
    """,
            "name": "tabs.js",
        },
        {
            "type": "css",
            "path": "blocks/tabs/tabs.css",
            "content": """
      .tabs .tabs-list {
        display: flex;
        gap: 8px;
        max-width: 100%;
      }
      .tabs .tabs-list button {
        flex: 0 0 max-content;
        padding: 8px 16px;
        overflow: unset;
      }
      .tabs .tabs-list button[aria-selected="true"] {
        background-color: white;
      }
      .tabs .tabs-panel[aria-hidden="true"] {
        display: none;
      }
    """,
            "name": "tabs.css",
        },
    ],
    "mdtable": """
  | Tabs    |              |
  |---------|--------------|
  | Tab1    | tab one text | 
  | Tab Two | tab two text |
""",
    "inputHtml": """
<div>
  <div>
    <div>Tab One</div>
    <div>tab one text</div>
  </div>
  <div>
    <div>Tab Two</div>
    <div>tab two text</div>
  </div>
</div>
  """,
}

DEFAULT_BLOCKS_CODE = """
export default async function decorate(block) {
    const tablist = document.createElement('div');
tablist.className = 'tabs-list';
const tabs = [...block.children].map((child) => child.firstElementChild);
tabs.forEach((tab, i) => {
    const id = "tab-" + i;
const tabpanel = block.children[i];
tabpanel.className = 'tabs-panel';
tabpanel.id = `tabpanel-${id}`;
const button = document.createElement('button');
button.className = 'tabs-tab';
button.innerHTML = tab.innerHTML;
button.setAttribute('type', 'button');
button.addEventListener('click', () => {
    block.querySelectorAll('[role=tabpanel]').forEach((panel) => {
    panel.setAttribute('aria-hidden', true);
});
tablist.querySelectorAll('button').forEach((btn) => {
    btn.setAttribute('aria-selected', false);
});
});
tablist.append(button);
tab.remove();
});
block.prepend(tablist);
}
"""

DEFAULT_BLOCKS_CODE_JS = """
export default async function decorate(block) {
     const wrapper = document.createElement('div');
     [...block.children].forEach((row) => {
         // Logic to extract and style elements
     });
     block.textContent = '';
     block.append(wrapper);
 }
"""

AEM_EXPORTED_METHODS = [
    {"name": "buildBlock", "signature": "buildBlock(tagName: string, contentArray: Array<any>): Element"},
    {"name": "createOptimizedPicture", "signature": "createOptimizedPicture(src: string, alt?: string, eager?: boolean, breakpoints?: Array<any>): Element"},
    {"name": "decorateBlock", "signature": "decorateBlock(block: Element): void"},
    {"name": "decorateBlocks", "signature": "decorateBlocks(main: Element): Promise<void>"},
    {"name": "decorateButtons", "signature": "decorateButtons(element: Element): void"},
    {"name": "decorateIcons", "signature": "decorateIcons(element: Element): void"},
    {"name": "decorateSections", "signature": "decorateSections(main: Element): void"},
    {"name": "decorateTemplateAndTheme", "signature": "decorateTemplateAndTheme(): void"},
    {"name": "getMetadata", "signature": "getMetadata(name: string): string | null"},
    {"name": "loadBlock", "signature": "loadBlock(block: Element): Promise<void>"},
    {"name": "loadCSS", "signature": "loadCSS(href: string): Promise<void>"},
    {"name": "loadFooter", "signature": "loadFooter(footer: Element): Promise<void>"},
    {"name": "loadHeader", "signature": "loadHeader(header: Element): Promise<void>"},
    {"name": "loadScript", "signature": "loadScript(src: string, callback?: Function, type?: string): Promise<void>"},
    {"name": "loadSection", "signature": "loadSection(section: Element): Promise<void>"},
    {"name": "loadSections", "signature": "loadSections(main: Element): Promise<void>"},
    {"name": "readBlockConfig", "signature": "readBlockConfig(block: Element): Record<string, string | string[]>"},
    {"name": "sampleRUM", "signature": "sampleRUM(checkpoint: string, data?: Record<string, any>): void"},
    {"name": "setup", "signature": "setup(): void"},
    {"name": "toCamelCase", "signature": "toCamelCase(name: string): string"},
    {"name": "toClassName", "signature": "toClassName(name: string): string"},
    {"name": "waitForFirstImage", "signature": "waitForFirstImage(main: Element): Promise<void>"},
    {"name": "wrapTextNodes", "signature": "wrapTextNodes(element: Element, spanClass?: string): void"},
]