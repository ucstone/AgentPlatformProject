import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useToast } from '@/components/ui/use-toast';
import ChatSessionList from '@/components/ChatSessionList';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';
import { AlertCircle, Send, Loader2 } from 'lucide-react';
import {
  Session,
  Message,
  getSessions,
  createSession,
  deleteSession,
  getMessages,
  sendMessage,
  stopMessageGeneration
} from '@/services/chat';

const ChatPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 状态管理
  const [sessions, setSessions] = useState<Session[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionsLoading, setSessionsLoading] = useState(false);
  const [generatingResponse, setGeneratingResponse] = useState(false);

  // 加载会话列表
  const loadSessions = async () => {
    try {
      setSessionsLoading(true);
      const response = await getSessions();
      
      if (!response.success) {
        throw new Error(response.message || '获取会话列表失败');
      }
      
      // 确保response.data是数组
      const sessionsList = Array.isArray(response.data) ? response.data : [];
      setSessions(sessionsList);
      
      // 如果没有指定会话ID，且有会话，则导航到第一个会话
      if (!sessionId && sessionsList.length > 0) {
        navigate(`/app/chat/${sessionsList[0].id}`);
      } else if (!sessionId && sessionsList.length === 0) {
        // 如果没有会话，创建一个新会话
        await handleCreateSession();
      }
    } catch (error) {
      console.error('加载会话失败:', error);
      setSessions([]);
      toast({
        title: '加载会话失败',
        description: error instanceof Error ? error.message : '无法获取会话列表，请稍后重试',
        variant: 'destructive',
      });
    } finally {
      setSessionsLoading(false);
    }
  };

  // 加载会话消息
  const loadMessages = async () => {
    if (!sessionId) {
      setMessages([]);
      return;
    }
    
    try {
      setLoading(true);
      const response = await getMessages(sessionId);
      
      if (!response.success) {
        throw new Error(response.message || '获取消息失败');
      }
      
      // 确保response.data是数组
      const messagesList = Array.isArray(response.data) ? response.data : [];
      setMessages(messagesList);
    } catch (error) {
      console.error('加载消息失败:', error);
      setMessages([]);
      toast({
        title: '加载消息失败',
        description: error instanceof Error ? error.message : '无法获取会话消息，请稍后重试',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  // 创建新会话
  const handleCreateSession = async () => {
    try {
      // 生成有意义的会话名称，包含时间戳
      const now = new Date();
      const title = `新会话 ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
      
      const response = await createSession(title);
      if (response.success) {
        const newSession = response.data;
        setSessions(prev => [...prev, newSession]);
        navigate(`/app/chat/${newSession.id}`); // 导航到新创建的会话
        setMessages([]);
        toast({
          title: "创建成功",
          description: "新会话已创建",
        });
      } else {
        throw new Error(response.message || '创建会话失败');
      }
    } catch (error) {
      console.error('创建会话失败:', error);
      toast({
        title: "创建失败",
        description: error instanceof Error ? error.message : "创建会话失败",
        variant: "destructive",
      });
    }
  };

  // 删除会话
  const handleDeleteSession = async (id: string) => {
    if (!confirm('确定要删除此会话吗？此操作不可撤销。')) return;
    
    try {
      await deleteSession(id);
      await loadSessions();
      
      if (id === sessionId) {
        // 如果删除的是当前会话，返回到会话列表
        navigate('/app/chat');
      }
      
      toast({
        title: '已删除会话',
        description: '会话已成功删除',
      });
    } catch (error) {
      console.error('删除会话失败:', error);
      toast({
        title: '删除会话失败',
        description: '无法删除会话，请稍后重试',
        variant: 'destructive',
      });
    }
  };

  // 发送消息
  const handleSendMessage = async () => {
    if (!userInput.trim() || !sessionId) return;
    
    try {
      setGeneratingResponse(true);
      
      // 添加用户消息到UI
      const userMessage: Message = {
        id: `temp-${Date.now()}`,
        session_id: sessionId,
        role: 'user',
        content: userInput,
        created_at: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, userMessage]);
      setUserInput('');
      
      // 滚动到底部
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      
      // 发送消息到服务器
      const response = await sendMessage(sessionId, userInput);
      
      // 更新消息列表
      await loadMessages();
      
    } catch (error) {
      console.error('发送消息失败:', error);
      toast({
        title: '发送消息失败',
        description: '无法发送消息，请稍后重试',
        variant: 'destructive',
      });
    } finally {
      setGeneratingResponse(false);
    }
  };
  
  // 停止生成响应
  const handleStopGeneration = async () => {
    if (!sessionId) return;
    
    try {
      await stopMessageGeneration(sessionId);
      setGeneratingResponse(false);
      toast({
        title: '已停止生成',
        description: '响应生成已停止',
      });
    } catch (error) {
      console.error('停止生成失败:', error);
      toast({
        title: '停止生成失败',
        description: '无法停止响应生成，请稍后重试',
        variant: 'destructive',
      });
    }
  };

  // 初始加载和会话切换
  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    if (sessionId) {
      loadMessages();
    } else {
      setMessages([]);
    }
  }, [sessionId]);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 渲染消息
  const renderMessage = (message: Message) => {
    const isUser = message.role === 'user';
    
    return (
      <div 
        key={message.id}
        className={`mb-4 ${isUser ? 'ml-auto' : 'mr-auto'} max-w-3/4`}
      >
        <div className={`rounded-lg p-4 ${isUser ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
          {message.content}
        </div>
        <div className={`text-xs mt-1 text-muted-foreground ${isUser ? 'text-right' : ''}`}>
          {new Date(message.created_at).toLocaleTimeString()}
        </div>
      </div>
    );
  };

  return (
    <div className="flex h-full gap-4">
      {/* 会话列表 */}
      <div className="w-1/4">
        <ChatSessionList
          sessions={sessions}
          currentSessionId={sessionId}
          loading={sessionsLoading}
          onCreateSession={handleCreateSession}
          onDeleteSession={handleDeleteSession}
          onRefresh={loadSessions}
        />
      </div>
      
      {/* 聊天区域 */}
      <div className="flex-1 flex flex-col">
        {!sessionId ? (
          <div className="flex-1 flex items-center justify-center">
            <Card className="max-w-md mx-auto text-center p-6">
              <CardContent>
                <AlertCircle className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-xl font-semibold mb-2">没有选择会话</h3>
                <p className="text-muted-foreground mb-4">
                  请选择一个现有会话或创建一个新会话来开始聊天
                </p>
                <Button onClick={handleCreateSession}>创建新会话</Button>
              </CardContent>
            </Card>
          </div>
        ) : (
          <>
            {/* 消息列表 */}
            <div className="flex-1 overflow-y-auto p-4 bg-card rounded-lg mb-4">
              {loading ? (
                <div className="flex items-center justify-center h-full">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
              ) : messages.length === 0 ? (
                <div className="flex items-center justify-center h-full text-center">
                  <div>
                    <h3 className="text-xl font-semibold mb-2">开始新对话</h3>
                    <p className="text-muted-foreground">
                      发送消息以开始与AI助手的对话
                    </p>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map(renderMessage)}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>
            
            {/* 输入框 */}
            <div className="relative">
              <Textarea
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="输入您的消息..."
                className="resize-none p-4 pr-12"
                rows={3}
                disabled={generatingResponse}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
              />
              <div className="absolute right-2 bottom-2">
                {generatingResponse ? (
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={handleStopGeneration}
                    className="rounded-full"
                  >
                    <Loader2 className="h-5 w-5 animate-spin" />
                  </Button>
                ) : (
                  <Button
                    variant="default"
                    size="icon"
                    onClick={handleSendMessage}
                    disabled={!userInput.trim() || !sessionId}
                    className="rounded-full"
                  >
                    <Send className="h-5 w-5" />
                  </Button>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ChatPage; 