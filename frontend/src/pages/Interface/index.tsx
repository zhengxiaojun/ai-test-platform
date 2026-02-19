import { PageContainer, ProTable, ProColumns } from '@ant-design/pro-components';
import { Button, Modal, Form, Input, Select, message, Space, Tag, Dropdown } from 'antd';
import { PlusOutlined, ApiOutlined, DeleteOutlined, EyeOutlined, ExperimentOutlined, MoreOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { useState, useEffect } from 'react';
import { interfaceAPI, testCaseAPI, Interface, TestPoint } from '@/services/api';

const { TextArea } = Input;

export default () => {
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [testPointsModalVisible, setTestPointsModalVisible] = useState(false);
  const [selectedInterface, setSelectedInterface] = useState<Interface | null>(null);
  const [testPoints, setTestPoints] = useState<TestPoint[]>([]);
  const [form] = Form.useForm();
  const [interfaceList, setInterfaceList] = useState<Interface[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchInterfaces = async () => {
    setLoading(true);
    try {
      const data: any = await interfaceAPI.list();
      setInterfaceList(data || []);
    } catch (error) {
      message.error('获取接口列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInterfaces();
  }, []);

  const handleCreate = async (values: any) => {
    try {
      if (values.params && typeof values.params === 'string') {
        try {
          values.params = JSON.parse(values.params);
        } catch (e) {
          values.params = {};
        }
      }
      if (values.response_example && typeof values.response_example === 'string') {
        try {
          values.response_example = JSON.parse(values.response_example);
        } catch (e) {
          values.response_example = {};
        }
      }

      await interfaceAPI.create(values);
      message.success('创建成功');
      setCreateModalVisible(false);
      form.resetFields();
      fetchInterfaces();
    } catch (error) {
      message.error('创建失败');
    }
  };

  const handleAnalyze = async (record: Interface) => {
    try {
      const result: any = await interfaceAPI.analyze(record.id!);
      message.success(`分析完成，生成 ${result.test_points_count} 个测试点`);
      setSelectedInterface(record);
      setTestPoints(result.test_points);
      setTestPointsModalVisible(true);
    } catch (error) {
      message.error('分析失败');
    }
  };

  const handleViewTestPoints = async (record: Interface) => {
    try {
      const result: any = await interfaceAPI.getTestPoints(record.id!);
      setSelectedInterface(record);
      setTestPoints(result || []);
      setTestPointsModalVisible(true);
      if (!result || result.length === 0) {
        message.info('该接口还没有测试点，请先进行AI分析');
      }
    } catch (error) {
      message.error('获取测试点失败');
    }
  };

  const handleGenerateTestCase = async (testPoint: TestPoint) => {
    Modal.confirm({
      title: '生成测试用例',
      content: `确定要为测试点"${testPoint.title}"生成测试用例吗？`,
      onOk: async () => {
        try {
          message.loading({ content: '正在生成测试用例...', key: 'generate', duration: 0 });
          await testCaseAPI.generate(testPoint.id!);
          message.success({ content: '测试用例生成成功！', key: 'generate' });
        } catch (error) {
          message.error({ content: '生成测试用例失败', key: 'generate' });
        }
      },
    });
  };

  const handleDelete = async (id: number) => {
    try {
      await interfaceAPI.delete(id);
      message.success('删除成功');
      fetchInterfaces();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const columns: ProColumns<Interface>[] = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 60,
      hideInSearch: true,
    },
    {
      title: '接口名称',
      dataIndex: 'name',
      width: 200,
      formItemProps: {
        label: '接口名称',
      },
    },
    {
      title: 'URL',
      dataIndex: 'url',
      ellipsis: true,
      hideInSearch: true,
    },
    {
      title: '方法',
      dataIndex: 'method',
      width: 80,
      hideInSearch: true,
      render: (method: any) => (
        <Tag color={
          method === 'GET' ? 'blue' :
          method === 'POST' ? 'green' :
          method === 'PUT' ? 'orange' :
          method === 'DELETE' ? 'red' : 'default'
        }>
          {method}
        </Tag>
      ),
      valueEnum: {
        GET: { text: 'GET', status: 'Default' },
        POST: { text: 'POST', status: 'Success' },
        PUT: { text: 'PUT', status: 'Warning' },
        DELETE: { text: 'DELETE', status: 'Error' },
      },
    },
    {
      title: '描述',
      dataIndex: 'description',
      ellipsis: true,
      width: 200,
      hideInSearch: true,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      valueType: 'dateTime',
      width: 180,
      hideInSearch: true,
    },
    {
      title: '操作',
      valueType: 'option',
      width: 200,
      fixed: 'right',
      render: (_, record) => {
        const menuItems: MenuProps['items'] = [
          {
            key: 'viewTestPoints',
            icon: <EyeOutlined />,
            label: '查看测试点',
            onClick: () => handleViewTestPoints(record),
          },
          {
            type: 'divider',
          },
          {
            key: 'delete',
            icon: <DeleteOutlined />,
            label: '删除',
            danger: true,
            onClick: () => {
              Modal.confirm({
                title: '确认删除',
                content: '确定要删除这个接口吗？',
                onOk: () => handleDelete(record.id!),
              });
            },
          },
        ];

        return (
          <Space>
            <Button
              type="primary"
              size="small"
              icon={<ApiOutlined />}
              onClick={() => handleAnalyze(record)}
            >
              AI分析
            </Button>
            <Dropdown menu={{ items: menuItems }} placement="bottomRight">
              <Button size="small" icon={<MoreOutlined />}>
                更多
              </Button>
            </Dropdown>
          </Space>
        );
      },
    },
  ];

  const testPointColumns: ProColumns<TestPoint>[] = [
    {
      title: '测试点标题',
      dataIndex: 'title',
    },
    {
      title: '描述',
      dataIndex: 'description',
      ellipsis: true,
    },
    {
      title: '分类',
      dataIndex: 'category',
      width: 120,
    },
    {
      title: '风险等级',
      dataIndex: 'risk_level',
      width: 100,
      render: (level: any) => (
        <Tag color={
          level === 'low' ? 'green' :
          level === 'medium' ? 'blue' :
          level === 'high' ? 'orange' : 'red'
        }>
          {level?.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: '操作',
      valueType: 'option',
      width: 120,
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          icon={<ExperimentOutlined />}
          onClick={() => handleGenerateTestCase(record)}
        >
          生成用例
        </Button>
      ),
    },
  ];

  return (
    <PageContainer
      title={false}
      breadcrumb={{
        items: [
          { title: '资源管理' },
          { title: '接口管理' },
        ],
      }}
      style={{ background: 'transparent' }}
    >
      <ProTable<Interface>
        columns={columns}
        dataSource={interfaceList}
        loading={loading}
        rowKey="id"
        search={{
          labelWidth: 100,
          defaultCollapsed: false,
          span: 6,
          optionRender: (searchConfig, formProps, _dom) => [
            <Button
              key="reset"
              onClick={() => {
                formProps?.form?.resetFields();
              }}
            >
              重置
            </Button>,
            <Button
              key="submit"
              type="primary"
              onClick={() => {
                formProps?.form?.submit();
              }}
            >
              查询
            </Button>,
          ],
        }}
        options={{
          reload: () => fetchInterfaces(),
          density: false,
          setting: true,
        }}
        toolBarRender={() => [
          <Button
            key="create"
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setCreateModalVisible(true)}
          >
            添加接口
          </Button>,
          <Button
            key="refresh"
            onClick={() => fetchInterfaces()}
          >
            刷新
          </Button>,
        ]}
        pagination={{
          pageSize: 10,
          showQuickJumper: true,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`,
        }}
        size="middle"
        cardProps={{
          bodyStyle: { padding: 0 },
        }}
        style={{ background: '#fff' }}
      />

      <Modal
        title="新建接口"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        width={800}
      >
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item
            name="name"
            label="接口名称"
            rules={[{ required: true, message: '请输入接口名称' }]}
          >
            <Input placeholder="例如：用户登录接口" />
          </Form.Item>
          <Form.Item
            name="url"
            label="URL"
            rules={[{ required: true, message: '请输入URL' }]}
          >
            <Input placeholder="例如：/api/v1/login" />
          </Form.Item>
          <Form.Item
            name="method"
            label="请求方法"
            rules={[{ required: true, message: '请选择请求方法' }]}
          >
            <Select>
              <Select.Option value="GET">GET</Select.Option>
              <Select.Option value="POST">POST</Select.Option>
              <Select.Option value="PUT">PUT</Select.Option>
              <Select.Option value="DELETE">DELETE</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="接口描述" />
          </Form.Item>
          <Form.Item name="params" label="请求参数（JSON格式）">
            <TextArea rows={5} placeholder='{"username": "string", "password": "string"}' />
          </Form.Item>
          <Form.Item name="response_example" label="响应示例（JSON格式）">
            <TextArea rows={5} placeholder='{"code": 200, "message": "success", "data": {}}' />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={`测试点列表 - ${selectedInterface?.name}`}
        open={testPointsModalVisible}
        onCancel={() => setTestPointsModalVisible(false)}
        footer={null}
        width={1000}
      >
        <ProTable<TestPoint>
          columns={testPointColumns}
          dataSource={testPoints}
          rowKey="id"
          search={false}
          pagination={false}
          toolBarRender={false}
        />
      </Modal>
    </PageContainer>
  );
};

