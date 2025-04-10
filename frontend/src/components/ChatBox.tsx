import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Message, sendMessage, sendMessageStream, StreamChunk, stopMessageGeneration, getMessages } from '../services/chat';
import { Loader2, Send, ArrowLeft, X, Square } from 'lucide-react';

interface ChatBoxProps {
  sessionId?: string;
  onSessionCreated?: (sessionId: string) => void;
}

const ChatBox: React.FC<ChatBoxProps> = ({ sessionId, onSessionCreated }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [streamSession, setStreamSession] = useState<string | null>(null);
  const [streamContent, setStreamContent] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  
  // 加载现有消息
  useEffect(() => {
    if (sessionId) {
      fetchMessages();
    } else {
      setMessages([]);
    }
  }, [sessionId]);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamContent]);

  // 获取消息列表
  const fetchMessages = async () => {
    if (!sessionId) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await getMessages(sessionId);
      if (response.success) {
        setMessages(response.data);
      } else {
        throw new Error(response.message || '获取消息失败');
      }
    } catch (error) {
      console.error('获取消息失败:', error);
      setError(error instanceof Error ? error.message : '获取消息失败');
    } finally {
      setLoading(false);
    }
  };

  // 发送消息（流式）
  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;
    
    // 清除之前的错误
    setError(null);
    
    // 创建临时用户消息
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      content: newMessage,
      role: 'user',
      session_id: sessionId || '',
      created_at: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    const userInput = newMessage;
    setNewMessage('');
    setLoading(true);
    
    try {
      // 准备接收流式响应
      setStreamContent('');
      
      // 创建临时助手消息用于流式显示
      const tempAssistantMsg: Message = {
        id: `assistant-stream-${Date.now()}`,
        content: '',
        role: 'assistant',
        session_id: sessionId || '',
        created_at: new Date().toISOString()
      };
      
      // 添加临时消息
      setMessages(prev => [...prev, { ...tempAssistantMsg }]);
      
      // 处理流式数据
      await sendMessageStream(
        userInput, 
        sessionId,
        (chunk: StreamChunk) => {
          // 处理会话ID
          if (chunk.session_id && !sessionId) {
            setStreamSession(chunk.session_id);
            if (onSessionCreated) {
              onSessionCreated(chunk.session_id);
            }
          }
          
          // 处理内容块
          if (chunk.chunk) {
            setStreamContent(prev => prev + chunk.chunk);
            
            // 更新消息内容
            setMessages(prev => {
              const newMessages = [...prev];
              const lastMsg = newMessages[newMessages.length - 1];
              if (lastMsg && lastMsg.role === 'assistant') {
                lastMsg.content = (lastMsg.content || '') + chunk.chunk;
              }
              return newMessages;
            });
          }
          
          // 处理完成标记
          if (chunk.done) {
            setLoading(false);
            setStreamContent('');
          }
        },
        (error: Error) => {
          console.error('流式请求错误:', error);
          setLoading(false);
          setError(error.message);
          
          // 在消息中显示错误
          setMessages(prev => {
            const newMessages = [...prev];
            const lastMsg = newMessages[newMessages.length - 1];
            if (lastMsg && lastMsg.role === 'assistant') {
              lastMsg.content = `抱歉，出现了错误: ${error.message}`;
            }
            return newMessages;
          });
        }
      );
      
    } catch (error) {
      console.error('发送消息失败:', error);
      setLoading(false);
      setError(error instanceof Error ? error.message : '发送消息失败');
    }
  };

  // 停止生成
  const handleStopGeneration = async () => {
    if (sessionId) {
      try {
        await stopMessageGeneration(sessionId);
      } catch (error) {
        console.error('停止生成失败:', error);
      }
    }
    setLoading(false);
  };

  // 处理回车键发送消息
  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full w-full">
      {/* 聊天头部 */}
      <div className="p-3 bg-primary text-primary-foreground flex items-center">
        <Button 
          variant="ghost" 
          size="icon" 
          onClick={() => navigate('/app/chat')}
          className="mr-2 text-primary-foreground"
        >
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <h2 className="text-lg font-semibold">智能客服</h2>
      </div>
      
      {/* 错误提示 */}
      {error && (
        <div className="p-2 bg-destructive/10 text-destructive text-sm">
          <p className="px-4 py-1">错误: {error}</p>
        </div>
      )}
      
      {/* 消息列表 */}
      <div className="flex-grow p-4 overflow-y-auto bg-muted/20">
        {messages.length === 0 && !loading && (
          <div className="flex justify-center items-center h-full">
            <p className="text-muted-foreground">
              {sessionId ? '没有消息，开始聊天吧' : '新对话，有什么我可以帮你的？'}
            </p>
          </div>
        )}
        
        {messages.map((msg, index) => (
          <div
            key={msg.id}
            className={`p-3 my-2 rounded-lg max-w-[80%] ${
              msg.role === 'user' 
                ? 'ml-auto bg-primary text-primary-foreground' 
                : 'mr-auto bg-secondary text-secondary-foreground'
            }`}
          >
            <p className="break-words whitespace-pre-line">{msg.content}</p>
            {index === messages.length - 1 && msg.role === 'assistant' && loading && (
              <div className="mt-2 animate-pulse">
                <Loader2 className="h-4 w-4 animate-spin inline mr-2" />
                <span className="text-xs">AI 正在思考...</span>
              </div>
            )}
          </div>
        ))}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* 消息输入框 */}
      <div className="p-4 border-t bg-background">
        <div className="flex gap-2">
          <Input
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="输入消息..."
            disabled={loading}
            className="flex-1"
          />
          {loading ? (
            <Button 
              variant="destructive"
              onClick={handleStopGeneration}
            >
              <X className="h-4 w-4 mr-2" />
              停止
            </Button>
          ) : (
            <Button 
              onClick={handleSendMessage}
              disabled={!newMessage.trim()}
            >
              <Send className="h-4 w-4 mr-2" />
              发送
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatBox; 