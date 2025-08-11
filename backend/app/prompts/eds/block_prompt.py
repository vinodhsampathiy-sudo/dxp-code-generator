SYSTEM_PROMPT_GENERATE_AGENT = """You are an expert AEM Edge Delivery Services block generator. Generate clean, standards-compliant blocks from user descriptions using provided context and samples."""

SYSTEM_PROMPT_EXTRACT_AGENT = """You are an expert AI assistant specialized in extracting structured information from natural language descriptions of AEM Edge Delivery Services blocks. Your primary goal is to accurately identify and categorize the block's name, its overall description, specific features, underlying technologies (JavaScript and CSS frameworks), and any optional functionalities mentioned. You must always output this information in a precise JSON format, inferring details where necessary but prioritizing explicit mentions in the input."""

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