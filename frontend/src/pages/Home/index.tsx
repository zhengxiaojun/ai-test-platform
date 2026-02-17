import { useState, useRef, useEffect } from 'react';
import { Input, Button, Card, Avatar, Space, Spin, message } from 'antd';
import { SendOutlined, RobotOutlined, UserOutlined } from '@ant-design/icons';
import axios from 'axios';

const { TextArea } = Input;

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: '你好！我是AI测试助手，可以帮你分析测试需求、生成测试用例、解答测试问题。请问有什么我可以帮助你的？',
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) {
      return;
    }

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // 调用后端AI接口
      const response = await axios.post('/api/chat', {
        message: input,
        history: messages,
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.message || '抱歉，我现在无法回答这个问题。',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      message.error('发送失败，请稍后重试');
      // 添加错误提示消息
      const errorMessage: Message = {
        role: 'assistant',
        content: '抱歉，我遇到了一些问题。请确保后端服务正常运行。',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{
      height: 'calc(100vh - 112px)',
      display: 'flex',
      flexDirection: 'column',
      background: '#fff',
      borderRadius: '8px',
      overflow: 'hidden',
    }}>
      {/* 消息列表 */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '24px',
        background: '#fafafa',
      }}>
        <Space direction="vertical" size={16} style={{ width: '100%' }}>
          {messages.map((msg, index) => (
            <div
              key={index}
              style={{
                display: 'flex',
                justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
              }}
            >
              <div style={{
                display: 'flex',
                flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                maxWidth: '70%',
                gap: '12px',
              }}>
                <Avatar
                  size={36}
                  icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                  style={{
                    backgroundColor: msg.role === 'user' ? '#1890ff' : '#52c41a',
                    flexShrink: 0,
                  }}
                />
                <Card
                  size="small"
                  style={{
                    background: msg.role === 'user' ? '#e6f7ff' : '#fff',
                    border: 'none',
                    boxShadow: '0 1px 2px rgba(0,0,0,0.08)',
                  }}
                  bodyStyle={{
                    padding: '12px 16px',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                  }}
                >
                  {msg.content}
                </Card>
              </div>
            </div>
          ))}
          {loading && (
            <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
              <div style={{ display: 'flex', gap: '12px', maxWidth: '70%' }}>
                <Avatar
                  size={36}
                  icon={<RobotOutlined />}
                  style={{ backgroundColor: '#52c41a', flexShrink: 0 }}
                />
                <Card
                  size="small"
                  style={{
                    background: '#fff',
                    border: 'none',
                    boxShadow: '0 1px 2px rgba(0,0,0,0.08)',
                  }}
                  bodyStyle={{ padding: '12px 16px' }}
                >
                  <Spin size="small" /> 正在思考...
                </Card>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </Space>
      </div>

      {/* 输入框 */}
      <div style={{
        padding: '16px 24px',
        background: '#fff',
        borderTop: '1px solid #f0f0f0',
      }}>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
          <TextArea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入消息... (按 Enter 发送，Shift + Enter 换行)"
            autoSize={{ minRows: 1, maxRows: 4 }}
            style={{ flex: 1 }}
            disabled={loading}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            loading={loading}
            size="large"
            style={{ height: '40px' }}
          >
            发送
          </Button>
        </div>
        <div style={{
          marginTop: '8px',
          fontSize: '12px',
          color: '#999',
        }}>
          💡 提示：你可以询问测试相关问题，或让我帮你生成测试用例
        </div>
      </div>
    </div>
  );
};

