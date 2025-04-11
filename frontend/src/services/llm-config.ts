import { apiRequest, ApiResponse } from './api';
import { toast } from '@/components/ui/use-toast';

// 请求配置
const REQUEST_CONFIG = {
  timeout: 10000, // 10秒超时
  maxRetries: 2,  // 最大重试次数
  retryDelay: 1000, // 重试延迟1秒
};

// 错误处理函数
const handleError = (error: any, operation: string) => {
  console.error(`${operation}失败:`, error);
  const errorMessage = error.response?.data?.detail || error.message || '未知错误';
  toast({
    title: '操作失败',
    description: errorMessage,
    variant: 'destructive',
  });
  throw error;
};

// 重试函数
const retry = async <T>(
  fn: () => Promise<T>,
  retries = REQUEST_CONFIG.maxRetries,
  delay = REQUEST_CONFIG.retryDelay
): Promise<T> => {
  try {
    return await fn();
  } catch (error) {
    if (retries > 0) {
      await new Promise(resolve => setTimeout(resolve, delay));
      return await retry(fn, retries - 1, delay);
    }
    throw error;
  }
};

export interface LLMConfigModel {
  id: number;
  name: string;
  provider: string;
  model_name: string;
  api_key: string | null;
  api_base_url: string | null;
  is_default: boolean;
  user_id: number;
}

export interface LLMConfigCreateModel {
  name: string;
  provider: string;
  model_name: string;
  api_key?: string;
  api_base_url?: string;
  is_default: boolean;
}

export interface LLMConfigUpdateModel {
  name?: string;
  provider?: string;
  model_name?: string;
  api_key?: string;
  api_base_url?: string;
  is_default?: boolean;
}

export interface ProvidersData {
  providers: Record<string, string[]>;
  current: {
    provider: string;
    model: string;
  };
}

/**
 * 获取可用的LLM提供商和模型列表
 */
export const getAvailableProviders = async (): Promise<ApiResponse<ProvidersData>> => {
  return await retry(async () => {
    try {
      const response = await apiRequest<ProvidersData>(
        '/providers',
        'GET',
        undefined,
        { timeout: REQUEST_CONFIG.timeout }
      );
      return response;
    } catch (error) {
      handleError(error, '获取提供商列表');
      return {
        data: null,
        message: '获取提供商列表失败',
        success: false
      };
    }
  });
};

/**
 * 获取当前用户的所有LLM配置
 */
export const getConfigs = async (): Promise<ApiResponse<LLMConfigModel[]>> => {
  return await retry(async () => {
    try {
      const response = await apiRequest<LLMConfigModel[]>(
        '',  // 空路径，因为 baseURL 已经包含了 /llm-config
        'GET',
        undefined,
        { timeout: REQUEST_CONFIG.timeout }
      );
      return response;
    } catch (error) {
      handleError(error, '获取配置列表');
      return {
        data: null,
        message: '获取配置列表失败',
        success: false
      };
    }
  });
};

/**
 * 创建新的LLM配置
 */
export const createConfig = async (config: LLMConfigCreateModel): Promise<ApiResponse<LLMConfigModel>> => {
  return await retry(async () => {
    try {
      const response = await apiRequest<LLMConfigModel>(
        '',  // 空路径，因为 baseURL 已经包含了 /llm-config
        'POST',
        config,
        { timeout: REQUEST_CONFIG.timeout }
      );
      toast({
        title: '创建成功',
        description: `模型配置「${config.name}」已创建`,
      });
      return response;
    } catch (error) {
      handleError(error, '创建配置');
      return {
        data: null,
        message: '创建配置失败',
        success: false
      };
    }
  });
};

/**
 * 获取当前用户的默认LLM配置
 */
export const getDefaultConfig = async (): Promise<ApiResponse<LLMConfigModel>> => {
  return await retry(async () => {
    try {
      const response = await apiRequest<LLMConfigModel>(
        '/default',
        'GET',
        undefined,
        { timeout: REQUEST_CONFIG.timeout }
      );
      return response;
    } catch (error) {
      handleError(error, '获取默认配置');
      return {
        data: null,
        message: '获取默认配置失败',
        success: false
      };
    }
  });
};

/**
 * 获取特定的LLM配置
 */
export const getConfig = async (configId: number): Promise<ApiResponse<LLMConfigModel>> => {
  return await retry(async () => {
    try {
      const response = await apiRequest<LLMConfigModel>(
        `/${configId}`,
        'GET',
        undefined,
        { timeout: REQUEST_CONFIG.timeout }
      );
      return response;
    } catch (error) {
      handleError(error, '获取配置详情');
      return {
        data: null,
        message: '获取配置详情失败',
        success: false
      };
    }
  });
};

/**
 * 更新LLM配置
 */
export const updateConfig = async (configId: number, config: LLMConfigUpdateModel): Promise<ApiResponse<LLMConfigModel>> => {
  return await retry(async () => {
    try {
      const response = await apiRequest<LLMConfigModel>(
        `/${configId}`,
        'PUT',
        config,
        { timeout: REQUEST_CONFIG.timeout }
      );
      toast({
        title: '更新成功',
        description: `模型配置已更新`,
      });
      return response;
    } catch (error) {
      handleError(error, '更新配置');
      return {
        data: null,
        message: '更新配置失败',
        success: false
      };
    }
  });
};

/**
 * 删除LLM配置
 */
export const deleteConfig = async (configId: number): Promise<ApiResponse<null>> => {
  return await retry(async () => {
    try {
      const response = await apiRequest<null>(
        `/${configId}`,
        'DELETE',
        undefined,
        { timeout: REQUEST_CONFIG.timeout }
      );
      toast({
        title: '删除成功',
        description: '模型配置已删除',
      });
      return response;
    } catch (error) {
      handleError(error, '删除配置');
      return {
        data: null,
        message: '删除配置失败',
        success: false
      };
    }
  });
} 