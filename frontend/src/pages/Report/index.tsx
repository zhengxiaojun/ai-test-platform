import { PageContainer, ProTable, ProColumns } from '@ant-design/pro-components';
import { Card, Tag, Space, Button, Modal, Descriptions, List } from 'antd';
import { EyeOutlined } from '@ant-design/icons';
import { useState, useEffect } from 'react';
import { reportAPI, TestReport } from '@/services/api';

export default () => {
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedReport, setSelectedReport] = useState<any>(null);
  const [reportList, setReportList] = useState<TestReport[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const data: any = await reportAPI.list();
      setReportList(data || []);
    } catch (error) {
      console.error('获取报告列表失败', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleViewDetail = async (record: TestReport) => {
    const detail = await reportAPI.get(record.id!);
    setSelectedReport(detail);
    setDetailModalVisible(true);
  };

  const columns: ProColumns<TestReport>[] = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 60,
      hideInSearch: true,
    },
    {
      title: '报告标题',
      dataIndex: 'title',
      width: 250,
      formItemProps: {
        label: '报告标题',
      },
    },
    {
      title: '总用例数',
      dataIndex: 'total_cases',
      width: 100,
      hideInSearch: true,
    },
    {
      title: '通过',
      dataIndex: 'passed_cases',
      width: 80,
      hideInSearch: true,
      render: (text: any) => (
        <Tag color="success">{text}</Tag>
      ),
    },
    {
      title: '失败',
      dataIndex: 'failed_cases',
      width: 80,
      hideInSearch: true,
      render: (text: any) => (
        <Tag color="error">{text}</Tag>
      ),
    },
    {
      title: '错误',
      dataIndex: 'error_cases',
      width: 80,
      hideInSearch: true,
      render: (text: any) => (
        <Tag color="warning">{text}</Tag>
      ),
    },
    {
      title: '通过率',
      dataIndex: 'pass_rate',
      width: 100,
      hideInSearch: true,
      render: (text: any) => {
        const rate = parseFloat(text || '0');
        const color = rate >= 80 ? 'success' : rate >= 60 ? 'warning' : 'error';
        return <Tag color={color}>{text}</Tag>;
      },
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
      width: 120,
      fixed: 'right',
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          icon={<EyeOutlined />}
          onClick={() => handleViewDetail(record)}
        >
          查看详情
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
          { title: '测试报告' },
        ],
      }}
      style={{ background: 'transparent' }}
    >
      <ProTable<TestReport>
        columns={columns}
        dataSource={reportList}
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
          reload: () => fetchReports(),
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
            onClick={() => fetchReports()}
            icon={<EyeOutlined />}
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
        title="测试报告详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={1000}
      >
        {selectedReport && (
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <Card title="基本信息" size="small">
              <Descriptions column={2}>
                <Descriptions.Item label="报告标题">
                  {selectedReport.title}
                </Descriptions.Item>
                <Descriptions.Item label="执行ID">
                  {selectedReport.execution_id}
                </Descriptions.Item>
                <Descriptions.Item label="总用例数">
                  {selectedReport.total_cases}
                </Descriptions.Item>
                <Descriptions.Item label="通过率">
                  <Tag color="success">{selectedReport.pass_rate}</Tag>
                </Descriptions.Item>
                <Descriptions.Item label="通过">
                  <Tag color="success">{selectedReport.passed_cases}</Tag>
                </Descriptions.Item>
                <Descriptions.Item label="失败">
                  <Tag color="error">{selectedReport.failed_cases}</Tag>
                </Descriptions.Item>
                <Descriptions.Item label="错误">
                  <Tag color="warning">{selectedReport.error_cases}</Tag>
                </Descriptions.Item>
                <Descriptions.Item label="创建时间">
                  {selectedReport.created_at}
                </Descriptions.Item>
              </Descriptions>
            </Card>

            {selectedReport.summary && (
              <Card title="AI 智能总结" size="small">
                <p>{selectedReport.summary}</p>
              </Card>
            )}

            {selectedReport.risk_analysis && (
              <Card title="风险分析" size="small">
                {selectedReport.risk_analysis.high_risks &&
                  selectedReport.risk_analysis.high_risks.length > 0 && (
                  <div style={{ marginBottom: 16 }}>
                    <Tag color="error">高风险</Tag>
                    <List
                      size="small"
                      dataSource={selectedReport.risk_analysis.high_risks}
                      renderItem={(item: string) => <List.Item>{item}</List.Item>}
                    />
                  </div>
                )}
                {selectedReport.risk_analysis.medium_risks &&
                  selectedReport.risk_analysis.medium_risks.length > 0 && (
                  <div style={{ marginBottom: 16 }}>
                    <Tag color="warning">中风险</Tag>
                    <List
                      size="small"
                      dataSource={selectedReport.risk_analysis.medium_risks}
                      renderItem={(item: string) => <List.Item>{item}</List.Item>}
                    />
                  </div>
                )}
              </Card>
            )}

            {selectedReport.optimization_suggestions &&
              selectedReport.optimization_suggestions.length > 0 && (
              <Card title="优化建议" size="small">
                <List
                  dataSource={selectedReport.optimization_suggestions}
                  renderItem={(item: any) => (
                    <List.Item>
                      <List.Item.Meta
                        title={
                          <Space>
                            {item.title}
                            <Tag color={
                              item.priority === 'high' ? 'error' :
                              item.priority === 'medium' ? 'warning' : 'default'
                            }>
                              {item.priority}
                            </Tag>
                          </Space>
                        }
                        description={item.description}
                      />
                    </List.Item>
                  )}
                />
              </Card>
            )}
          </Space>
        )}
      </Modal>
    </PageContainer>
  );
};

