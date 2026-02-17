import { PageContainer, ProTable, ProColumns } from '@ant-design/pro-components';
import { Button, Modal, Tag, Space, message, Drawer } from 'antd';
import { PlayCircleOutlined, CodeOutlined, DeleteOutlined } from '@ant-design/icons';
import { useState, useEffect } from 'react';
import { testCaseAPI, TestCase } from '@/services/api';

export default () => {
  const [codeDrawerVisible, setCodeDrawerVisible] = useState(false);
  const [selectedTestCase, setSelectedTestCase] = useState<TestCase | null>(null);
  const [testCaseList, setTestCaseList] = useState<TestCase[]>([]);
  const [loading, setLoading] = useState(false);

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
      render: (type: any) => (
        <Tag color={type === 'api' ? 'blue' : 'green'}>
          {type?.toUpperCase()}
        </Tag>
      ),
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
      width: 250,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<PlayCircleOutlined />}
            onClick={() => handleExecute(record)}
          >
            执行
          </Button>
          <Button
            type="link"
            size="small"
            icon={<CodeOutlined />}
            onClick={() => handleViewCode(record)}
          >
            查看代码
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => {
              Modal.confirm({
                title: '确认删除',
                content: '确定要删除这个测试用例吗？',
                onOk: () => handleDelete(record.id!),
              });
            }}
          >
            删除
          </Button>
        </Space>
      ),
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
    </PageContainer>
  );
};

