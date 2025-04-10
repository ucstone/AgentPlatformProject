// API 基础封装
// 配置API基础URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// 请求选项接口
interface RequestOptions extends RequestInit {
  token?: string;
}

// 响应类型
export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  status: number;
}

/**
 * 发送API请求
 * @param endpoint API端点
 * @param options 请求选项
 * @returns Promise<ApiResponse>
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<ApiResponse<T>> {
  const { token, ...customOptions } = options;
  
  // 设置headers
  const headers = new Headers(customOptions.headers || {});
  
  // 只有在没有设置Content-Type的情况下才设置默认值
  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  
  // 如果有token则添加到headers
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  try {
    // 发送请求
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...customOptions,
      headers,
    });
    
    // 尝试解析为JSON
    let data;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }
    
    // 处理非2xx响应
    if (!response.ok) {
      return {
        error: data.detail || 'API请求失败',
        status: response.status
      };
    }
    
    // 返回成功响应
    return {
      data,
      status: response.status
    };
  } catch (error) {
    // 处理网络错误
    return {
      error: error instanceof Error ? error.message : '网络请求失败',
      status: 0
    };
  }
} 