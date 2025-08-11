from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document

def create_vector_store():
    examples = [{
                "name": "Text Component",
                "framework": "AEM + HTL + Sling Model",
                "code": """<!-- HTL Template -->
        <div class="cmp-text" data-cmp-is="text" data-sly-use.textModel="com.adobe.cq.wcm.core.components.models.Text">
            <div class="cmp-text__paragraph" data-sly-test="${textModel.text}">${textModel.text @ context='html'}</div>
        </div>
        
        /* Sling Model */
        @Model(adaptables = SlingHttpServletRequest.class, 
               adapters = {Text.class, ComponentExporter.class},
               resourceType = Text.RESOURCE_TYPE)
        @Exporter(name = ExporterConstants.SLING_MODEL_EXPORTER_NAME, extensions = ExporterConstants.JSON)
        public class TextImpl implements Text {
            
            @ValueMapValue
            private String text;
            
            @Override
            public String getText() {
                return text;
            }
        }""",
                "description": "Text component with HTL template and Sling Model for business logic"
            },
            {
                "name": "Image Component with Dialog",
                "framework": "AEM + HTL + Sling Model + Dialog",
                "code": """<!-- HTL Template -->
        <div class="cmp-image" data-cmp-is="image" data-sly-use.imageModel="com.adobe.cq.wcm.core.components.models.Image">
            <img class="cmp-image__image" 
                 src="${imageModel.src}" 
                 alt="${imageModel.alt}"
                 data-sly-test="${imageModel.src}"/>
        </div>
        
        /* Sling Model */
        @Model(adaptables = SlingHttpServletRequest.class,
               adapters = {Image.class, ComponentExporter.class},
               resourceType = Image.RESOURCE_TYPE)
        public class ImageImpl implements Image {
            
            @ValueMapValue
            private String fileReference;
            
            @ValueMapValue
            private String alt;
            
            @Override
            public String getSrc() {
                return fileReference;
            }
            
            @Override
            public String getAlt() {
                return alt;
            }
        }
        
        <!-- Dialog XML -->
        <?xml version="1.0" encoding="UTF-8"?>
        <jcr:root xmlns:sling="http://sling.apache.org/jcr/sling/1.0" 
                  xmlns:granite="http://www.adobe.com/jcr/granite/1.0" 
                  xmlns:cq="http://www.day.com/jcr/cq/1.0" 
                  xmlns:jcr="http://www.jcp.org/jcr/1.0" 
                  xmlns:nt="http://www.jcp.org/jcr/nt/1.0"
            jcr:primaryType="nt:unstructured"
            jcr:title="Image"
            sling:resourceType="cq/gui/components/authoring/dialog">
            <content jcr:primaryType="nt:unstructured"
                     sling:resourceType="granite/ui/components/coral/foundation/container">
                <items jcr:primaryType="nt:unstructured">
                    <tabs jcr:primaryType="nt:unstructured"
                          sling:resourceType="granite/ui/components/coral/foundation/tabs"
                          maximized="{Boolean}true">
                        <items jcr:primaryType="nt:unstructured">
                            <asset jcr:primaryType="nt:unstructured"
                                   jcr:title="Asset"
                                   sling:resourceType="granite/ui/components/coral/foundation/container">
                                <items jcr:primaryType="nt:unstructured">
                                    <columns jcr:primaryType="nt:unstructured"
                                             sling:resourceType="granite/ui/components/coral/foundation/fixedcolumns"
                                             margin="{Boolean}true">
                                        <items jcr:primaryType="nt:unstructured">
                                            <column jcr:primaryType="nt:unstructured"
                                                    sling:resourceType="granite/ui/components/coral/foundation/container">
                                                <items jcr:primaryType="nt:unstructured">
                                                    <file jcr:primaryType="nt:unstructured"
                                                          sling:resourceType="cq/gui/components/authoring/dialog/fileupload"
                                                          autoStart="{Boolean}false"
                                                          class="cq-droptarget"
                                                          fieldLabel="Image asset"
                                                          fileNameParameter="./fileName"
                                                          fileReferenceParameter="./fileReference"
                                                          mimeTypes="[image]"
                                                          multiple="{Boolean}false"
                                                          name="./file"
                                                          title="Upload Image Asset"
                                                          uploadUrl="${suffix.path}"
                                                          useHTML5="{Boolean}true"/>
                                                    <alt jcr:primaryType="nt:unstructured"
                                                         sling:resourceType="granite/ui/components/coral/foundation/form/textfield"
                                                         fieldLabel="Alternative text"
                                                         name="./alt"/>
                                                </items>
                                            </column>
                                        </items>
                                    </columns>
                                </items>
                            </asset>
                        </items>
                    </tabs>
                </items>
            </content>
        </jcr:root>""",
                "description": "Complete AEM image component with HTL template, Sling Model, and Touch UI dialog"
            },
            {
                "name": "Navigation Component",
                "framework": "AEM + HTL + Sling Model",
                "code": """<!-- HTL Template -->
        <nav class="cmp-navigation" data-cmp-is="navigation" data-sly-use.navModel="com.adobe.cq.wcm.core.components.models.Navigation">
            <ul class="cmp-navigation__group" data-sly-list.item="${navModel.items}">
                <li class="cmp-navigation__item">
                    <a class="cmp-navigation__item-link" href="${item.URL}">${item.title}</a>
                </li>
            </ul>
        </nav>
        
        /* Sling Model */
        @Model(adaptables = SlingHttpServletRequest.class,
               adapters = {Navigation.class, ComponentExporter.class},
               resourceType = Navigation.RESOURCE_TYPE)
        public class NavigationImpl implements Navigation {
            
            @ValueMapValue
            private int structureDepth;
            
            @SlingObject
            private ResourceResolver resourceResolver;
            
            @Override
            public List<NavigationItem> getItems() {
                // Navigation logic implementation
                return buildNavigationItems();
            }
        }""",
                "description": "Navigation component with dynamic menu generation"
            },
            {
                "name": "Button Component",
                "framework": "AEM + HTL",
                "code": """<div class="cmp-button" data-cmp-is="button">
            <a class="cmp-button__link" 
               href="${properties.link}" 
               data-sly-test="${properties.link}"
               target="${properties.target}">
                ${properties.text}
            </a>
        </div>""",
                "description": "Simple button component with link and target properties"
            },
            {
                "name": "List Component",
                "framework": "AEM + HTL + Sling Model",
                "code": """<!-- HTL Template -->
        <div class="cmp-list" data-cmp-is="list" data-sly-use.listModel="com.adobe.cq.wcm.core.components.models.List">
            <ul class="cmp-list__group" data-sly-list.item="${listModel.listItems}">
                <li class="cmp-list__item">
                    <article class="cmp-list__item-article">
                        <h3 class="cmp-list__item-title">
                            <a href="${item.URL}">${item.title}</a>
                        </h3>
                        <span class="cmp-list__item-date">${item.lastModified @ format='dd MMM yyyy'}</span>
                    </article>
                </li>
            </ul>
        </div>
        
        /* Sling Model */
        @Model(adaptables = SlingHttpServletRequest.class,
               adapters = {List.class, ComponentExporter.class},
               resourceType = List.RESOURCE_TYPE)
        public class ListImpl implements List {
            
            @ValueMapValue
            private String listFrom;
            
            @ValueMapValue
            private String[] tags;
            
            @Override
            public Collection<ListItem> getListItems() {
                return buildListItems();
            }
        }""",
                "description": "List component that can show children pages or tagged content"
            },
            {
                "name": "Teaser Component",
                "framework": "AEM + HTL + Sling Model",
                "code": """<!-- HTL Template -->
        <div class="cmp-teaser" data-cmp-is="teaser" data-sly-use.teaserModel="com.adobe.cq.wcm.core.components.models.Teaser">
            <div class="cmp-teaser__image" data-sly-test="${teaserModel.imageResource}">
                <img src="${teaserModel.imageResource.path}" alt="${teaserModel.imageAlt}"/>
            </div>
            <div class="cmp-teaser__content">
                <h3 class="cmp-teaser__title">
                    <a href="${teaserModel.linkURL}">${teaserModel.title}</a>
                </h3>
                <div class="cmp-teaser__description">${teaserModel.description @ context='html'}</div>
            </div>
        </div>
        
        /* Sling Model */
        @Model(adaptables = SlingHttpServletRequest.class,
               adapters = {Teaser.class, ComponentExporter.class},
               resourceType = Teaser.RESOURCE_TYPE)
        public class TeaserImpl implements Teaser {
            
            @ValueMapValue
            private String jcrTitle;
            
            @ValueMapValue
            private String jcrDescription;
            
            @ValueMapValue
            private String linkURL;
            
            @Override
            public String getTitle() {
                return jcrTitle;
            }
            
            @Override
            public String getDescription() {
                return jcrDescription;
            }
            
            @Override
            public String getLinkURL() {
                return linkURL;
            }
        }""",
                "description": "Teaser component with image, title, description and link functionality"
            },
            {
                "name": "Content Fragment Component",
                "framework": "AEM + HTL + Sling Model",
                "code": """<!-- HTL Template -->
        <div class="cmp-contentfragment" data-cmp-is="contentfragment" data-sly-use.cfModel="com.adobe.cq.wcm.core.components.models.ContentFragment">
            <div class="cmp-contentfragment__elements" data-sly-list.element="${cfModel.elements}">
                <div class="cmp-contentfragment__element">
                    <h4 class="cmp-contentfragment__element-title">${element.title}</h4>
                    <div class="cmp-contentfragment__element-value">${element.value @ context='html'}</div>
                </div>
            </div>
        </div>
        
        /* Sling Model */
        @Model(adaptables = SlingHttpServletRequest.class,
               adapters = {ContentFragment.class, ComponentExporter.class},
               resourceType = ContentFragment.RESOURCE_TYPE)
        public class ContentFragmentImpl implements ContentFragment {
            
            @ValueMapValue
            private String fragmentPath;
            
            @ValueMapValue
            private String[] elementNames;
            
            @Override
            public Map<String, Object> getElements() {
                return getContentFragmentElements();
            }
        }""",
                "description": "Content Fragment component for structured content display"
            }
        ]

    docs = [
        Document(
            page_content=f"{ex['name']} - {ex['description']}. Framework: {ex['framework']}. Code: {ex['code']}",
            metadata={
                "name": ex["name"],
                "framework": ex["framework"],
                "description": ex["description"],
                "type": "aem-component"
            }
        )
        for ex in examples
    ]

    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(docs, embeddings)

    return db