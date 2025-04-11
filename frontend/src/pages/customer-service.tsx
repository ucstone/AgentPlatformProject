import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/auth-context';
import { useToast } from '@/components/ui/use-toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Loader2, Send } from 'lucide-react';
import { getDefaultConfig, sendMessageStream } from '@/services/llm-config';
import { createSession, getSessions, getMessages } from '@/services/chat';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export default function CustomerService() {
  const { user } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentModel, setCurrentModel] = useState('');
  const [sessionId, setSessionId] = useState<string | undefined>();

  // 加载默认模型配置
  useEffect(() => {
    const loadDefaultConfig = async () => {
      try {
        const response = await getDefaultConfig();
        if (response.data) {
          setCurrentModel(`${response.data.provider}/${response.data.model}`);
        }
      } catch (error) {
        toast({
          title: "加载模型配置失败",
          description: "无法获取默认模型配置",
          variant: "destructive",
        });
      }
    };

    loadDefaultConfig();
  }, [toast]);

  // 创建或获取会话
  useEffect(() => {
    const initSession = async () => {
      try {
        const sessionsResponse = await getSessions();
        if (sessionsResponse.data && sessionsResponse.data.length > 0) {
          setSessionId(sessionsResponse.data[0].id);
          loadMessages(sessionsResponse.data[0].id);
        } else {
          const newSessionResponse = await createSession('智能客服对话');
          if (newSessionResponse.data) {
            setSessionId(newSessionResponse.data.id);
          }
        }
      } catch (error) {
        toast({
          title: "初始化会话失败",
          description: "无法创建或获取会话",
          variant: "destructive",
        });
      }
    };

    if (user) {
      initSession();
    }
  }, [user, toast]);

  // 加载消息历史
  const loadMessages = async (sessionId: string) => {
    try {
      const response = await getMessages(sessionId);
      if (response.data) {
        setMessages(response.data.map(msg => ({
          role: msg.role as 'user' | 'assistant',
          content: msg.content,
          timestamp: msg.created_at
        })));
      }
    } catch (error) {
      toast({
        title: "加载消息失败",
        description: "无法获取历史消息",
        variant: "destructive",
      });
    }
  };

  // 滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 处理发送消息
  const handleSendMessage = async () => {
    if (!input.trim() || !sessionId) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);

    // 添加用户消息到列表
    setMessages(prev => [...prev, {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }]);

    try {
      // 使用流式响应
      await sendMessageStream(
        userMessage,
        sessionId,
        (chunk) => {
          setMessages(prev => {
            const lastMessage = prev[prev.length - 1];
            if (lastMessage && lastMessage.role === 'assistant') {
              return [
                ...prev.slice(0, -1),
                {
                  ...lastMessage,
                  content: lastMessage.content + chunk
                }
              ];
            }
            return [
              ...prev,
              {
                role: 'assistant',
                content: chunk,
                timestamp: new Date().toISOString()
              }
            ];
          });
        },
        (error) => {
          toast({
            title: "发送消息失败",
            description: error.message,
            variant: "destructive",
          });
        }
      );
    } catch (error) {
      toast({
        title: "发送消息失败",
        description: "无法发送消息",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // 处理输入框回车
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen">
      {/* 顶部信息栏 */}
      <div className="bg-white border-b p-4">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold">智能客服</h1>
          <div className="text-sm text-gray-500">
            当前模型: {currentModel || '未设置'}
          </div>
        </div>
      </div>

      {/* 聊天区域 */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((message, index) => (
            <Card
              key={index}
              className={`p-4 ${
                message.role === 'user'
                  ? 'bg-blue-50 ml-auto max-w-[80%]'
                  : 'bg-white mr-auto max-w-[80%]'
              }`}
            >
              <div className="text-sm text-gray-500 mb-1">
                {message.role === 'user' ? '您' : '智能客服'}
              </div>
              <div className="whitespace-pre-wrap">{message.content}</div>
            </Card>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* 输入区域 */}
      <div className="bg-white border-t p-4">
        <div className="max-w-4xl mx-auto flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="请输入您的问题..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button
            onClick={handleSendMessage}
            disabled={isLoading || !input.trim()}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
} 