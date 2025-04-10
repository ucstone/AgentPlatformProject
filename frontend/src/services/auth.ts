import { apiRequest, ApiResponse } from './api';

// 用户相关接口
export interface User {
  id: number;
  email: string;
  is_active: boolean;
}

// 登录响应
export interface LoginResponse {
  access_token: string;
  token_type: string;
}

// 登录请求参数
export interface LoginRequest {
  username: string; // 使用邮箱作为用户名
  password: string;
}

// 注册请求参数
export interface RegisterRequest {
  email: string;
  password: string;
}

/**
 * 用户登录
 * @param email 用户邮箱
 * @param password 密码
 * @returns 包含token的响应
 */
export async function login(email: string, password: string): Promise<ApiResponse<LoginResponse>> {
  // 创建表单数据 (FastAPI OAuth2PasswordRequestForm 需要表单格式)
  const formData = new URLSearchParams();
  formData.append('username', email); // OAuth2 默认使用username字段
  formData.append('password', password);

  // 直接使用fetch，避免apiRequest中的处理逻辑
  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });

    // 解析响应
    let data;
    try {
      data = await response.json();
    } catch (error) {
      data = await response.text();
    }

    if (!response.ok) {
      return {
        error: typeof data === 'object' && data.detail ? data.detail : 'API请求失败',
        status: response.status
      };
    }

    return {
      data,
      status: response.status
    };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : '网络请求失败',
      status: 0
    };
  }
}

/**
 * 用户注册
 * @param email 用户邮箱
 * @param password 密码
 * @returns 包含用户信息的响应
 */
export async function register(email: string, password: string): Promise<ApiResponse<User>> {
  return apiRequest<User>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

/**
 * 获取当前用户信息
 * @param token 访问令牌
 * @returns 包含用户信息的响应
 */
export async function getCurrentUser(token: string): Promise<ApiResponse<User>> {
  return apiRequest<User>('/auth/me', {
    token,
  });
}

/**
 * 保存令牌到本地存储
 * @param token 访问令牌
 */
export function saveToken(token: string): void {
  localStorage.setItem('token', token);
}

/**
 * 从本地存储获取令牌
 * @returns 访问令牌或null
 */
export function getToken(): string | null {
  return localStorage.getItem('token');
}

/**
 * 从本地存储移除令牌
 */
export function removeToken(): void {
  localStorage.removeItem('token');
} 