import { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/context/auth-context';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

/**
 * 保护路由组件，确保只有已登录用户才能访问
 */
export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, isLoading } = useAuth();
  const location = useLocation();

  // 如果正在加载，显示空白或加载指示器
  if (isLoading) {
    return <div className="flex h-screen items-center justify-center">加载中...</div>;
  }

  // 如果用户未登录，重定向到登录页面并保存当前URL
  if (!user) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  // 用户已登录，显示子组件
  return <>{children}</>;
} 