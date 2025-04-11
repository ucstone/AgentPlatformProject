import { apiRequest, ApiResponse } from './api';

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at?: string;
}

export interface StreamChunk {
  chunk?: string;
  session_id?: string;
  done?: boolean;
  error?: string;
}

// 获取会话列表
export const getSessions = async (): Promise<ApiResponse<Session[]>> => {
  return await apiRequest<Session[]>('/chat/sessions', 'GET', undefined, undefined, true);
};

// 创建新会话
export const createSession = async (title: string): Promise<ApiResponse<Session>> => {
  return await apiRequest<Session>('/chat/sessions', 'POST', { title }, undefined, true);
};

// 更新会话
export const updateSession = async (id: string, title: string): Promise<ApiResponse<Session>> => {
  return await apiRequest<Session>(`/chat/sessions/${id}`, 'PUT', { title }, undefined, true);
};

// 删除会话
export const deleteSession = async (id: string): Promise<ApiResponse<null>> => {
  return await apiRequest<null>(`/chat/sessions/${id}`, 'DELETE', undefined, undefined, true);
};

// 获取会话消息
export const getMessages = async (sessionId: string): Promise<ApiResponse<Message[]>> => {
  if (!sessionId) {
    return {
      success: false,
      data: [],
      message: '会话ID不能为空'
    };
  }
  
  return await apiRequest<Message[]>(`/chat/sessions/${sessionId}/messages`, 'GET', undefined, undefined, true);
};

// 发送消息
export const sendMessage = async (sessionId: string, content: string): Promise<ApiResponse<Message>> => {
  return await apiRequest<Message>(`/chat/sessions/${sessionId}/messages`, 'POST', { content }, undefined, true);
};

// 以流式方式发送消息
export const sendMessageStream = async (
  content: string, 
  sessionId: string | undefined,
  onChunk: (chunk: StreamChunk) => void,
  onError: (error: Error) => void
): Promise<void> => {
  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
    const endpoint = `${baseUrl}/chat/stream`;
    
    // 获取认证token
    const token = localStorage.getItem('token');
    
    // 创建请求头
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    // 创建 AbortController，用于超时中断
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30秒超时
    
    // 发送请求
    const response = await fetch(endpoint, {
      method: 'POST',
      headers,
      body: JSON.stringify({ 
        message: content, 
        session_id: sessionId 
      }),
      signal: controller.signal
    });
    
    // 清除超时定时器
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      // 尝试读取错误详情
      let errorDetail = '';
      try {
        const errorData = await response.json();
        errorDetail = errorData.detail || `HTTP error! status: ${response.status}`;
      } catch (e) {
        errorDetail = `HTTP error! status: ${response.status}`;
      }
      throw new Error(errorDetail);
    }
    
    // 创建事件流读取器
    const reader = response.body?.getReader();
    
    if (!reader) {
      throw new Error('无法创建流读取器');
    }
    
    // 创建文本解码器
    const decoder = new TextDecoder();
    
    // 设置读取超时
    let noDataTimer: NodeJS.Timeout | null = null;
    const resetNoDataTimer = () => {
      if (noDataTimer) clearTimeout(noDataTimer);
      noDataTimer = setTimeout(() => {
        console.warn('流式数据接收超时');
        reader.cancel(); // 取消流读取
        onError(new Error('接收数据超时，请检查网络连接'));
      }, 15000); // 15秒无数据则超时
    };
    
    resetNoDataTimer(); // 初始化计时器
    
    // 读取流数据
    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          if (noDataTimer) clearTimeout(noDataTimer);
          break;
        }
        
        // 重置无数据计时器
        resetNoDataTimer();
        
        // 解码二进制数据
        const decodedChunk = decoder.decode(value, { stream: true });
        
        // 按SSE格式分割数据
        const lines = decodedChunk
          .split('\n\n')
          .filter(line => line.trim().startsWith('data:'));
        
        // 处理每一行数据
        for (const line of lines) {
          try {
            const jsonStr = line.replace('data:', '').trim();
            const chunkData = JSON.parse(jsonStr) as StreamChunk;
            
            // 检查是否有错误
            if (chunkData.error) {
              console.error('服务器报告错误:', chunkData.error);
              onError(new Error(chunkData.error));
              return;
            }
            
            onChunk(chunkData);
          } catch (e) {
            console.error('解析流数据失败:', e);
          }
        }
      }
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.warn('流式请求被中止');
        onError(new Error('请求超时'));
      } else {
        console.error('流式读取错误:', error);
        onError(error instanceof Error ? error : new Error(String(error)));
      }
    } finally {
      if (noDataTimer) clearTimeout(noDataTimer);
    }
  } catch (error) {
    console.error('流式请求失败:', error);
    onError(error instanceof Error ? error : new Error(String(error)));
  }
};

// 获取可用的模型提供商
export const getAvailableProviders = async (): Promise<ApiResponse<any>> => {
  return await apiRequest<any>('/llm-config/providers', 'GET');
};

// 停止消息生成
export const stopMessageGeneration = async (sessionId: string): Promise<ApiResponse<any>> => {
  return await apiRequest<any>('/chat/stop', 'POST', { session_id: sessionId }, undefined, true);
};