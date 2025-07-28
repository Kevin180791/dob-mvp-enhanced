import React, { useState, useEffect } from 'react';
import { Card, Tabs, List, Avatar, Badge, Button, Modal, Input, Select, Tag, Spin, Typography, Divider, Timeline, Collapse, message } from 'antd';
import { UserOutlined, RobotOutlined, TeamOutlined, SettingOutlined, PlusOutlined, EditOutlined, DeleteOutlined, SendOutlined, SyncOutlined, CheckCircleOutlined, CloseCircleOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { agentService } from '../services/agentService';

const { TabPane } = Tabs;
const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Option } = Select;
const { Panel } = Collapse;

const AgentCrew = () => {
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [taskLoading, setTaskLoading] = useState(false);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [taskModalVisible, setTaskModalVisible] = useState(false);
  const [newAgent, setNewAgent] = useState({
    name: '',
    description: '',
    type: 'rfi_analyst',
    model: 'default',
    parameters: {}
  });
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    agent_id: '',
    priority: 'medium',
    data: {}
  });
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState('1');

  const agentTypes = [
    { value: 'rfi_analyst', label: 'RFI-Analyst' },
    { value: 'plan_reviewer', label: 'Plan-Prüfer' },
    { value: 'communication_agent', label: 'Kommunikations-Agent' },
    { value: 'cost_estimation_agent', label: 'Kosten-Schätzungs-Agent' },
    { value: 'schedule_impact_agent', label: 'Terminplan-Auswirkungs-Agent' },
    { value: 'compliance_agent', label: 'Compliance-Agent' },
    { value: 'document_analysis_agent', label: 'Dokumentenanalyse-Agent' },
    { value: 'coordination_agent', label: 'Koordinations-Agent' }
  ];

  const modelOptions = [
    { value: 'default', label: 'Standard (Auto-Select)' },
    { value: 'openai-gpt4', label: 'OpenAI GPT-4' },
    { value: 'openai-gpt35', label: 'OpenAI GPT-3.5' },
    { value: 'gemini-pro', label: 'Google Gemini Pro' },
    { value: 'ollama-llama3', label: 'Ollama Llama 3' },
    { value: 'ollama-mistral', label: 'Ollama Mistral' }
  ];

  const priorityOptions = [
    { value: 'low', label: 'Niedrig', color: 'blue' },
    { value: 'medium', label: 'Mittel', color: 'orange' },
    { value: 'high', label: 'Hoch', color: 'red' }
  ];

  const statusColors = {
    idle: 'default',
    busy: 'processing',
    error: 'error',
    offline: 'default'
  };

  const taskStatusColors = {
    pending: 'default',
    running: 'processing',
    completed: 'success',
    failed: 'error',
    cancelled: 'default'
  };

  useEffect(() => {
    fetchAgents();
    fetchTasks();
  }, []);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      const data = await agentService.getAgents();
      setAgents(data);
      setLoading(false);
    } catch (error) {
      message.error('Fehler beim Laden der Agenten: ' + error.message);
      setLoading(false);
    }
  };

  const fetchTasks = async () => {
    try {
      setTaskLoading(true);
      const data = await agentService.getTasks();
      setTasks(data);
      setTaskLoading(false);
    } catch (error) {
      message.error('Fehler beim Laden der Tasks: ' + error.message);
      setTaskLoading(false);
    }
  };

  const handleCreateAgent = async () => {
    try {
      setLoading(true);
      await agentService.createAgent(newAgent);
      message.success('Agent erfolgreich erstellt');
      setCreateModalVisible(false);
      setNewAgent({
        name: '',
        description: '',
        type: 'rfi_analyst',
        model: 'default',
        parameters: {}
      });
      fetchAgents();
    } catch (error) {
      message.error('Fehler beim Erstellen des Agenten: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateAgent = async (agentId, data) => {
    try {
      setLoading(true);
      await agentService.updateAgent(agentId, data);
      message.success('Agent erfolgreich aktualisiert');
      fetchAgents();
      if (selectedAgent && selectedAgent.id === agentId) {
        const agent = await agentService.getAgent(agentId);
        setSelectedAgent(agent);
      }
    } catch (error) {
      message.error('Fehler beim Aktualisieren des Agenten: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAgent = async (agentId) => {
    try {
      setLoading(true);
      await agentService.deleteAgent(agentId);
      message.success('Agent erfolgreich gelöscht');
      fetchAgents();
      if (selectedAgent && selectedAgent.id === agentId) {
        setSelectedAgent(null);
      }
    } catch (error) {
      message.error('Fehler beim Löschen des Agenten: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async () => {
    try {
      setTaskLoading(true);
      await agentService.createTask(newTask);
      message.success('Task erfolgreich erstellt');
      setTaskModalVisible(false);
      setNewTask({
        title: '',
        description: '',
        agent_id: '',
        priority: 'medium',
        data: {}
      });
      fetchTasks();
    } catch (error) {
      message.error('Fehler beim Erstellen des Tasks: ' + error.message);
    } finally {
      setTaskLoading(false);
    }
  };

  const handleCancelTask = async (taskId) => {
    try {
      setTaskLoading(true);
      await agentService.cancelTask(taskId);
      message.success('Task erfolgreich abgebrochen');
      fetchTasks();
      if (selectedTask && selectedTask.id === taskId) {
        const task = await agentService.getTask(taskId);
        setSelectedTask(task);
      }
    } catch (error) {
      message.error('Fehler beim Abbrechen des Tasks: ' + error.message);
    } finally {
      setTaskLoading(false);
    }
  };

  const handleSelectAgent = async (agentId) => {
    try {
      setLoading(true);
      const agent = await agentService.getAgent(agentId);
      setSelectedAgent(agent);
      setActiveTab('1');
      
      // Lade die Konversationen des Agenten
      const conversations = await agentService.getAgentConversations(agentId);
      setConversations(conversations);
      
      setLoading(false);
    } catch (error) {
      message.error('Fehler beim Laden des Agenten: ' + error.message);
      setLoading(false);
    }
  };

  const handleSelectTask = async (taskId) => {
    try {
      setTaskLoading(true);
      const task = await agentService.getTask(taskId);
      setSelectedTask(task);
      setTaskLoading(false);
    } catch (error) {
      message.error('Fehler beim Laden des Tasks: ' + error.message);
      setTaskLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!selectedAgent || !message.trim()) return;

    try {
      setLoading(true);
      await agentService.sendMessageToAgent(selectedAgent.id, { message });
      setMessage('');
      
      // Aktualisiere die Konversationen
      const conversations = await agentService.getAgentConversations(selectedAgent.id);
      setConversations(conversations);
      
      setLoading(false);
    } catch (error) {
      message.error('Fehler beim Senden der Nachricht: ' + error.message);
      setLoading(false);
    }
  };

  const renderAgentIcon = (type) => {
    switch (type) {
      case 'rfi_analyst':
        return <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#1890ff' }} />;
      case 'plan_reviewer':
        return <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#52c41a' }} />;
      case 'communication_agent':
        return <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#722ed1' }} />;
      case 'cost_estimation_agent':
        return <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#fa8c16' }} />;
      case 'schedule_impact_agent':
        return <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#eb2f96' }} />;
      case 'compliance_agent':
        return <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#f5222d' }} />;
      case 'document_analysis_agent':
        return <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#13c2c2' }} />;
      case 'coordination_agent':
        return <Avatar icon={<TeamOutlined />} style={{ backgroundColor: '#faad14' }} />;
      default:
        return <Avatar icon={<RobotOutlined />} style={{ backgroundColor: '#8c8c8c' }} />;
    }
  };

  const getAgentTypeLabel = (type) => {
    const agentType = agentTypes.find(t => t.value === type);
    return agentType ? agentType.label : type;
  };

  const getModelLabel = (modelId) => {
    const model = modelOptions.find(m => m.value === modelId);
    return model ? model.label : modelId;
  };

  const getPriorityLabel = (priority) => {
    const priorityOption = priorityOptions.find(p => p.value === priority);
    return priorityOption ? priorityOption.label : priority;
  };

  const getPriorityColor = (priority) => {
    const priorityOption = priorityOptions.find(p => p.value === priority);
    return priorityOption ? priorityOption.color : 'default';
  };

  return (
    <div className="agent-crew p-4">
      <div className="flex justify-between items-center mb-4">
        <Title level={3}>KI-Agenten-Crew</Title>
        <div className="space-x-2">
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setCreateModalVisible(true)}
          >
            Agent erstellen
          </Button>
          <Button
            type="default"
            icon={<PlusOutlined />}
            onClick={() => setTaskModalVisible(true)}
          >
            Task erstellen
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-1">
          <Card title="Agenten" loading={loading}>
            <List
              dataSource={agents}
              renderItem={agent => (
                <List.Item
                  key={agent.id}
                  className={`agent-item ${selectedAgent?.id === agent.id ? 'selected' : ''}`}
                  onClick={() => handleSelectAgent(agent.id)}
                  style={{ cursor: 'pointer', padding: '8px', borderRadius: '4px', backgroundColor: selectedAgent?.id === agent.id ? '#f0f5ff' : 'transparent' }}
                  actions={[
                    <Button
                      key="edit"
                      type="text"
                      icon={<EditOutlined />}
                      onClick={(e) => {
                        e.stopPropagation();
                        Modal.confirm({
                          title: 'Agent bearbeiten',
                          content: (
                            <div>
                              <div className="mb-2">
                                <label className="block mb-1">Name</label>
                                <Input
                                  defaultValue={agent.name}
                                  onChange={(e) => agent.name = e.target.value}
                                />
                              </div>
                              <div className="mb-2">
                                <label className="block mb-1">Beschreibung</label>
                                <Input.TextArea
                                  defaultValue={agent.description}
                                  onChange={(e) => agent.description = e.target.value}
                                  rows={2}
                                />
                              </div>
                              <div className="mb-2">
                                <label className="block mb-1">Modell</label>
                                <Select
                                  defaultValue={agent.model}
                                  style={{ width: '100%' }}
                                  onChange={(value) => agent.model = value}
                                >
                                  {modelOptions.map(model => (
                                    <Option key={model.value} value={model.value}>{model.label}</Option>
                                  ))}
                                </Select>
                              </div>
                            </div>
                          ),
                          onOk: () => handleUpdateAgent(agent.id, agent),
                          width: 500
                        });
                      }}
                    />,
                    <Button
                      key="delete"
                      type="text"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={(e) => {
                        e.stopPropagation();
                        Modal.confirm({
                          title: 'Agent löschen',
                          content: 'Möchten Sie diesen Agenten wirklich löschen?',
                          okText: 'Ja',
                          okType: 'danger',
                          cancelText: 'Nein',
                          onOk: () => handleDeleteAgent(agent.id)
                        });
                      }}
                    />
                  ]}
                >
                  <List.Item.Meta
                    avatar={renderAgentIcon(agent.type)}
                    title={
                      <div className="flex items-center">
                        <span>{agent.name}</span>
                        <Badge status={statusColors[agent.status]} className="ml-2" />
                      </div>
                    }
                    description={
                      <div>
                        <div>{getAgentTypeLabel(agent.type)}</div>
                        <div className="text-xs text-gray-500">Modell: {getModelLabel(agent.model)}</div>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>

          <Card title="Tasks" className="mt-4" loading={taskLoading}>
            <List
              dataSource={tasks}
              renderItem={task => (
                <List.Item
                  key={task.id}
                  className={`task-item ${selectedTask?.id === task.id ? 'selected' : ''}`}
                  onClick={() => handleSelectTask(task.id)}
                  style={{ cursor: 'pointer', padding: '8px', borderRadius: '4px', backgroundColor: selectedTask?.id === task.id ? '#f0f5ff' : 'transparent' }}
                  actions={[
                    task.status === 'pending' || task.status === 'running' ? (
                      <Button
                        key="cancel"
                        type="text"
                        danger
                        icon={<CloseCircleOutlined />}
                        onClick={(e) => {
                          e.stopPropagation();
                          Modal.confirm({
                            title: 'Task abbrechen',
                            content: 'Möchten Sie diesen Task wirklich abbrechen?',
                            okText: 'Ja',
                            okType: 'danger',
                            cancelText: 'Nein',
                            onOk: () => handleCancelTask(task.id)
                          });
                        }}
                      />
                    ) : null
                  ]}
                >
                  <List.Item.Meta
                    title={
                      <div className="flex items-center">
                        <span>{task.title}</span>
                        <Badge status={taskStatusColors[task.status]} className="ml-2" />
                      </div>
                    }
                    description={
                      <div>
                        <div className="flex items-center">
                          <Tag color={getPriorityColor(task.priority)}>{getPriorityLabel(task.priority)}</Tag>
                          <span className="text-xs text-gray-500 ml-2">
                            {task.agent_name || 'Kein Agent zugewiesen'}
                          </span>
                        </div>
                        <div className="text-xs text-gray-500">
                          Erstellt: {new Date(task.created_at).toLocaleString()}
                        </div>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </div>

        <div className="md:col-span-2">
          {selectedAgent ? (
            <Card
              title={
                <div className="flex justify-between items-center">
                  <div className="flex items-center">
                    {renderAgentIcon(selectedAgent.type)}
                    <span className="ml-2">{selectedAgent.name}</span>
                    <Badge status={statusColors[selectedAgent.status]} className="ml-2" />
                  </div>
                  <Tag color="blue">{getAgentTypeLabel(selectedAgent.type)}</Tag>
                </div>
              }
              extra={
                <Button
                  type="default"
                  size="small"
                  onClick={() => {
                    setSelectedAgent(null);
                    setConversations([]);
                  }}
                >
                  Schließen
                </Button>
              }
              loading={loading}
            >
              <Tabs activeKey={activeTab} onChange={setActiveTab}>
                <TabPane tab="Übersicht" key="1">
                  <div className="mb-4">
                    <Title level={4}>Details</Title>
                    <Divider />
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <Text strong>ID:</Text> {selectedAgent.id}
                      </div>
                      <div>
                        <Text strong>Status:</Text> {selectedAgent.status}
                      </div>
                      <div>
                        <Text strong>Typ:</Text> {getAgentTypeLabel(selectedAgent.type)}
                      </div>
                      <div>
                        <Text strong>Modell:</Text> {getModelLabel(selectedAgent.model)}
                      </div>
                      <div className="col-span-2">
                        <Text strong>Beschreibung:</Text> {selectedAgent.description}
                      </div>
                    </div>
                  </div>

                  <div className="mb-4">
                    <Title level={4}>Fähigkeiten</Title>
                    <Divider />
                    <div className="grid grid-cols-2 gap-2">
                      {selectedAgent.capabilities && selectedAgent.capabilities.map((capability, index) => (
                        <div key={index}>
                          <Tag color="blue">{capability}</Tag>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="mb-4">
                    <Title level={4}>Aktuelle Tasks</Title>
                    <Divider />
                    {selectedAgent.tasks && selectedAgent.tasks.length > 0 ? (
                      <List
                        dataSource={selectedAgent.tasks}
                        renderItem={task => (
                          <List.Item
                            key={task.id}
                            actions={[
                              <Button
                                key="view"
                                type="link"
                                onClick={() => handleSelectTask(task.id)}
                              >
                                Details
                              </Button>
                            ]}
                          >
                            <List.Item.Meta
                              title={
                                <div className="flex items-center">
                                  <span>{task.title}</span>
                                  <Badge status={taskStatusColors[task.status]} className="ml-2" />
                                </div>
                              }
                              description={
                                <div>
                                  <Tag color={getPriorityColor(task.priority)}>{getPriorityLabel(task.priority)}</Tag>
                                  <div className="text-xs text-gray-500 mt-1">
                                    Erstellt: {new Date(task.created_at).toLocaleString()}
                                  </div>
                                </div>
                              }
                            />
                          </List.Item>
                        )}
                      />
                    ) : (
                      <Text type="secondary">Keine aktiven Tasks</Text>
                    )}
                  </div>
                </TabPane>

                <TabPane tab="Konversation" key="2">
                  <div className="conversation-container mb-4" style={{ height: '400px', overflowY: 'auto', border: '1px solid #f0f0f0', borderRadius: '4px', padding: '16px' }}>
                    {conversations.length > 0 ? (
                      <Timeline>
                        {conversations.map((message, index) => (
                          <Timeline.Item
                            key={index}
                            color={message.sender === 'user' ? 'blue' : 'green'}
                          >
                            <div className="mb-2">
                              <Text strong>{message.sender === 'user' ? 'Sie' : selectedAgent.name}</Text>
                              <Text type="secondary" className="ml-2 text-xs">
                                {new Date(message.timestamp).toLocaleString()}
                              </Text>
                            </div>
                            <div className="bg-gray-50 p-2 rounded">
                              <Paragraph>{message.content}</Paragraph>
                            </div>
                          </Timeline.Item>
                        ))}
                      </Timeline>
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        <div className="mb-2">Keine Konversation vorhanden</div>
                        <div>Starten Sie eine Konversation mit dem Agenten</div>
                      </div>
                    )}
                  </div>

                  <div className="flex">
                    <TextArea
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      placeholder="Nachricht eingeben..."
                      autoSize={{ minRows: 2, maxRows: 6 }}
                      className="flex-grow mr-2"
                      onPressEnter={(e) => {
                        if (!e.shiftKey) {
                          e.preventDefault();
                          handleSendMessage();
                        }
                      }}
                    />
                    <Button
                      type="primary"
                      icon={<SendOutlined />}
                      onClick={handleSendMessage}
                      loading={loading}
                    >
                      Senden
                    </Button>
                  </div>
                </TabPane>

                <TabPane tab="Einstellungen" key="3">
                  <div className="mb-4">
                    <Title level={4}>Modell-Einstellungen</Title>
                    <Divider />
                    <div className="mb-4">
                      <Text strong>Aktuelles Modell:</Text> {getModelLabel(selectedAgent.model)}
                    </div>
                    <div className="mb-4">
                      <Text strong>Modell ändern:</Text>
                      <Select
                        value={selectedAgent.model}
                        style={{ width: '100%', marginTop: '8px' }}
                        onChange={(value) => {
                          const updatedAgent = { ...selectedAgent, model: value };
                          handleUpdateAgent(selectedAgent.id, updatedAgent);
                        }}
                      >
                        {modelOptions.map(model => (
                          <Option key={model.value} value={model.value}>{model.label}</Option>
                        ))}
                      </Select>
                    </div>
                  </div>

                  <div className="mb-4">
                    <Title level={4}>Parameter</Title>
                    <Divider />
                    <Collapse>
                      <Panel header="Allgemeine Parameter" key="1">
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <Text strong>Temperatur:</Text>
                            <Input
                              type="number"
                              min={0}
                              max={1}
                              step={0.1}
                              value={selectedAgent.parameters?.temperature || 0.7}
                              onChange={(e) => {
                                const updatedAgent = {
                                  ...selectedAgent,
                                  parameters: {
                                    ...selectedAgent.parameters,
                                    temperature: parseFloat(e.target.value)
                                  }
                                };
                                handleUpdateAgent(selectedAgent.id, updatedAgent);
                              }}
                              style={{ marginTop: '8px' }}
                            />
                          </div>
                          <div>
                            <Text strong>Max Tokens:</Text>
                            <Input
                              type="number"
                              min={1}
                              max={8192}
                              value={selectedAgent.parameters?.max_tokens || 1024}
                              onChange={(e) => {
                                const updatedAgent = {
                                  ...selectedAgent,
                                  parameters: {
                                    ...selectedAgent.parameters,
                                    max_tokens: parseInt(e.target.value)
                                  }
                                };
                                handleUpdateAgent(selectedAgent.id, updatedAgent);
                              }}
                              style={{ marginTop: '8px' }}
                            />
                          </div>
                        </div>
                      </Panel>
                      <Panel header="Erweiterte Parameter" key="2">
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <Text strong>Top P:</Text>
                            <Input
                              type="number"
                              min={0}
                              max={1}
                              step={0.1}
                              value={selectedAgent.parameters?.top_p || 0.9}
                              onChange={(e) => {
                                const updatedAgent = {
                                  ...selectedAgent,
                                  parameters: {
                                    ...selectedAgent.parameters,
                                    top_p: parseFloat(e.target.value)
                                  }
                                };
                                handleUpdateAgent(selectedAgent.id, updatedAgent);
                              }}
                              style={{ marginTop: '8px' }}
                            />
                          </div>
                          <div>
                            <Text strong>Frequency Penalty:</Text>
                            <Input
                              type="number"
                              min={0}
                              max={2}
                              step={0.1}
                              value={selectedAgent.parameters?.frequency_penalty || 0}
                              onChange={(e) => {
                                const updatedAgent = {
                                  ...selectedAgent,
                                  parameters: {
                                    ...selectedAgent.parameters,
                                    frequency_penalty: parseFloat(e.target.value)
                                  }
                                };
                                handleUpdateAgent(selectedAgent.id, updatedAgent);
                              }}
                              style={{ marginTop: '8px' }}
                            />
                          </div>
                          <div>
                            <Text strong>Presence Penalty:</Text>
                            <Input
                              type="number"
                              min={0}
                              max={2}
                              step={0.1}
                              value={selectedAgent.parameters?.presence_penalty || 0}
                              onChange={(e) => {
                                const updatedAgent = {
                                  ...selectedAgent,
                                  parameters: {
                                    ...selectedAgent.parameters,
                                    presence_penalty: parseFloat(e.target.value)
                                  }
                                };
                                handleUpdateAgent(selectedAgent.id, updatedAgent);
                              }}
                              style={{ marginTop: '8px' }}
                            />
                          </div>
                        </div>
                      </Panel>
                    </Collapse>
                  </div>
                </TabPane>
              </Tabs>
            </Card>
          ) : selectedTask ? (
            <Card
              title={
                <div className="flex justify-between items-center">
                  <span>{selectedTask.title}</span>
                  <Badge status={taskStatusColors[selectedTask.status]} text={selectedTask.status} />
                </div>
              }
              extra={
                <Button
                  type="default"
                  size="small"
                  onClick={() => setSelectedTask(null)}
                >
                  Schließen
                </Button>
              }
              loading={taskLoading}
            >
              <div className="mb-4">
                <Title level={4}>Details</Title>
                <Divider />
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <Text strong>ID:</Text> {selectedTask.id}
                  </div>
                  <div>
                    <Text strong>Status:</Text> {selectedTask.status}
                  </div>
                  <div>
                    <Text strong>Priorität:</Text> <Tag color={getPriorityColor(selectedTask.priority)}>{getPriorityLabel(selectedTask.priority)}</Tag>
                  </div>
                  <div>
                    <Text strong>Agent:</Text> {selectedTask.agent_name || 'Kein Agent zugewiesen'}
                  </div>
                  <div>
                    <Text strong>Erstellt am:</Text> {new Date(selectedTask.created_at).toLocaleString()}
                  </div>
                  {selectedTask.completed_at && (
                    <div>
                      <Text strong>Abgeschlossen am:</Text> {new Date(selectedTask.completed_at).toLocaleString()}
                    </div>
                  )}
                  <div className="col-span-2">
                    <Text strong>Beschreibung:</Text> {selectedTask.description}
                  </div>
                </div>
              </div>

              {selectedTask.result && (
                <div className="mb-4">
                  <Title level={4}>Ergebnis</Title>
                  <Divider />
                  <pre className="bg-gray-100 p-4 rounded overflow-auto max-h-60">
                    {typeof selectedTask.result === 'object'
                      ? JSON.stringify(selectedTask.result, null, 2)
                      : selectedTask.result}
                  </pre>
                </div>
              )}

              {selectedTask.error && (
                <div className="mb-4">
                  <Title level={4}>Fehler</Title>
                  <Divider />
                  <div className="bg-red-50 p-4 rounded text-red-500">
                    {selectedTask.error}
                  </div>
                </div>
              )}

              <div className="mb-4">
                <Title level={4}>Verlauf</Title>
                <Divider />
                {selectedTask.history && selectedTask.history.length > 0 ? (
                  <Timeline>
                    {selectedTask.history.map((event, index) => (
                      <Timeline.Item
                        key={index}
                        color={
                          event.type === 'created' ? 'blue' :
                          event.type === 'started' ? 'green' :
                          event.type === 'completed' ? 'green' :
                          event.type === 'failed' ? 'red' :
                          event.type === 'cancelled' ? 'gray' :
                          'blue'
                        }
                      >
                        <div className="mb-1">
                          <Text strong>{event.type}</Text>
                          <Text type="secondary" className="ml-2 text-xs">
                            {new Date(event.timestamp).toLocaleString()}
                          </Text>
                        </div>
                        {event.details && (
                          <div className="text-sm">
                            {typeof event.details === 'object'
                              ? JSON.stringify(event.details)
                              : event.details}
                          </div>
                        )}
                      </Timeline.Item>
                    ))}
                  </Timeline>
                ) : (
                  <Text type="secondary">Kein Verlauf verfügbar</Text>
                )}
              </div>
            </Card>
          ) : (
            <Card title="Agent-Details" loading={loading}>
              <div className="text-center py-8 text-gray-500">
                <div className="mb-2">Kein Agent ausgewählt</div>
                <div>Wählen Sie einen Agenten aus der Liste aus, um Details anzuzeigen</div>
              </div>
            </Card>
          )}
        </div>
      </div>

      {/* Agent erstellen Modal */}
      <Modal
        title="Agent erstellen"
        visible={createModalVisible}
        onOk={handleCreateAgent}
        onCancel={() => {
          setCreateModalVisible(false);
          setNewAgent({
            name: '',
            description: '',
            type: 'rfi_analyst',
            model: 'default',
            parameters: {}
          });
        }}
        confirmLoading={loading}
      >
        <div className="mb-4">
          <label className="block mb-2">Name</label>
          <Input
            placeholder="Name"
            value={newAgent.name}
            onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
          />
        </div>

        <div className="mb-4">
          <label className="block mb-2">Beschreibung</label>
          <Input.TextArea
            placeholder="Beschreibung"
            value={newAgent.description}
            onChange={(e) => setNewAgent({ ...newAgent, description: e.target.value })}
            rows={3}
          />
        </div>

        <div className="mb-4">
          <label className="block mb-2">Typ</label>
          <Select
            value={newAgent.type}
            onChange={(value) => setNewAgent({ ...newAgent, type: value })}
            style={{ width: '100%' }}
          >
            {agentTypes.map(type => (
              <Option key={type.value} value={type.value}>{type.label}</Option>
            ))}
          </Select>
        </div>

        <div className="mb-4">
          <label className="block mb-2">Modell</label>
          <Select
            value={newAgent.model}
            onChange={(value) => setNewAgent({ ...newAgent, model: value })}
            style={{ width: '100%' }}
          >
            {modelOptions.map(model => (
              <Option key={model.value} value={model.value}>{model.label}</Option>
            ))}
          </Select>
        </div>
      </Modal>

      {/* Task erstellen Modal */}
      <Modal
        title="Task erstellen"
        visible={taskModalVisible}
        onOk={handleCreateTask}
        onCancel={() => {
          setTaskModalVisible(false);
          setNewTask({
            title: '',
            description: '',
            agent_id: '',
            priority: 'medium',
            data: {}
          });
        }}
        confirmLoading={taskLoading}
      >
        <div className="mb-4">
          <label className="block mb-2">Titel</label>
          <Input
            placeholder="Titel"
            value={newTask.title}
            onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
          />
        </div>

        <div className="mb-4">
          <label className="block mb-2">Beschreibung</label>
          <Input.TextArea
            placeholder="Beschreibung"
            value={newTask.description}
            onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
            rows={3}
          />
        </div>

        <div className="mb-4">
          <label className="block mb-2">Agent</label>
          <Select
            value={newTask.agent_id}
            onChange={(value) => setNewTask({ ...newTask, agent_id: value })}
            style={{ width: '100%' }}
          >
            <Option value="">Keinen Agent auswählen</Option>
            {agents.map(agent => (
              <Option key={agent.id} value={agent.id}>{agent.name}</Option>
            ))}
          </Select>
        </div>

        <div className="mb-4">
          <label className="block mb-2">Priorität</label>
          <Select
            value={newTask.priority}
            onChange={(value) => setNewTask({ ...newTask, priority: value })}
            style={{ width: '100%' }}
          >
            {priorityOptions.map(priority => (
              <Option key={priority.value} value={priority.value}>{priority.label}</Option>
            ))}
          </Select>
        </div>

        <div className="mb-4">
          <label className="block mb-2">Daten (JSON)</label>
          <Input.TextArea
            placeholder="Daten als JSON"
            value={JSON.stringify(newTask.data, null, 2)}
            onChange={(e) => {
              try {
                setNewTask({ ...newTask, data: JSON.parse(e.target.value) });
              } catch (error) {
                // Ignoriere Parsing-Fehler während der Eingabe
              }
            }}
            rows={4}
          />
        </div>
      </Modal>
    </div>
  );
};

export default AgentCrew;

