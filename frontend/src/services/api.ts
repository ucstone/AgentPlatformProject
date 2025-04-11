import axios, { AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig, AxiosError } from 'axios';
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
  const { data } = response;
  response.data = {
    success: true,
    data: data.data || data,
    message: data.message
  };
  return response;
};

// 错误拦截器
const errorInterceptor = (error: AxiosError) => {
  const { response } = error;
  if (response) {
    const { data } = response as { data: any };
    response.data = {
      success: false,
      error: data.message || '请求失败',
      message: data.message
    };
  } else {
    error.response = {
      data: {
        success: false,
        error: '网络错误',
        message: '网络错误'
      },
      status: 500,
      statusText: 'Network Error',
      headers: {},
      config: error.config
    } as AxiosResponse;
  }
  return Promise.reject(error);
};

// 为两个实例添加拦截器
baseInstance.interceptors.request.use(requestInterceptor);
baseInstance.interceptors.response.use(responseInterceptor, errorInterceptor);
llmConfigInstance.interceptors.request.use(requestInterceptor);
llmConfigInstance.interceptors.response.use(responseInterceptor, errorInterceptor);

// API 响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
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
        success: true,
        data: response.data.data,
        message: response.data.message
      };
    }
    
    return {
      success: false,
      data: undefined as T,
      message: response.data?.detail || '请求失败'
    };
    
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.data) {
      return {
        success: false,
        data: undefined as T,
        message: error.response.data.detail || '请求失败'
      };
    }
    
    return {
      success: false,
      data: undefined as T,
      message: '请求失败'
    };
  }
}; 