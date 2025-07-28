import React, { useState, useRef } from 'react';
import { Upload, Button, Card, Tabs, Input, Select, Spin, message, Typography, Divider, Tag, Space, List, Image } from 'antd';
import { InboxOutlined, FileTextOutlined, FileImageOutlined, FilePdfOutlined, FileUnknownOutlined, SearchOutlined, DownloadOutlined } from '@ant-design/icons';
import { multimodalService } from '../services/multimodalService';

const { TabPane } = Tabs;
const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Option } = Select;
const { Dragger } = Upload;

const fileTypeIcons = {
  pdf: <FilePdfOutlined />,
  image: <FileImageOutlined />,
  text: <FileTextOutlined />,
  default: <FileUnknownOutlined />
};

const MultimodalDocumentAnalysis = () => {
  const [files, setFiles] = useState([]);
  const [activeTab, setActiveTab] = useState('upload');
  const [query, setQuery] = useState('');
  const [analysisType, setAnalysisType] = useState('general');
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedModel, setSelectedModel] = useState('default');
  const [filePreview, setFilePreview] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [documentCollection, setDocumentCollection] = useState('default');
  const fileInputRef = useRef(null);

  const analysisTypes = [
    { value: 'general', label: 'Allgemeine Analyse' },
    { value: 'rfi', label: 'RFI-Analyse' },
    { value: 'compliance', label: 'Compliance-Prüfung' },
    { value: 'cost', label: 'Kostenschätzung' },
    { value: 'schedule', label: 'Terminplanauswirkung' },
    { value: 'technical', label: 'Technische Analyse' },
    { value: 'extraction', label: 'Datenextraktion' }
  ];

  const modelOptions = [
    { value: 'default', label: 'Standard (Auto-Select)' },
    { value: 'openai-gpt4-vision', label: 'OpenAI GPT-4 Vision' },
    { value: 'gemini-pro-vision', label: 'Google Gemini Pro Vision' },
    { value: 'ollama-llava', label: 'Ollama LLaVA' }
  ];

  const documentCollections = [
    { value: 'default', label: 'Standard-Sammlung' },
    { value: 'project-docs', label: 'Projektdokumente' },
    { value: 'technical-specs', label: 'Technische Spezifikationen' },
    { value: 'contracts', label: 'Verträge' },
    { value: 'regulations', label: 'Vorschriften und Normen' }
  ];

  const handleFileUpload = ({ file, fileList }) => {
    if (file.status === 'done') {
      message.success(`${file.name} erfolgreich hochgeladen.`);
      setFiles(fileList.map(f => ({
        uid: f.uid,
        name: f.name,
        status: f.status,
        url: f.response?.url || '',
        type: getFileType(f.name),
        size: f.size,
        response: f.response
      })));
    } else if (file.status === 'error') {
      message.error(`${file.name} konnte nicht hochgeladen werden.`);
    }
  };

  const getFileType = (filename) => {
    const extension = filename.split('.').pop().toLowerCase();
    if (['pdf'].includes(extension)) return 'pdf';
    if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg'].includes(extension)) return 'image';
    if (['txt', 'doc', 'docx', 'rtf', 'odt'].includes(extension)) return 'text';
    return 'default';
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      message.warning('Bitte wählen Sie eine Datei aus.');
      return;
    }

    try {
      setAnalyzing(true);
      const response = await multimodalService.analyzeDocument({
        file_id: selectedFile.uid,
        analysis_type: analysisType,
        query: query,
        model: selectedModel
      });
      
      setResults(response);
      setActiveTab('results');
      message.success('Analyse erfolgreich abgeschlossen.');
    } catch (error) {
      message.error('Fehler bei der Analyse: ' + (error.message || 'Unbekannter Fehler'));
    } finally {
      setAnalyzing(false);
    }
  };

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    
    // Dateivorschau laden
    if (file.type === 'image') {
      setFilePreview({
        type: 'image',
        url: file.url
      });
    } else if (file.type === 'pdf') {
      setFilePreview({
        type: 'pdf',
        url: file.url
      });
    } else {
      setFilePreview(null);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      message.warning('Bitte geben Sie einen Suchbegriff ein.');
      return;
    }

    try {
      setSearchLoading(true);
      const response = await multimodalService.searchDocuments({
        query: searchQuery,
        collection: documentCollection,
        limit: 10
      });
      
      setSearchResults(response.results);
      message.success(`${response.results.length} Dokumente gefunden.`);
    } catch (error) {
      message.error('Fehler bei der Suche: ' + (error.message || 'Unbekannter Fehler'));
    } finally {
      setSearchLoading(false);
    }
  };

  const uploadProps = {
    name: 'file',
    multiple: true,
    action: '/api/multimodal/upload',
    onChange: handleFileUpload,
    showUploadList: false,
    beforeUpload: (file) => {
      const isValidType = [
        'application/pdf',
        'image/jpeg',
        'image/png',
        'image/gif',
        'text/plain',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      ].includes(file.type);
      
      if (!isValidType) {
        message.error(`${file.name} ist kein unterstützter Dateityp.`);
      }
      
      return isValidType || Upload.LIST_IGNORE;
    }
  };

  const renderFileIcon = (type) => {
    return fileTypeIcons[type] || fileTypeIcons.default;
  };

  const renderResults = () => {
    if (!results) return null;

    return (
      <div className="results-container">
        <Card className="mb-4">
          <Title level={4}>Analyseergebnisse</Title>
          <Divider />
          
          {results.summary && (
            <div className="mb-4">
              <Title level={5}>Zusammenfassung</Title>
              <Paragraph>{results.summary}</Paragraph>
            </div>
          )}
          
          {results.key_points && results.key_points.length > 0 && (
            <div className="mb-4">
              <Title level={5}>Kernpunkte</Title>
              <List
                dataSource={results.key_points}
                renderItem={item => (
                  <List.Item>
                    <Text>{item}</Text>
                  </List.Item>
                )}
              />
            </div>
          )}
          
          {results.entities && results.entities.length > 0 && (
            <div className="mb-4">
              <Title level={5}>Erkannte Entitäten</Title>
              <Space wrap>
                {results.entities.map((entity, index) => (
                  <Tag key={index} color={entity.type === 'person' ? 'blue' : entity.type === 'organization' ? 'green' : 'orange'}>
                    {entity.text} ({entity.type})
                  </Tag>
                ))}
              </Space>
            </div>
          )}
          
          {results.extracted_data && Object.keys(results.extracted_data).length > 0 && (
            <div className="mb-4">
              <Title level={5}>Extrahierte Daten</Title>
              <List
                dataSource={Object.entries(results.extracted_data)}
                renderItem={([key, value]) => (
                  <List.Item>
                    <Text strong>{key}:</Text> <Text>{value}</Text>
                  </List.Item>
                )}
              />
            </div>
          )}
          
          {results.recommendations && results.recommendations.length > 0 && (
            <div className="mb-4">
              <Title level={5}>Empfehlungen</Title>
              <List
                dataSource={results.recommendations}
                renderItem={item => (
                  <List.Item>
                    <Text>{item}</Text>
                  </List.Item>
                )}
              />
            </div>
          )}
          
          {results.answer && (
            <div className="mb-4">
              <Title level={5}>Antwort auf Ihre Frage</Title>
              <Paragraph>{results.answer}</Paragraph>
            </div>
          )}
        </Card>
      </div>
    );
  };

  const renderFilePreview = () => {
    if (!filePreview) return null;

    if (filePreview.type === 'image') {
      return (
        <div className="file-preview">
          <Image
            src={filePreview.url}
            alt="Dateivorschau"
            style={{ maxWidth: '100%', maxHeight: '400px' }}
          />
        </div>
      );
    } else if (filePreview.type === 'pdf') {
      return (
        <div className="file-preview">
          <iframe
            src={`${filePreview.url}#toolbar=0`}
            title="PDF Vorschau"
            width="100%"
            height="400px"
            style={{ border: 'none' }}
          />
        </div>
      );
    }

    return null;
  };

  return (
    <div className="multimodal-document-analysis p-4">
      <Title level={3}>Multimodale Dokumentenanalyse</Title>
      <Paragraph>
        Analysieren Sie Dokumente verschiedener Formate mit KI-gestützten Modellen. 
        Laden Sie Dateien hoch, stellen Sie Fragen und erhalten Sie detaillierte Analysen.
      </Paragraph>
      
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab="Dokumente hochladen" key="upload">
          <div className="upload-container">
            <Dragger {...uploadProps} className="mb-4">
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">Klicken oder ziehen Sie Dateien in diesen Bereich, um sie hochzuladen</p>
              <p className="ant-upload-hint">
                Unterstützt werden PDF, Bilder (JPG, PNG, GIF) und Textdokumente (TXT, DOC, DOCX)
              </p>
            </Dragger>
            
            <div className="file-list mb-4">
              <Title level={4}>Hochgeladene Dokumente</Title>
              {files.length === 0 ? (
                <Text type="secondary">Keine Dokumente hochgeladen</Text>
              ) : (
                <List
                  dataSource={files}
                  renderItem={file => (
                    <List.Item
                      key={file.uid}
                      className={`file-item ${selectedFile?.uid === file.uid ? 'selected' : ''}`}
                      onClick={() => handleFileSelect(file)}
                      style={{ cursor: 'pointer', padding: '8px', borderRadius: '4px', backgroundColor: selectedFile?.uid === file.uid ? '#f0f5ff' : 'transparent' }}
                    >
                      <List.Item.Meta
                        avatar={renderFileIcon(file.type)}
                        title={file.name}
                        description={`${(file.size / 1024).toFixed(2)} KB`}
                      />
                    </List.Item>
                  )}
                />
              )}
            </div>
            
            {selectedFile && (
              <div className="analysis-options mb-4">
                <Title level={4}>Analyseoptionen</Title>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <Text strong>Analysetyp</Text>
                    <Select
                      value={analysisType}
                      onChange={setAnalysisType}
                      style={{ width: '100%' }}
                      className="mb-2"
                    >
                      {analysisTypes.map(type => (
                        <Option key={type.value} value={type.value}>{type.label}</Option>
                      ))}
                    </Select>
                  </div>
                  
                  <div>
                    <Text strong>Modell</Text>
                    <Select
                      value={selectedModel}
                      onChange={setSelectedModel}
                      style={{ width: '100%' }}
                      className="mb-2"
                    >
                      {modelOptions.map(model => (
                        <Option key={model.value} value={model.value}>{model.label}</Option>
                      ))}
                    </Select>
                  </div>
                </div>
                
                <div className="mb-4">
                  <Text strong>Frage oder Anweisung (optional)</Text>
                  <TextArea
                    value={query}
                    onChange={e => setQuery(e.target.value)}
                    placeholder="Stellen Sie eine Frage zum Dokument oder geben Sie eine spezifische Anweisung für die Analyse..."
                    rows={4}
                  />
                </div>
                
                {renderFilePreview()}
                
                <Button
                  type="primary"
                  icon={<SearchOutlined />}
                  onClick={handleAnalyze}
                  loading={analyzing}
                  className="mt-4"
                >
                  Dokument analysieren
                </Button>
              </div>
            )}
          </div>
        </TabPane>
        
        <TabPane tab="Dokumentensuche" key="search">
          <div className="search-container">
            <Card className="mb-4">
              <Title level={4}>Dokumentensuche</Title>
              <Paragraph>
                Durchsuchen Sie die Dokumentensammlung nach relevanten Informationen.
              </Paragraph>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div className="md:col-span-2">
                  <Input
                    placeholder="Suchbegriff eingeben..."
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    onPressEnter={handleSearch}
                    prefix={<SearchOutlined />}
                  />
                </div>
                
                <div>
                  <Select
                    value={documentCollection}
                    onChange={setDocumentCollection}
                    style={{ width: '100%' }}
                  >
                    {documentCollections.map(collection => (
                      <Option key={collection.value} value={collection.value}>{collection.label}</Option>
                    ))}
                  </Select>
                </div>
              </div>
              
              <Button
                type="primary"
                onClick={handleSearch}
                loading={searchLoading}
              >
                Suchen
              </Button>
            </Card>
            
            {searchLoading ? (
              <div className="text-center py-8">
                <Spin size="large" />
                <div className="mt-4">Suche läuft...</div>
              </div>
            ) : searchResults.length > 0 ? (
              <List
                dataSource={searchResults}
                renderItem={item => (
                  <List.Item
                    actions={[
                      <Button
                        key="view"
                        type="link"
                        onClick={() => {
                          // Dokument zur Analyse auswählen
                          const file = {
                            uid: item.id,
                            name: item.filename,
                            type: getFileType(item.filename),
                            url: item.url,
                            size: item.size || 0
                          };
                          handleFileSelect(file);
                          setActiveTab('upload');
                        }}
                      >
                        Analysieren
                      </Button>,
                      <Button
                        key="download"
                        type="link"
                        icon={<DownloadOutlined />}
                        href={item.url}
                        target="_blank"
                      >
                        Herunterladen
                      </Button>
                    ]}
                  >
                    <List.Item.Meta
                      avatar={renderFileIcon(getFileType(item.filename))}
                      title={item.filename}
                      description={
                        <div>
                          <div>{item.description || 'Keine Beschreibung verfügbar'}</div>
                          <div className="text-xs text-gray-500 mt-1">
                            Relevanz: {(item.score * 100).toFixed(0)}% | 
                            Hochgeladen: {new Date(item.uploaded_at).toLocaleDateString()}
                          </div>
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            ) : searchQuery ? (
              <div className="text-center py-8 text-gray-500">
                <FileUnknownOutlined style={{ fontSize: '48px' }} />
                <div className="mt-4">Keine Dokumente gefunden.</div>
              </div>
            ) : null}
          </div>
        </TabPane>
        
        <TabPane tab="Analyseergebnisse" key="results">
          {loading ? (
            <div className="text-center py-8">
              <Spin size="large" />
              <div className="mt-4">Analyse wird durchgeführt...</div>
            </div>
          ) : (
            renderResults()
          )}
        </TabPane>
      </Tabs>
    </div>
  );
};

export default MultimodalDocumentAnalysis;

