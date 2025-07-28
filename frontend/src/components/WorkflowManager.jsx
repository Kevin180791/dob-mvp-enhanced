import React, { useState, useEffect } from 'react';
import { Card, Tabs, List, Avatar, Badge, Button, Modal, Input, Select, Tag, Spin, Typography, Divider, Timeline, Collapse, message, Steps, Drawer, Form, Switch, Space, Tooltip } from 'antd';
import { UserOutlined, TeamOutlined, SettingOutlined, PlusOutlined, EditOutlined, DeleteOutlined, SendOutlined, SyncOutlined, CheckCircleOutlined, CloseCircleOutlined, QuestionCircleOutlined, NodeIndexOutlined, BranchesOutlined, ApiOutlined, RobotOutlined, FileOutlined, UserSwitchOutlined } from '@ant-design/icons';
import { workflowService } from '../services/workflowService';
import ReactFlow, { Controls, Background, MiniMap } from 'react-flow-renderer';

const { TabPane } = Tabs;
const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Option } = Select;
const { Panel } = Collapse;
const { Step } = Steps;

const WorkflowManager = () => {
  const [workflows, setWorkflows] = useState([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [instances, setInstances] = useState([]);
  const [selectedInstance, setSelectedInstance] = useState(null);
  const [loading, setLoading] = useState(false);
  const [instanceLoading, setInstanceLoading] = useState(false);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [editorDrawerVisible, setEditorDrawerVisible] = useState(false);
  const [newWorkflow, setNewWorkflow] = useState({
    name: '',
    description: '',
    type: 'rfi_workflow',
    steps: [],
    settings: {
      auto_assign: true,
      notifications: true,
      approval_required: false
    }
  });
  const [activeTab, setActiveTab] = useState('1');
  const [flowElements, setFlowElements] = useState([]);

  const workflowTypes = [
    { value: 'rfi_workflow', label: 'RFI-Workflow' },
    { value: 'document_review', label: 'Dokumentenprüfung' },
    { value: 'approval_workflow', label: 'Freigabe-Workflow' },
    { value: 'coordination_workflow', label: 'Koordinations-Workflow' },
    { value: 'custom_workflow', label: 'Benutzerdefinierter Workflow' }
  ];

  const stepTypes = [
    { value: 'agent_task', label: 'Agent-Aufgabe', icon: <RobotOutlined /> },
    { value: 'user_task', label: 'Benutzer-Aufgabe', icon: <UserOutlined /> },
    { value: 'approval', label: 'Freigabe', icon: <CheckCircleOutlined /> },
    { value: 'condition', label: 'Bedingung', icon: <BranchesOutlined /> },
    { value: 'document_processing', label: 'Dokumentenverarbeitung', icon: <FileOutlined /> },
    { value: 'notification', label: 'Benachrichtigung', icon: <SendOutlined /> },
    { value: 'integration', label: 'Integration', icon: <ApiOutlined /> },
    { value: 'assignment', label: 'Zuweisung', icon: <UserSwitchOutlined /> }
  ];

  const statusColors = {
    active: 'green',
    inactive: 'default',
    draft: 'orange',
    archived: 'default'
  };

  const instanceStatusColors = {
    running: 'processing',
    completed: 'success',
    failed: 'error',
    waiting: 'warning',
    cancelled: 'default'
  };

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      const data = await workflowService.getWorkflows();
      setWorkflows(data);
      setLoading(false);
    } catch (error) {
      message.error('Fehler beim Laden der Workflows: ' + error.message);
      setLoading(false);
    }
  };

  const fetchInstances = async (workflowId) => {
    try {
      setInstanceLoading(true);
      const data = await workflowService.getWorkflowInstances(workflowId);
      setInstances(data);
      setInstanceLoading(false);
    } catch (error) {
      message.error('Fehler beim Laden der Workflow-Instanzen: ' + error.message);
      setInstanceLoading(false);
    }
  };

  const handleCreateWorkflow = async () => {
    try {
      setLoading(true);
      await workflowService.createWorkflow(newWorkflow);
      message.success('Workflow erfolgreich erstellt');
      setCreateModalVisible(false);
      setNewWorkflow({
        name: '',
        description: '',
        type: 'rfi_workflow',
        steps: [],
        settings: {
          auto_assign: true,
          notifications: true,
          approval_required: false
        }
      });
      fetchWorkflows();
    } catch (error) {
      message.error('Fehler beim Erstellen des Workflows: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateWorkflow = async (workflowId, data) => {
    try {
      setLoading(true);
      await workflowService.updateWorkflow(workflowId, data);
      message.success('Workflow erfolgreich aktualisiert');
      fetchWorkflows();
      if (selectedWorkflow && selectedWorkflow.id === workflowId) {
        const workflow = await workflowService.getWorkflow(workflowId);
        setSelectedWorkflow(workflow);
      }
    } catch (error) {
      message.error('Fehler beim Aktualisieren des Workflows: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteWorkflow = async (workflowId) => {
    try {
      setLoading(true);
      await workflowService.deleteWorkflow(workflowId);
      message.success('Workflow erfolgreich gelöscht');
      fetchWorkflows();
      if (selectedWorkflow && selectedWorkflow.id === workflowId) {
        setSelectedWorkflow(null);
      }
    } catch (error) {
      message.error('Fehler beim Löschen des Workflows: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectWorkflow = async (workflowId) => {
    try {
      setLoading(true);
      const workflow = await workflowService.getWorkflow(workflowId);
      setSelectedWorkflow(workflow);
      setActiveTab('1');
      
      // Lade die Instanzen des Workflows
      fetchInstances(workflowId);
      
      // Erstelle Flow-Elemente für die Visualisierung
      createFlowElements(workflow);
      
      setLoading(false);
    } catch (error) {
      message.error('Fehler beim Laden des Workflows: ' + error.message);
      setLoading(false);
    }
  };

  const handleSelectInstance = async (instanceId) => {
    try {
      setInstanceLoading(true);
      const instance = await workflowService.getWorkflowInstance(instanceId);
      setSelectedInstance(instance);
      setInstanceLoading(false);
    } catch (error) {
      message.error('Fehler beim Laden der Workflow-Instanz: ' + error.message);
      setInstanceLoading(false);
    }
  };

  const handleStartWorkflow = async (workflowId, data = {}) => {
    try {
      setLoading(true);
      const instance = await workflowService.startWorkflow(workflowId, data);
      message.success('Workflow erfolgreich gestartet');
      fetchInstances(workflowId);
      setLoading(false);
      return instance;
    } catch (error) {
      message.error('Fehler beim Starten des Workflows: ' + error.message);
      setLoading(false);
      throw error;
    }
  };

  const handleCancelInstance = async (instanceId) => {
    try {
      setInstanceLoading(true);
      await workflowService.cancelWorkflowInstance(instanceId);
      message.success('Workflow-Instanz erfolgreich abgebrochen');
      if (selectedWorkflow) {
        fetchInstances(selectedWorkflow.id);
      }
      if (selectedInstance && selectedInstance.id === instanceId) {
        const instance = await workflowService.getWorkflowInstance(instanceId);
        setSelectedInstance(instance);
      }
      setInstanceLoading(false);
    } catch (error) {
      message.error('Fehler beim Abbrechen der Workflow-Instanz: ' + error.message);
      setInstanceLoading(false);
    }
  };

  const handleCompleteTask = async (instanceId, taskId, data = {}) => {
    try {
      setInstanceLoading(true);
      await workflowService.completeWorkflowTask(instanceId, taskId, data);
      message.success('Aufgabe erfolgreich abgeschlossen');
      if (selectedInstance && selectedInstance.id === instanceId) {
        const instance = await workflowService.getWorkflowInstance(instanceId);
        setSelectedInstance(instance);
      }
      setInstanceLoading(false);
    } catch (error) {
      message.error('Fehler beim Abschließen der Aufgabe: ' + error.message);
      setInstanceLoading(false);
    }
  };

  const createFlowElements = (workflow) => {
    if (!workflow || !workflow.steps || workflow.steps.length === 0) {
      setFlowElements([]);
      return;
    }

    const nodes = workflow.steps.map((step, index) => {
      const stepType = stepTypes.find(t => t.value === step.type) || { label: step.type, icon: <NodeIndexOutlined /> };
      
      return {
        id: step.id.toString(),
        type: step.type === 'condition' ? 'special' : 'default',
        data: { 
          label: (
            <div className="flex items-center">
              <div className="mr-2">{stepType.icon}</div>
              <div>
                <div>{step.name}</div>
                <div className="text-xs text-gray-500">{stepType.label}</div>
              </div>
            </div>
          )
        },
        position: { x: 250, y: index * 100 }
      };
    });

    const edges = [];
    workflow.steps.forEach((step, index) => {
      if (index < workflow.steps.length - 1) {
        if (step.type === 'condition') {
          // Für Bedingungen zwei Kanten erstellen (true/false)
          edges.push({
            id: `e${step.id}-true`,
            source: step.id.toString(),
            target: step.transitions?.true || workflow.steps[index + 1].id.toString(),
            label: 'Ja',
            type: 'smoothstep',
            animated: true,
            style: { stroke: '#52c41a' }
          });
          
          if (step.transitions?.false) {
            edges.push({
              id: `e${step.id}-false`,
              source: step.id.toString(),
              target: step.transitions.false,
              label: 'Nein',
              type: 'smoothstep',
              animated: true,
              style: { stroke: '#f5222d' }
            });
          }
        } else {
          // Normale Kante für sequentielle Schritte
          edges.push({
            id: `e${step.id}-${workflow.steps[index + 1].id}`,
            source: step.id.toString(),
            target: workflow.steps[index + 1].id.toString(),
            type: 'smoothstep',
            animated: true
          });
        }
      }
    });

    setFlowElements([...nodes, ...edges]);
  };

  const getWorkflowTypeLabel = (type) => {
    const workflowType = workflowTypes.find(t => t.value === type);
    return workflowType ? workflowType.label : type;
  };

  const getStepTypeLabel = (type) => {
    const stepType = stepTypes.find(t => t.value === type);
    return stepType ? stepType.label : type;
  };

  const getStepTypeIcon = (type) => {
    const stepType = stepTypes.find(t => t.value === type);
    return stepType ? stepType.icon : <NodeIndexOutlined />;
  };

  return (
    <div className="workflow-manager p-4">
      <div className="flex justify-between items-center mb-4">
        <Title level={3}>Kollaborative Workflow-Engine</Title>
        <div className="space-x-2">
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setCreateModalVisible(true)}
          >
            Workflow erstellen
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-1">
          <Card title="Workflows" loading={loading}>
            <List
              dataSource={workflows}
              renderItem={workflow => (
                <List.Item
                  key={workflow.id}
                  className={`workflow-item ${selectedWorkflow?.id === workflow.id ? 'selected' : ''}`}
                  onClick={() => handleSelectWorkflow(workflow.id)}
                  style={{ cursor: 'pointer', padding: '8px', borderRadius: '4px', backgroundColor: selectedWorkflow?.id === workflow.id ? '#f0f5ff' : 'transparent' }}
                  actions={[
                    <Button
                      key="edit"
                      type="text"
                      icon={<EditOutlined />}
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedWorkflow(workflow);
                        setEditorDrawerVisible(true);
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
                          title: 'Workflow löschen',
                          content: 'Möchten Sie diesen Workflow wirklich löschen?',
                          okText: 'Ja',
                          okType: 'danger',
                          cancelText: 'Nein',
                          onOk: () => handleDeleteWorkflow(workflow.id)
                        });
                      }}
                    />
                  ]}
                >
                  <List.Item.Meta
                    avatar={<Avatar icon={<NodeIndexOutlined />} style={{ backgroundColor: '#1890ff' }} />}
                    title={
                      <div className="flex items-center">
                        <span>{workflow.name}</span>
                        <Tag color={statusColors[workflow.status]} className="ml-2">{workflow.status}</Tag>
                      </div>
                    }
                    description={
                      <div>
                        <div>{getWorkflowTypeLabel(workflow.type)}</div>
                        <div className="text-xs text-gray-500">Schritte: {workflow.steps?.length || 0}</div>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>

          <Card title="Workflow-Instanzen" className="mt-4" loading={instanceLoading}>
            <List
              dataSource={instances}
              renderItem={instance => (
                <List.Item
                  key={instance.id}
                  className={`instance-item ${selectedInstance?.id === instance.id ? 'selected' : ''}`}
                  onClick={() => handleSelectInstance(instance.id)}
                  style={{ cursor: 'pointer', padding: '8px', borderRadius: '4px', backgroundColor: selectedInstance?.id === instance.id ? '#f0f5ff' : 'transparent' }}
                  actions={[
                    instance.status === 'running' || instance.status === 'waiting' ? (
                      <Button
                        key="cancel"
                        type="text"
                        danger
                        icon={<CloseCircleOutlined />}
                        onClick={(e) => {
                          e.stopPropagation();
                          Modal.confirm({
                            title: 'Workflow-Instanz abbrechen',
                            content: 'Möchten Sie diese Workflow-Instanz wirklich abbrechen?',
                            okText: 'Ja',
                            okType: 'danger',
                            cancelText: 'Nein',
                            onOk: () => handleCancelInstance(instance.id)
                          });
                        }}
                      />
                    ) : null
                  ]}
                >
                  <List.Item.Meta
                    title={
                      <div className="flex items-center">
                        <span>#{instance.id}</span>
                        <Badge status={instanceStatusColors[instance.status]} className="ml-2" />
                      </div>
                    }
                    description={
                      <div>
                        <div className="text-xs text-gray-500">
                          Gestartet: {new Date(instance.created_at).toLocaleString()}
                        </div>
                        <div className="text-xs text-gray-500">
                          Aktueller Schritt: {instance.current_step?.name || 'Nicht gestartet'}
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
          {selectedWorkflow ? (
            <Card
              title={
                <div className="flex justify-between items-center">
                  <div className="flex items-center">
                    <Avatar icon={<NodeIndexOutlined />} style={{ backgroundColor: '#1890ff' }} />
                    <span className="ml-2">{selectedWorkflow.name}</span>
                    <Tag color={statusColors[selectedWorkflow.status]} className="ml-2">{selectedWorkflow.status}</Tag>
                  </div>
                  <Tag color="blue">{getWorkflowTypeLabel(selectedWorkflow.type)}</Tag>
                </div>
              }
              extra={
                <Space>
                  <Button
                    type="primary"
                    onClick={() => {
                      Modal.confirm({
                        title: 'Workflow starten',
                        content: 'Möchten Sie diesen Workflow starten?',
                        okText: 'Ja',
                        cancelText: 'Nein',
                        onOk: () => handleStartWorkflow(selectedWorkflow.id)
                      });
                    }}
                    disabled={selectedWorkflow.status !== 'active'}
                  >
                    Starten
                  </Button>
                  <Button
                    type="default"
                    size="small"
                    onClick={() => {
                      setSelectedWorkflow(null);
                      setInstances([]);
                    }}
                  >
                    Schließen
                  </Button>
                </Space>
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
                        <Text strong>ID:</Text> {selectedWorkflow.id}
                      </div>
                      <div>
                        <Text strong>Status:</Text> {selectedWorkflow.status}
                      </div>
                      <div>
                        <Text strong>Typ:</Text> {getWorkflowTypeLabel(selectedWorkflow.type)}
                      </div>
                      <div>
                        <Text strong>Version:</Text> {selectedWorkflow.version || '1.0'}
                      </div>
                      <div className="col-span-2">
                        <Text strong>Beschreibung:</Text> {selectedWorkflow.description}
                      </div>
                    </div>
                  </div>

                  <div className="mb-4">
                    <Title level={4}>Schritte</Title>
                    <Divider />
                    {selectedWorkflow.steps && selectedWorkflow.steps.length > 0 ? (
                      <Steps direction="vertical" current={-1}>
                        {selectedWorkflow.steps.map((step, index) => (
                          <Step
                            key={step.id}
                            title={step.name}
                            description={
                              <div>
                                <div className="flex items-center">
                                  {getStepTypeIcon(step.type)}
                                  <span className="ml-2">{getStepTypeLabel(step.type)}</span>
                                </div>
                                {step.description && <div className="text-sm mt-1">{step.description}</div>}
                              </div>
                            }
                            icon={getStepTypeIcon(step.type)}
                          />
                        ))}
                      </Steps>
                    ) : (
                      <Text type="secondary">Keine Schritte definiert</Text>
                    )}
                  </div>

                  <div className="mb-4">
                    <Title level={4}>Einstellungen</Title>
                    <Divider />
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <Text strong>Automatische Zuweisung:</Text> {selectedWorkflow.settings?.auto_assign ? 'Ja' : 'Nein'}
                      </div>
                      <div>
                        <Text strong>Benachrichtigungen:</Text> {selectedWorkflow.settings?.notifications ? 'Ja' : 'Nein'}
                      </div>
                      <div>
                        <Text strong>Freigabe erforderlich:</Text> {selectedWorkflow.settings?.approval_required ? 'Ja' : 'Nein'}
                      </div>
                    </div>
                  </div>
                </TabPane>

                <TabPane tab="Visualisierung" key="2">
                  <div style={{ height: '500px', border: '1px solid #f0f0f0', borderRadius: '4px' }}>
                    <ReactFlow
                      elements={flowElements}
                      snapToGrid={true}
                      snapGrid={[15, 15]}
                      defaultZoom={1.5}
                      minZoom={0.5}
                      maxZoom={2}
                    >
                      <MiniMap
                        nodeStrokeColor={(n) => {
                          if (n.type === 'special') return '#ff0072';
                          return '#0041d0';
                        }}
                        nodeColor={(n) => {
                          if (n.type === 'special') return '#ff0072';
                          return '#0041d0';
                        }}
                      />
                      <Controls />
                      <Background color="#aaa" gap={16} />
                    </ReactFlow>
                  </div>
                </TabPane>

                <TabPane tab="Instanzen" key="3">
                  <div className="mb-4">
                    <Title level={4}>Aktive Instanzen</Title>
                    <Divider />
                    {instances.filter(i => i.status === 'running' || i.status === 'waiting').length > 0 ? (
                      <List
                        dataSource={instances.filter(i => i.status === 'running' || i.status === 'waiting')}
                        renderItem={instance => (
                          <List.Item
                            key={instance.id}
                            actions={[
                              <Button
                                key="view"
                                type="link"
                                onClick={() => handleSelectInstance(instance.id)}
                              >
                                Details
                              </Button>,
                              <Button
                                key="cancel"
                                type="link"
                                danger
                                onClick={() => {
                                  Modal.confirm({
                                    title: 'Workflow-Instanz abbrechen',
                                    content: 'Möchten Sie diese Workflow-Instanz wirklich abbrechen?',
                                    okText: 'Ja',
                                    okType: 'danger',
                                    cancelText: 'Nein',
                                    onOk: () => handleCancelInstance(instance.id)
                                  });
                                }}
                              >
                                Abbrechen
                              </Button>
                            ]}
                          >
                            <List.Item.Meta
                              title={
                                <div className="flex items-center">
                                  <span>#{instance.id}</span>
                                  <Badge status={instanceStatusColors[instance.status]} className="ml-2" />
                                </div>
                              }
                              description={
                                <div>
                                  <div className="text-xs text-gray-500">
                                    Gestartet: {new Date(instance.created_at).toLocaleString()}
                                  </div>
                                  <div className="text-xs text-gray-500">
                                    Aktueller Schritt: {instance.current_step?.name || 'Nicht gestartet'}
                                  </div>
                                </div>
                              }
                            />
                          </List.Item>
                        )}
                      />
                    ) : (
                      <Text type="secondary">Keine aktiven Instanzen</Text>
                    )}
                  </div>

                  <div className="mb-4">
                    <Title level={4}>Abgeschlossene Instanzen</Title>
                    <Divider />
                    {instances.filter(i => i.status === 'completed').length > 0 ? (
                      <List
                        dataSource={instances.filter(i => i.status === 'completed')}
                        renderItem={instance => (
                          <List.Item
                            key={instance.id}
                            actions={[
                              <Button
                                key="view"
                                type="link"
                                onClick={() => handleSelectInstance(instance.id)}
                              >
                                Details
                              </Button>
                            ]}
                          >
                            <List.Item.Meta
                              title={
                                <div className="flex items-center">
                                  <span>#{instance.id}</span>
                                  <Badge status={instanceStatusColors[instance.status]} className="ml-2" />
                                </div>
                              }
                              description={
                                <div>
                                  <div className="text-xs text-gray-500">
                                    Gestartet: {new Date(instance.created_at).toLocaleString()}
                                  </div>
                                  <div className="text-xs text-gray-500">
                                    Abgeschlossen: {new Date(instance.completed_at).toLocaleString()}
                                  </div>
                                </div>
                              }
                            />
                          </List.Item>
                        )}
                      />
                    ) : (
                      <Text type="secondary">Keine abgeschlossenen Instanzen</Text>
                    )}
                  </div>
                </TabPane>

                <TabPane tab="Einstellungen" key="4">
                  <div className="mb-4">
                    <Title level={4}>Workflow-Einstellungen</Title>
                    <Divider />
                    <Form
                      layout="vertical"
                      initialValues={{
                        name: selectedWorkflow.name,
                        description: selectedWorkflow.description,
                        status: selectedWorkflow.status,
                        auto_assign: selectedWorkflow.settings?.auto_assign || false,
                        notifications: selectedWorkflow.settings?.notifications || false,
                        approval_required: selectedWorkflow.settings?.approval_required || false
                      }}
                      onFinish={(values) => {
                        const updatedWorkflow = {
                          ...selectedWorkflow,
                          name: values.name,
                          description: values.description,
                          status: values.status,
                          settings: {
                            ...selectedWorkflow.settings,
                            auto_assign: values.auto_assign,
                            notifications: values.notifications,
                            approval_required: values.approval_required
                          }
                        };
                        handleUpdateWorkflow(selectedWorkflow.id, updatedWorkflow);
                      }}
                    >
                      <Form.Item
                        label="Name"
                        name="name"
                        rules={[{ required: true, message: 'Bitte geben Sie einen Namen ein' }]}
                      >
                        <Input />
                      </Form.Item>

                      <Form.Item
                        label="Beschreibung"
                        name="description"
                      >
                        <TextArea rows={3} />
                      </Form.Item>

                      <Form.Item
                        label="Status"
                        name="status"
                      >
                        <Select>
                          <Option value="active">Aktiv</Option>
                          <Option value="inactive">Inaktiv</Option>
                          <Option value="draft">Entwurf</Option>
                          <Option value="archived">Archiviert</Option>
                        </Select>
                      </Form.Item>

                      <Form.Item
                        label="Automatische Zuweisung"
                        name="auto_assign"
                        valuePropName="checked"
                      >
                        <Switch />
                      </Form.Item>

                      <Form.Item
                        label="Benachrichtigungen"
                        name="notifications"
                        valuePropName="checked"
                      >
                        <Switch />
                      </Form.Item>

                      <Form.Item
                        label="Freigabe erforderlich"
                        name="approval_required"
                        valuePropName="checked"
                      >
                        <Switch />
                      </Form.Item>

                      <Form.Item>
                        <Button type="primary" htmlType="submit">
                          Speichern
                        </Button>
                      </Form.Item>
                    </Form>
                  </div>
                </TabPane>
              </Tabs>
            </Card>
          ) : selectedInstance ? (
            <Card
              title={
                <div className="flex justify-between items-center">
                  <span>Workflow-Instanz #{selectedInstance.id}</span>
                  <Badge status={instanceStatusColors[selectedInstance.status]} text={selectedInstance.status} />
                </div>
              }
              extra={
                <Button
                  type="default"
                  size="small"
                  onClick={() => setSelectedInstance(null)}
                >
                  Schließen
                </Button>
              }
              loading={instanceLoading}
            >
              <div className="mb-4">
                <Title level={4}>Details</Title>
                <Divider />
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <Text strong>ID:</Text> {selectedInstance.id}
                  </div>
                  <div>
                    <Text strong>Status:</Text> {selectedInstance.status}
                  </div>
                  <div>
                    <Text strong>Workflow:</Text> {selectedInstance.workflow_name || 'Unbekannt'}
                  </div>
                  <div>
                    <Text strong>Workflow-ID:</Text> {selectedInstance.workflow_id}
                  </div>
                  <div>
                    <Text strong>Gestartet am:</Text> {new Date(selectedInstance.created_at).toLocaleString()}
                  </div>
                  {selectedInstance.completed_at && (
                    <div>
                      <Text strong>Abgeschlossen am:</Text> {new Date(selectedInstance.completed_at).toLocaleString()}
                    </div>
                  )}
                </div>
              </div>

              <div className="mb-4">
                <Title level={4}>Aktueller Schritt</Title>
                <Divider />
                {selectedInstance.current_step ? (
                  <div>
                    <div className="mb-2">
                      <Text strong>Name:</Text> {selectedInstance.current_step.name}
                    </div>
                    <div className="mb-2">
                      <Text strong>Typ:</Text> {getStepTypeLabel(selectedInstance.current_step.type)}
                    </div>
                    {selectedInstance.current_step.description && (
                      <div className="mb-2">
                        <Text strong>Beschreibung:</Text> {selectedInstance.current_step.description}
                      </div>
                    )}
                    {selectedInstance.current_step.type === 'user_task' && selectedInstance.status === 'waiting' && (
                      <div className="mt-4">
                        <Button
                          type="primary"
                          onClick={() => {
                            Modal.confirm({
                              title: 'Aufgabe abschließen',
                              content: 'Möchten Sie diese Aufgabe als abgeschlossen markieren?',
                              okText: 'Ja',
                              cancelText: 'Nein',
                              onOk: () => handleCompleteTask(selectedInstance.id, selectedInstance.current_step.id)
                            });
                          }}
                        >
                          Aufgabe abschließen
                        </Button>
                      </div>
                    )}
                    {selectedInstance.current_step.type === 'approval' && selectedInstance.status === 'waiting' && (
                      <div className="mt-4">
                        <Space>
                          <Button
                            type="primary"
                            onClick={() => {
                              handleCompleteTask(selectedInstance.id, selectedInstance.current_step.id, { approved: true });
                            }}
                          >
                            Genehmigen
                          </Button>
                          <Button
                            danger
                            onClick={() => {
                              handleCompleteTask(selectedInstance.id, selectedInstance.current_step.id, { approved: false });
                            }}
                          >
                            Ablehnen
                          </Button>
                        </Space>
                      </div>
                    )}
                  </div>
                ) : (
                  <Text type="secondary">Kein aktiver Schritt</Text>
                )}
              </div>

              <div className="mb-4">
                <Title level={4}>Verlauf</Title>
                <Divider />
                {selectedInstance.history && selectedInstance.history.length > 0 ? (
                  <Timeline>
                    {selectedInstance.history.map((event, index) => (
                      <Timeline.Item
                        key={index}
                        color={
                          event.type === 'started' ? 'blue' :
                          event.type === 'step_completed' ? 'green' :
                          event.type === 'completed' ? 'green' :
                          event.type === 'failed' ? 'red' :
                          event.type === 'cancelled' ? 'gray' :
                          'blue'
                        }
                      >
                        <div className="mb-1">
                          <Text strong>{event.type === 'step_completed' ? `Schritt abgeschlossen: ${event.step_name}` : event.type}</Text>
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

              <div className="mb-4">
                <Title level={4}>Daten</Title>
                <Divider />
                {selectedInstance.data ? (
                  <pre className="bg-gray-100 p-4 rounded overflow-auto max-h-60">
                    {JSON.stringify(selectedInstance.data, null, 2)}
                  </pre>
                ) : (
                  <Text type="secondary">Keine Daten verfügbar</Text>
                )}
              </div>
            </Card>
          ) : (
            <Card title="Workflow-Details" loading={loading}>
              <div className="text-center py-8 text-gray-500">
                <div className="mb-2">Kein Workflow ausgewählt</div>
                <div>Wählen Sie einen Workflow aus der Liste aus, um Details anzuzeigen</div>
              </div>
            </Card>
          )}
        </div>
      </div>

      {/* Workflow erstellen Modal */}
      <Modal
        title="Workflow erstellen"
        visible={createModalVisible}
        onOk={handleCreateWorkflow}
        onCancel={() => {
          setCreateModalVisible(false);
          setNewWorkflow({
            name: '',
            description: '',
            type: 'rfi_workflow',
            steps: [],
            settings: {
              auto_assign: true,
              notifications: true,
              approval_required: false
            }
          });
        }}
        confirmLoading={loading}
        width={600}
      >
        <div className="mb-4">
          <label className="block mb-2">Name</label>
          <Input
            placeholder="Name"
            value={newWorkflow.name}
            onChange={(e) => setNewWorkflow({ ...newWorkflow, name: e.target.value })}
          />
        </div>

        <div className="mb-4">
          <label className="block mb-2">Beschreibung</label>
          <TextArea
            placeholder="Beschreibung"
            value={newWorkflow.description}
            onChange={(e) => setNewWorkflow({ ...newWorkflow, description: e.target.value })}
            rows={3}
          />
        </div>

        <div className="mb-4">
          <label className="block mb-2">Typ</label>
          <Select
            value={newWorkflow.type}
            onChange={(value) => setNewWorkflow({ ...newWorkflow, type: value })}
            style={{ width: '100%' }}
          >
            {workflowTypes.map(type => (
              <Option key={type.value} value={type.value}>{type.label}</Option>
            ))}
          </Select>
        </div>

        <div className="mb-4">
          <Collapse>
            <Panel header="Einstellungen" key="1">
              <div className="mb-2">
                <label className="flex items-center">
                  <Switch
                    checked={newWorkflow.settings.auto_assign}
                    onChange={(checked) => setNewWorkflow({
                      ...newWorkflow,
                      settings: { ...newWorkflow.settings, auto_assign: checked }
                    })}
                  />
                  <span className="ml-2">Automatische Zuweisung</span>
                </label>
              </div>

              <div className="mb-2">
                <label className="flex items-center">
                  <Switch
                    checked={newWorkflow.settings.notifications}
                    onChange={(checked) => setNewWorkflow({
                      ...newWorkflow,
                      settings: { ...newWorkflow.settings, notifications: checked }
                    })}
                  />
                  <span className="ml-2">Benachrichtigungen</span>
                </label>
              </div>

              <div className="mb-2">
                <label className="flex items-center">
                  <Switch
                    checked={newWorkflow.settings.approval_required}
                    onChange={(checked) => setNewWorkflow({
                      ...newWorkflow,
                      settings: { ...newWorkflow.settings, approval_required: checked }
                    })}
                  />
                  <span className="ml-2">Freigabe erforderlich</span>
                </label>
              </div>
            </Panel>
          </Collapse>
        </div>
      </Modal>

      {/* Workflow-Editor Drawer */}
      <Drawer
        title="Workflow-Editor"
        placement="right"
        width={800}
        onClose={() => setEditorDrawerVisible(false)}
        visible={editorDrawerVisible}
        footer={
          <div className="flex justify-end">
            <Button onClick={() => setEditorDrawerVisible(false)} style={{ marginRight: 8 }}>
              Abbrechen
            </Button>
            <Button
              type="primary"
              onClick={() => {
                if (selectedWorkflow) {
                  handleUpdateWorkflow(selectedWorkflow.id, selectedWorkflow);
                  setEditorDrawerVisible(false);
                }
              }}
            >
              Speichern
            </Button>
          </div>
        }
      >
        {selectedWorkflow && (
          <div>
            <div className="mb-4">
              <Title level={4}>Workflow bearbeiten</Title>
              <Divider />
              <Form layout="vertical">
                <Form.Item label="Name">
                  <Input
                    value={selectedWorkflow.name}
                    onChange={(e) => setSelectedWorkflow({ ...selectedWorkflow, name: e.target.value })}
                  />
                </Form.Item>

                <Form.Item label="Beschreibung">
                  <TextArea
                    value={selectedWorkflow.description}
                    onChange={(e) => setSelectedWorkflow({ ...selectedWorkflow, description: e.target.value })}
                    rows={3}
                  />
                </Form.Item>

                <Form.Item label="Status">
                  <Select
                    value={selectedWorkflow.status}
                    onChange={(value) => setSelectedWorkflow({ ...selectedWorkflow, status: value })}
                    style={{ width: '100%' }}
                  >
                    <Option value="active">Aktiv</Option>
                    <Option value="inactive">Inaktiv</Option>
                    <Option value="draft">Entwurf</Option>
                    <Option value="archived">Archiviert</Option>
                  </Select>
                </Form.Item>
              </Form>
            </div>

            <div className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <Title level={4}>Schritte</Title>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => {
                    const newStep = {
                      id: Date.now(),
                      name: 'Neuer Schritt',
                      type: 'user_task',
                      description: '',
                      config: {}
                    };
                    setSelectedWorkflow({
                      ...selectedWorkflow,
                      steps: [...(selectedWorkflow.steps || []), newStep]
                    });
                  }}
                >
                  Schritt hinzufügen
                </Button>
              </div>
              <Divider />
              {selectedWorkflow.steps && selectedWorkflow.steps.length > 0 ? (
                <List
                  dataSource={selectedWorkflow.steps}
                  renderItem={(step, index) => (
                    <List.Item
                      key={step.id}
                      actions={[
                        <Button
                          key="edit"
                          type="text"
                          icon={<EditOutlined />}
                          onClick={() => {
                            Modal.info({
                              title: 'Schritt bearbeiten',
                              width: 600,
                              content: (
                                <Form layout="vertical">
                                  <Form.Item label="Name">
                                    <Input
                                      defaultValue={step.name}
                                      onChange={(e) => {
                                        const updatedSteps = [...selectedWorkflow.steps];
                                        updatedSteps[index].name = e.target.value;
                                        setSelectedWorkflow({ ...selectedWorkflow, steps: updatedSteps });
                                      }}
                                    />
                                  </Form.Item>

                                  <Form.Item label="Typ">
                                    <Select
                                      defaultValue={step.type}
                                      onChange={(value) => {
                                        const updatedSteps = [...selectedWorkflow.steps];
                                        updatedSteps[index].type = value;
                                        setSelectedWorkflow({ ...selectedWorkflow, steps: updatedSteps });
                                      }}
                                      style={{ width: '100%' }}
                                    >
                                      {stepTypes.map(type => (
                                        <Option key={type.value} value={type.value}>{type.label}</Option>
                                      ))}
                                    </Select>
                                  </Form.Item>

                                  <Form.Item label="Beschreibung">
                                    <TextArea
                                      defaultValue={step.description}
                                      onChange={(e) => {
                                        const updatedSteps = [...selectedWorkflow.steps];
                                        updatedSteps[index].description = e.target.value;
                                        setSelectedWorkflow({ ...selectedWorkflow, steps: updatedSteps });
                                      }}
                                      rows={3}
                                    />
                                  </Form.Item>

                                  {step.type === 'condition' && (
                                    <div>
                                      <Form.Item label="True-Übergang (Schritt-ID)">
                                        <Input
                                          defaultValue={step.transitions?.true}
                                          onChange={(e) => {
                                            const updatedSteps = [...selectedWorkflow.steps];
                                            updatedSteps[index].transitions = {
                                              ...updatedSteps[index].transitions,
                                              true: e.target.value
                                            };
                                            setSelectedWorkflow({ ...selectedWorkflow, steps: updatedSteps });
                                          }}
                                        />
                                      </Form.Item>

                                      <Form.Item label="False-Übergang (Schritt-ID)">
                                        <Input
                                          defaultValue={step.transitions?.false}
                                          onChange={(e) => {
                                            const updatedSteps = [...selectedWorkflow.steps];
                                            updatedSteps[index].transitions = {
                                              ...updatedSteps[index].transitions,
                                              false: e.target.value
                                            };
                                            setSelectedWorkflow({ ...selectedWorkflow, steps: updatedSteps });
                                          }}
                                        />
                                      </Form.Item>
                                    </div>
                                  )}

                                  <Form.Item label="Konfiguration (JSON)">
                                    <TextArea
                                      defaultValue={JSON.stringify(step.config || {}, null, 2)}
                                      onChange={(e) => {
                                        try {
                                          const updatedSteps = [...selectedWorkflow.steps];
                                          updatedSteps[index].config = JSON.parse(e.target.value);
                                          setSelectedWorkflow({ ...selectedWorkflow, steps: updatedSteps });
                                        } catch (error) {
                                          // Ignoriere Parsing-Fehler während der Eingabe
                                        }
                                      }}
                                      rows={4}
                                    />
                                  </Form.Item>
                                </Form>
                              ),
                              okText: 'Schließen'
                            });
                          }}
                        />,
                        <Button
                          key="delete"
                          type="text"
                          danger
                          icon={<DeleteOutlined />}
                          onClick={() => {
                            Modal.confirm({
                              title: 'Schritt löschen',
                              content: 'Möchten Sie diesen Schritt wirklich löschen?',
                              okText: 'Ja',
                              okType: 'danger',
                              cancelText: 'Nein',
                              onOk: () => {
                                const updatedSteps = selectedWorkflow.steps.filter(s => s.id !== step.id);
                                setSelectedWorkflow({ ...selectedWorkflow, steps: updatedSteps });
                              }
                            });
                          }}
                        />
                      ]}
                    >
                      <List.Item.Meta
                        avatar={
                          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-600">
                            {index + 1}
                          </div>
                        }
                        title={
                          <div className="flex items-center">
                            <span>{step.name}</span>
                          </div>
                        }
                        description={
                          <div>
                            <div className="flex items-center">
                              {getStepTypeIcon(step.type)}
                              <span className="ml-2">{getStepTypeLabel(step.type)}</span>
                            </div>
                            {step.description && <div className="text-sm mt-1">{step.description}</div>}
                          </div>
                        }
                      />
                    </List.Item>
                  )}
                />
              ) : (
                <Text type="secondary">Keine Schritte definiert</Text>
              )}
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default WorkflowManager;

