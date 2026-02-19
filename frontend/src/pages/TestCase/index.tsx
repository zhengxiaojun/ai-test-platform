import { PageContainer, ProTable, ProColumns } from '@ant-design/pro-components';
import { Button, Modal, Tag, Space, message, Drawer, Form, Input, Select, Upload, Dropdown } from 'antd';
import { PlayCircleOutlined, CodeOutlined, DeleteOutlined, EditOutlined, CopyOutlined, DownloadOutlined, UploadOutlined, MoreOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { useState, useEffect } from 'react';
import { testCaseAPI, TestCase } from '@/services/api';

const { TextArea } = Input;

export default () => {
  const [codeDrawerVisible, setCodeDrawerVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [selectedTestCase, setSelectedTestCase] = useState<TestCase | null>(null);
  const [testCaseList, setTestCaseList] = useState<TestCase[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [form] = Form.useForm();

  const fetchTestCases = async () => {
    setLoading(true);
    try {
      const data: any = await testCaseAPI.list();
      setTestCaseList(data || []);
    } catch (error) {
      message.error('获取测试用例列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTestCases();
  }, []);

  const handleExecute = async (record: TestCase) => {
    try {
      const result: any = await testCaseAPI.execute(record.id!);
      message.success(`测试已提交执行，执行ID: ${result.execution_id}`);
    } catch (error) {
      message.error('执行失败');
    }
  };

  const handleViewCode = (record: TestCase) => {
    setSelectedTestCase(record);
    setCodeDrawerVisible(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await testCaseAPI.delete(id);
      message.success('删除成功');
      fetchTestCases();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleEdit = (record: TestCase) => {
    setSelectedTestCase(record);
    form.setFieldsValue({
      name: record.name,
      description: record.description,
      test_type: record.test_type,
      code: record.code,
      test_data: JSON.stringify(record.test_data, null, 2),
      expected_result: record.expected_result,
      tags: record.tags,
    });
    setEditModalVisible(true);
  };

  const handleUpdate = async () => {
    try {
      const values = await form.validateFields();
      const updateData = {
        ...values,
        test_data: values.test_data ? JSON.parse(values.test_data) : null,
      };
      await testCaseAPI.update(selectedTestCase!.id!, updateData);
      message.success('更新成功');
      setEditModalVisible(false);
      fetchTestCases();
    } catch (error) {
      message.error('更新失败');
    }
  };

  const handleClone = async (id: number) => {
    try {
      await testCaseAPI.clone(id);
      message.success('克隆成功');
      fetchTestCases();
    } catch (error) {
      message.error('克隆失败');
    }
  };

  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请选择要删除的测试用例');
      return;
    }
    Modal.confirm({
      title: '批量删除',
      content: `确定要删除选中的 ${selectedRowKeys.length} 个测试用例吗？`,
      onOk: async () => {
        try {
          await testCaseAPI.batchDelete(selectedRowKeys as number[]);
          message.success('批量删除成功');
          setSelectedRowKeys([]);
          fetchTestCases();
        } catch (error) {
          message.error('批量删除失败');
        }
      },
    });
  };

  const handleBatchExecute = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请选择要执行的测试用例');
      return;
    }
    try {
      const result: any = await testCaseAPI.batchExecute(selectedRowKeys as number[]);
      message.success(`已提交 ${selectedRowKeys.length} 个测试用例执行`);
      setSelectedRowKeys([]);
    } catch (error) {
      message.error('批量执行失败');
    }
  };

  const handleExport = async () => {
    try {
      const result: any = await testCaseAPI.exportJson();
      const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `test_cases_${new Date().getTime()}.json`;
      a.click();
      window.URL.revokeObjectURL(url);
      message.success('导出成功');
    } catch (error) {
      message.error('导出失败');
    }
  };

  const handleImport = (file: File) => {
    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const data = JSON.parse(e.target?.result as string);
        const testCases = data.data || data;
        await testCaseAPI.importJson(testCases);
        message.success('导入成功');
        fetchTestCases();
      } catch (error) {
        message.error('导入失败，请检查文件格式');
      }
    };
    reader.readAsText(file);
    return false; // 阻止默认上传行为
  };

  const columns: ProColumns<TestCase>[] = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 60,
      search: false,
      hideInSearch: true,
    },
    {
      title: '用例名称',
      dataIndex: 'name',
      width: 200,
      formItemProps: {
        label: '用例名称',
      },
    },
    {
      title: '描述',
      dataIndex: 'description',
      ellipsis: true,
      search: false,
      hideInSearch: true,
    },
    {
      title: '测试类型',
      dataIndex: 'test_type',
      width: 100,
      hideInSearch: true,
      render: (text: any, record: any) => {
        const type = text || record.test_type;
        return (
          <Tag color={type === 'api' ? 'blue' : 'green'}>
            {type?.toUpperCase ? type.toUpperCase() : type}
          </Tag>
        );
      },
      valueEnum: {
        api: { text: 'API', status: 'Default' },
        ui: { text: 'UI', status: 'Success' },
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      valueType: 'dateTime',
      width: 180,
      search: false,
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
            key: 'viewCode',
            icon: <CodeOutlined />,
            label: '查看代码',
            onClick: () => handleViewCode(record),
          },
          {
            key: 'edit',
            icon: <EditOutlined />,
            label: '编辑',
            onClick: () => handleEdit(record),
          },
          {
            key: 'clone',
            icon: <CopyOutlined />,
            label: '克隆',
            onClick: () => handleClone(record.id!),
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
                content: '确定要删除这个测试用例吗？',
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
              icon={<PlayCircleOutlined />}
              onClick={() => handleExecute(record)}
            >
              执行
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

  return (
    <PageContainer
      title={false}
      breadcrumb={{
        items: [
          { title: '资源管理' },
          { title: '测试用例' },
        ],
      }}
      style={{ background: 'transparent' }}
    >
      <ProTable<TestCase>
        columns={columns}
        dataSource={testCaseList}
        loading={loading}
        rowKey="id"
        rowSelection={{
          selectedRowKeys,
          onChange: (keys) => setSelectedRowKeys(keys),
        }}
        search={{
          labelWidth: 100,
          defaultCollapsed: false,
          span: 6,
          optionRender: (searchConfig, formProps, dom) => [
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
          reload: () => fetchTestCases(),
          density: false,
          setting: true,
        }}
        pagination={{
          pageSize: 10,
          showQuickJumper: true,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`,
        }}
        toolBarRender={() => [
          <Button
            key="batchExecute"
            type="primary"
            disabled={selectedRowKeys.length === 0}
            onClick={handleBatchExecute}
          >
            批量执行
          </Button>,
          <Button
            key="batchDelete"
            danger
            disabled={selectedRowKeys.length === 0}
            onClick={handleBatchDelete}
          >
            批量删除
          </Button>,
          <Button
            key="export"
            icon={<DownloadOutlined />}
            onClick={handleExport}
          >
            导出
          </Button>,
          <Upload
            key="import"
            accept=".json"
            showUploadList={false}
            beforeUpload={handleImport}
          >
            <Button icon={<UploadOutlined />}>导入</Button>
          </Upload>,
          <Button
            key="refresh"
            onClick={() => fetchTestCases()}
          >
            刷新
          </Button>,
        ]}
        size="middle"
        cardProps={{
          bodyStyle: { padding: 0 },
        }}
        style={{ background: '#fff' }}
      />

      <Drawer
        title={`测试代码 - ${selectedTestCase?.name}`}
        open={codeDrawerVisible}
        onClose={() => setCodeDrawerVisible(false)}
        width={800}
      >
        {selectedTestCase && (
          <div>
            <h3>用例描述</h3>
            <p>{selectedTestCase.description}</p>

            <h3>测试代码</h3>
            <pre style={{
              background: '#f5f5f5',
              padding: '16px',
              borderRadius: '4px',
              overflow: 'auto'
            }}>
              <code>{selectedTestCase.code}</code>
            </pre>

            {selectedTestCase.test_data && (
              <>
                <h3>测试数据</h3>
                <pre style={{
                  background: '#f5f5f5',
                  padding: '16px',
                  borderRadius: '4px',
                  overflow: 'auto'
                }}>
                  <code>{JSON.stringify(selectedTestCase.test_data, null, 2)}</code>
                </pre>
              </>
            )}

            {selectedTestCase.expected_result && (
              <>
                <h3>预期结果</h3>
                <p>{selectedTestCase.expected_result}</p>
              </>
            )}
          </div>
        )}
      </Drawer>

      <Modal
        title="编辑测试用例"
        open={editModalVisible}
        onOk={handleUpdate}
        onCancel={() => {
          setEditModalVisible(false);
          form.resetFields();
        }}
        width={800}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="用例名称"
            name="name"
            rules={[{ required: true, message: '请输入用例名称' }]}
          >
            <Input placeholder="请输入用例名称" />
          </Form.Item>

          <Form.Item label="描述" name="description">
            <TextArea rows={3} placeholder="请输入描述" />
          </Form.Item>

          <Form.Item
            label="测试类型"
            name="test_type"
            rules={[{ required: true, message: '请选择测试类型' }]}
          >
            <Select>
              <Select.Option value="api">API</Select.Option>
              <Select.Option value="ui">UI</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="测试代码"
            name="code"
            rules={[{ required: true, message: '请输入测试代码' }]}
          >
            <TextArea
              rows={10}
              placeholder="请输入测试代码"
              style={{ fontFamily: 'monospace' }}
            />
          </Form.Item>

          <Form.Item label="测试数据(JSON格式)" name="test_data">
            <TextArea
              rows={6}
              placeholder='{"key": "value"}'
              style={{ fontFamily: 'monospace' }}
            />
          </Form.Item>

          <Form.Item label="预期结果" name="expected_result">
            <TextArea rows={3} placeholder="请输入预期结果" />
          </Form.Item>

          <Form.Item label="标签" name="tags">
            <Select mode="tags" placeholder="请输入标签，按回车添加">
              <Select.Option value="smoke">smoke</Select.Option>
              <Select.Option value="regression">regression</Select.Option>
              <Select.Option value="critical">critical</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </PageContainer>
  );
};

