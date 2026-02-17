import { PageContainer, ProTable, ProColumns } from '@ant-design/pro-components';
import { Tag, Space, Button, Modal, Descriptions, message } from 'antd';
import { EyeOutlined, FileTextOutlined } from '@ant-design/icons';
import { useState, useEffect } from 'react';
import { testCaseAPI, reportAPI } from '@/services/api';

interface Execution {
  id: number;
  test_case_id?: number;
  status: 'pending' | 'running' | 'success' | 'failed' | 'error';
  start_time?: string;
  end_time?: string;
  duration?: number;
  error_message?: string;
  created_at: string;
}

export default () => {
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedExecution, setSelectedExecution] = useState<Execution | null>(null);
  const [allExecutions, setAllExecutions] = useState<Execution[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchExecutions = async () => {
    setLoading(true);
    try {
      const testCases: any = await testCaseAPI.list();
      const executions: Execution[] = [];

      for (const tc of testCases || []) {
        try {
          const execs: any = await testCaseAPI.getExecutions(tc.id);
          executions.push(...(execs || []));
        } catch (error) {
          // 忽略错误
        }
      }

      executions.sort((a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );

      setAllExecutions(executions);
    } catch (error) {
      message.error('获取执行记录失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExecutions();
  }, []);

  const handleViewDetail = (record: Execution) => {
    setSelectedExecution(record);
    setDetailModalVisible(true);
  };

  const handleGenerateReport = async (executionId: number) => {
    try {
      await reportAPI.generate(executionId);
      message.success('报告生成成功');
    } catch (error) {
      message.error('报告生成失败');
    }
  };

  const columns: ProColumns<Execution>[] = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 80,
      hideInSearch: true,
    },
    {
      title: '测试用例ID',
      dataIndex: 'test_case_id',
      width: 120,
      hideInSearch: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      hideInSearch: true,
      render: (status: any) => {
        const colors: Record<string, string> = {
          pending: 'default',
          running: 'processing',
          success: 'success',
          failed: 'error',
          error: 'warning'
        };
        return <Tag color={colors[status]}>{status?.toUpperCase()}</Tag>;
      },
      valueEnum: {
        pending: { text: '等待中', status: 'Default' },
        running: { text: '运行中', status: 'Processing' },
        success: { text: '成功', status: 'Success' },
        failed: { text: '失败', status: 'Error' },
        error: { text: '错误', status: 'Warning' },
      },
    },
    {
      title: '开始时间',
      dataIndex: 'start_time',
      valueType: 'dateTime',
      width: 180,
      hideInSearch: true,
    },
    {
      title: '结束时间',
      dataIndex: 'end_time',
      valueType: 'dateTime',
      width: 180,
      hideInSearch: true,
    },
    {
      title: '耗时(秒)',
      dataIndex: 'duration',
      width: 100,
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
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            详情
          </Button>
          <Button
            type="link"
            size="small"
            icon={<FileTextOutlined />}
            onClick={() => handleGenerateReport(record.id)}
          >
            生成报告
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
          { title: '测试执行' },
        ],
      }}
      style={{ background: 'transparent' }}
    >
      <ProTable<Execution>
        columns={columns}
        dataSource={allExecutions}
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
          reload: () => fetchExecutions(),
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
            onClick={() => fetchExecutions()}
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

      <Modal
        title="执行详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={800}
      >
        {selectedExecution && (
          <Descriptions column={2} bordered>
            <Descriptions.Item label="执行ID">
              {selectedExecution.id}
            </Descriptions.Item>
            <Descriptions.Item label="测试用例ID">
              {selectedExecution.test_case_id}
            </Descriptions.Item>
            <Descriptions.Item label="状态">
              <Tag color={
                selectedExecution.status === 'success' ? 'success' :
                selectedExecution.status === 'failed' ? 'error' :
                selectedExecution.status === 'running' ? 'processing' : 'default'
              }>
                {selectedExecution.status.toUpperCase()}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="耗时">
              {selectedExecution.duration ? `${selectedExecution.duration}秒` : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="开始时间" span={2}>
              {selectedExecution.start_time || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="结束时间" span={2}>
              {selectedExecution.end_time || '-'}
            </Descriptions.Item>
            {selectedExecution.error_message && (
              <Descriptions.Item label="错误信息" span={2}>
                <pre style={{
                  background: '#fff1f0',
                  padding: '12px',
                  borderRadius: '4px',
                  color: '#cf1322'
                }}>
                  {selectedExecution.error_message}
                </pre>
              </Descriptions.Item>
            )}
          </Descriptions>
        )}
      </Modal>
    </PageContainer>
  );
};

