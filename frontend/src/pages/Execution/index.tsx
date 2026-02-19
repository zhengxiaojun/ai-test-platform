import { PageContainer, ProTable, ProColumns } from '@ant-design/pro-components';
import { Tag, Space, Button, Modal, Descriptions, message } from 'antd';
import { EyeOutlined, FileTextOutlined } from '@ant-design/icons';
import { useState, useEffect } from 'react';
import { testCaseAPI, reportAPI } from '@/services/api';

interface Execution {
  id: number;
  test_case_id?: number;
  test_case_name?: string;
  status: 'pending' | 'running' | 'success' | 'failed' | 'error';
  start_time?: string;
  end_time?: string;
  duration?: number;
  error_message?: string;
  result?: any;
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

      // 创建测试用例ID到名称的映射
      const testCaseMap = new Map();
      (testCases || []).forEach((tc: any) => {
        testCaseMap.set(tc.id, tc.name);
      });

      for (const tc of testCases || []) {
        try {
          const execs: any = await testCaseAPI.getExecutions(tc.id);
          // 确保test_case_id存在并正确映射名称
          const execsWithName = (execs || []).map((exec: any) => ({
            ...exec,
            test_case_id: exec.test_case_id || tc.id,
            test_case_name: testCaseMap.get(exec.test_case_id || tc.id) || tc.name || `用例#${exec.test_case_id || tc.id}`
          }));
          executions.push(...execsWithName);
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
      message.loading({ content: '正在生成报告...', key: 'generateReport', duration: 0 });
      await reportAPI.generate(executionId);
      message.success({ content: '报告生成成功！', key: 'generateReport' });
    } catch (error) {
      message.error({ content: '报告生成失败', key: 'generateReport' });
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
      title: '测试用例',
      dataIndex: 'test_case_name',
      width: 250,
      ellipsis: true,
      hideInSearch: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      hideInSearch: true,
      render: (text: any, record: any) => {
        const status = text || record.status;
        const colors: Record<string, string> = {
          pending: 'default',
          running: 'processing',
          success: 'success',
          failed: 'error',
          error: 'warning'
        };
        return <Tag color={colors[status]}>{status?.toUpperCase ? status.toUpperCase() : status}</Tag>;
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
        scroll={{ x: 1400 }}
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
        width={900}
      >
        {selectedExecution && (
          <Descriptions column={2} bordered>
            <Descriptions.Item label="执行ID">
              {selectedExecution.id}
            </Descriptions.Item>
            <Descriptions.Item label="测试用例">
              {selectedExecution.test_case_name || `用例#${selectedExecution.test_case_id}`}
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

            {/* 显示完整的执行结果信息 */}
            {selectedExecution.result && (
              <>
                {/* 显示执行状态 */}
                {selectedExecution.result.status && (
                  <Descriptions.Item label="执行状态" span={2}>
                    <Tag color={selectedExecution.result.status === 'success' ? 'success' : 'error'}>
                      {selectedExecution.result.status.toUpperCase()}
                    </Tag>
                  </Descriptions.Item>
                )}

                {/* 显示执行时长 */}
                {selectedExecution.result.duration !== undefined && (
                  <Descriptions.Item label="执行时长">
                    {selectedExecution.result.duration}秒
                  </Descriptions.Item>
                )}

                {/* 显示返回码 */}
                {selectedExecution.result.return_code !== undefined && (
                  <Descriptions.Item label="返回码">
                    <Tag color={selectedExecution.result.return_code === 0 ? 'success' : 'error'}>
                      {selectedExecution.result.return_code}
                      {selectedExecution.result.return_code === 0 ? ' (成功)' : ' (失败)'}
                    </Tag>
                  </Descriptions.Item>
                )}

                {/* 显示文件路径 */}
                {selectedExecution.result.file_path && (
                  <Descriptions.Item label="测试文件" span={2}>
                    <code style={{ fontSize: '12px', background: '#f5f5f5', padding: '2px 6px', borderRadius: '3px' }}>
                      {selectedExecution.result.file_path}
                    </code>
                  </Descriptions.Item>
                )}

                {/* 显示日志路径 */}
                {selectedExecution.result.log_path && (
                  <Descriptions.Item label="日志文件" span={2}>
                    <code style={{ fontSize: '12px', background: '#f5f5f5', padding: '2px 6px', borderRadius: '3px' }}>
                      {selectedExecution.result.log_path}
                    </code>
                  </Descriptions.Item>
                )}

                {/* 显示HTML报告路径 */}
                {selectedExecution.result.html_report_path && (
                  <Descriptions.Item label="HTML报告" span={2}>
                    <code style={{ fontSize: '12px', background: '#f5f5f5', padding: '2px 6px', borderRadius: '3px' }}>
                      {selectedExecution.result.html_report_path}
                    </code>
                  </Descriptions.Item>
                )}

                {/* 显示JSON报告路径 */}
                {selectedExecution.result.json_report_path && (
                  <Descriptions.Item label="JSON报告" span={2}>
                    <code style={{ fontSize: '12px', background: '#f5f5f5', padding: '2px 6px', borderRadius: '3px' }}>
                      {selectedExecution.result.json_report_path}
                    </code>
                  </Descriptions.Item>
                )}

                {/* 显示测试结果统计 */}
                {(() => {
                  const testResults = selectedExecution.result.test_results ||
                                     selectedExecution.result.result?.test_results;

                  if (testResults && testResults.summary) {
                    return (
                      <Descriptions.Item label="测试统计" span={2}>
                        <div style={{ background: '#f5f5f5', padding: '12px', borderRadius: '4px' }}>
                          <Space size="large">
                            <span><Tag color="default">总计: {testResults.summary.total || 0}</Tag></span>
                            <span><Tag color="success">通过: {testResults.summary.passed || 0}</Tag></span>
                            <span><Tag color="error">失败: {testResults.summary.failed || 0}</Tag></span>
                            {testResults.summary.skipped > 0 && (
                              <span><Tag color="warning">跳过: {testResults.summary.skipped || 0}</Tag></span>
                            )}
                          </Space>
                        </div>
                      </Descriptions.Item>
                    );
                  }
                  return null;
                })()}

                {/* 显示测试用例详情 */}
                {(() => {
                  const testResults = selectedExecution.result.test_results ||
                                     selectedExecution.result.result?.test_results;

                  if (testResults && testResults.tests && testResults.tests.length > 0) {
                    return (
                      <Descriptions.Item label="测试详情" span={2}>
                        <div style={{ background: '#f5f5f5', padding: '12px', borderRadius: '4px', maxHeight: '200px', overflow: 'auto' }}>
                          {testResults.tests.map((test: any, index: number) => (
                            <div key={index} style={{ marginBottom: '8px', padding: '8px', background: '#fff', borderRadius: '4px' }}>
                              <Space direction="vertical" style={{ width: '100%' }}>
                                <div>
                                  <Tag color={test.outcome === 'passed' ? 'success' : 'error'}>
                                    {test.outcome}
                                  </Tag>
                                  <span style={{ fontWeight: 'bold' }}>{test.name}</span>
                                </div>
                                {test.duration && (
                                  <span style={{ fontSize: '12px', color: '#666' }}>耗时: {test.duration}秒</span>
                                )}
                                {test.call?.longrepr && (
                                  <pre style={{
                                    fontSize: '11px',
                                    color: '#cf1322',
                                    margin: 0,
                                    whiteSpace: 'pre-wrap',
                                    wordBreak: 'break-word'
                                  }}>
                                    {test.call.longrepr}
                                  </pre>
                                )}
                              </Space>
                            </div>
                          ))}
                        </div>
                      </Descriptions.Item>
                    );
                  }
                  return null;
                })()}

                {/* 显示输出日志 */}
                {selectedExecution.result.stdout && (
                  <Descriptions.Item label="标准输出" span={2}>
                    <pre style={{
                      background: '#f5f5f5',
                      padding: '12px',
                      borderRadius: '4px',
                      maxHeight: '200px',
                      overflow: 'auto',
                      fontSize: '12px',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word'
                    }}>
                      {selectedExecution.result.stdout}
                    </pre>
                  </Descriptions.Item>
                )}

                {/* 显示错误输出 */}
                {selectedExecution.result.stderr && (
                  <Descriptions.Item label="错误输出" span={2}>
                    <pre style={{
                      background: '#fff7e6',
                      padding: '12px',
                      borderRadius: '4px',
                      maxHeight: '200px',
                      overflow: 'auto',
                      fontSize: '12px',
                      color: '#d46b08',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word'
                    }}>
                      {selectedExecution.result.stderr}
                    </pre>
                  </Descriptions.Item>
                )}

                {/* 显示错误消息（result中的） */}
                {selectedExecution.result.error_message && (
                  <Descriptions.Item label="错误详情" span={2}>
                    <pre style={{
                      background: '#fff1f0',
                      padding: '12px',
                      borderRadius: '4px',
                      color: '#cf1322',
                      maxHeight: '200px',
                      overflow: 'auto',
                      fontSize: '12px',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word'
                    }}>
                      {selectedExecution.result.error_message}
                    </pre>
                  </Descriptions.Item>
                )}
              </>
            )}

            {/* 显示执行记录的错误信息（execution表的error_message字段） */}
            {selectedExecution.error_message && !selectedExecution.result?.error_message && (
              <Descriptions.Item label="错误信息" span={2}>
                <pre style={{
                  background: '#fff1f0',
                  padding: '12px',
                  borderRadius: '4px',
                  color: '#cf1322',
                  maxHeight: '200px',
                  overflow: 'auto',
                  fontSize: '12px',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word'
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

