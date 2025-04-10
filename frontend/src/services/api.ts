import axios, { AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { toast } from '@/components/ui/use-toast';

// 基础配置
const baseConfig = {
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
};

// 创建基础 axios 实例
const baseInstance = axios.create({
  baseURL: (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1').replace(/\/$/, ''),
  ...baseConfig,
});

// 创建 LLM 配置相关的 axios 实例
const llmConfigInstance = axios.create({
  baseURL: `${(import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '')}/llm-config`,
  ...baseConfig,
});

// 添加调试信息
console.log("Base API URL:", baseInstance.defaults.baseURL);
console.log("LLM Config API URL:", llmConfigInstance.defaults.baseURL);

// 请求拦截器
const requestInterceptor = (config: InternalAxiosRequestConfig) => {
  console.log('请求配置:', {
    url: config.url,
    method: config.method,
    headers: config.headers,
    data: config.data
  });
  
  const token = localStorage.getItem('token');
  if (token) {
    config.headers = config.headers || {};
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
};

// 响应拦截器
const responseInterceptor = (response: AxiosResponse) => {
  console.log('响应数据:', {
    status: response.status,
    headers: response.headers,
    data: response.data
  });
  return response;
};

const errorInterceptor = (error: any) => {
  console.error('响应错误详情:', {
    message: error.message,
    code: error.code,
    config: error.config,
    response: error.response
  });
  
  // 处理错误响应
  const { response } = error;
  if (response) {
    // 根据状态码处理不同错误
    switch (response.status) {
      case 401:
        toast({
          title: '登录失效',
          description: '请重新登录',
          variant: 'destructive',
        });
        // 可以在这里处理登出逻辑
        localStorage.removeItem('token');
        window.location.href = '/login';
        break;
      case 403:
        toast({
          title: '无权限',
          description: '您没有权限执行此操作',
          variant: 'destructive',
        });
        break;
      case 422:
        toast({
          title: '请求数据错误',
          description: response.data?.detail || '请求数据格式不正确',
          variant: 'destructive',
        });
        break;
      case 500:
        toast({
          title: '服务器错误',
          description: '服务器发生错误，请稍后再试',
          variant: 'destructive',
        });
        break;
      default:
        toast({
          title: '请求失败',
          description: typeof response.data?.message === 'string' ? 
            response.data.message : 
            typeof response.data?.detail === 'string' ? 
              response.data.detail : 
              '未知错误',
          variant: 'destructive',
        });
    }
  } else {
    // 网络错误
    toast({
      title: '网络错误',
      description: error.message || '网络连接失败，请检查您的网络设置',
      variant: 'destructive',
    });
  }
  
  return Promise.reject(error);
};

// 为两个实例添加拦截器
baseInstance.interceptors.request.use(requestInterceptor);
baseInstance.interceptors.response.use(responseInterceptor, errorInterceptor);
llmConfigInstance.interceptors.request.use(requestInterceptor);
llmConfigInstance.interceptors.response.use(responseInterceptor, errorInterceptor);

export interface ApiResponse<T> {
  data: T | null;
  message?: string;
  status?: number;
  success?: boolean;
}

// 通用请求方法
export const apiRequest = async <T>(
  url: string,
  method: string,
  data?: any,
  config?: AxiosRequestConfig,
  useBaseInstance: boolean = false
): Promise<ApiResponse<T>> => {
  const instance = useBaseInstance ? baseInstance : llmConfigInstance;
  
  try {
    const requestConfig: AxiosRequestConfig = {
      url,
      method,
      ...config
    };

    // 处理 FormData
    if (data instanceof FormData) {
      requestConfig.data = data;
    } else {
      requestConfig.data = method.toUpperCase() !== 'GET' ? data : undefined;
      requestConfig.params = method.toUpperCase() === 'GET' ? data : undefined;
    }
    
    const response = await instance(requestConfig);
    
    // 如果响应状态码是2xx，则认为请求成功
    if (response.status >= 200 && response.status < 300) {
      return {
        data: response.data,
        message: response.data?.message,
        status: response.status,
        success: true
      };
    }
    
    return {
      data: null,
      message: response.data?.detail || '请求失败',
      status: response.status,
      success: false
    };
    
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.data) {
      return {
        data: null,
        message: error.response.data.detail || '请求失败',
        status: error.response.status,
        success: false
      };
    }
    
    return {
      data: null,
      message: '请求失败',
      success: false
    };
  }
}; 