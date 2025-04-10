import { apiRequest } from './api';

// 用户相关接口
export interface User {
  id: number;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
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

export interface LoginData {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

/**
 * 用户登录
 * @param email 用户邮箱
 * @param password 密码
 * @returns 包含token的响应
 */
export const login = async (data: LoginData) => {
  const formData = new FormData();
  formData.append('username', data.username);
  formData.append('password', data.password);
  
  return apiRequest<Token>('/auth/login', 'POST', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }, true);
};

/**
 * 用户注册
 * @param email 用户邮箱
 * @param password 密码
 * @returns 包含用户信息的响应
 */
export const register = async (data: RegisterData) => {
  return apiRequest<User>('/auth/register', 'POST', data, undefined, true);
};

/**
 * 获取当前用户信息
 * @param token 访问令牌
 * @returns 包含用户信息的响应
 */
export const getCurrentUser = async () => {
  return apiRequest<User>('/auth/me', 'GET', undefined, undefined, true);
};

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