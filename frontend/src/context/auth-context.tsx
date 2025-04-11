import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, login as loginApi, register as registerApi, 
         getCurrentUser, saveToken, getToken, removeToken } from '@/services/auth';
import { useToast } from '@/components/ui/use-toast';

// 上下文类型
interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
}

// 创建上下文
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// 提供者组件
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { toast } = useToast();

  // 初始化 - 检查是否已登录
  useEffect(() => {
    const initAuth = async () => {
      const token = getToken();
      if (token) {
        try {
          const response = await getCurrentUser();
          if (response.data) {
            setUser(response.data);
          } else {
            // Token无效，清除它
            removeToken();
          }
        } catch (error) {
          // 处理错误
          removeToken();
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  /**
   * 用户登录
   */
  const login = async (email: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await loginApi({
        username: email,
        password: password
      });
      
      if (!response.data) {
        setError(response.message || '登录失败');
        toast({
          title: "登录失败",
          description: response.message || '登录失败',
          variant: "destructive",
        });
        setIsLoading(false);
        return false;
      }
      
      // 保存token
      if (response.data.access_token) {
        const token = response.data.access_token;
        saveToken(token);
        
        // 获取用户信息
        const userResponse = await getCurrentUser();
        if (userResponse.data) {
          setUser(userResponse.data);
          toast({
            title: "登录成功",
            description: `欢迎回来，${userResponse.data.email}`,
          });
          setIsLoading(false);
          return true;
        }
      }
      
      setError("获取用户信息失败");
      toast({
        title: "登录失败",
        description: "获取用户信息失败",
        variant: "destructive",
      });
      setIsLoading(false);
      return false;
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 
        typeof err === 'object' && err !== null ? 
          (err as any).message || JSON.stringify(err) : 
          "登录过程中发生错误";
      setError(errorMessage);
      toast({
        title: "登录失败",
        description: errorMessage,
        variant: "destructive",
      });
      setIsLoading(false);
      return false;
    }
  };

  /**
   * 用户注册
   */
  const register = async (email: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await registerApi({
        email,
        password
      });
      
      if (!response.data) {
        const errorMsg = typeof response.message === 'string' ? response.message : '注册失败';
        setError(errorMsg);
        toast({
          title: "注册失败",
          description: errorMsg,
          variant: "destructive",
        });
        setIsLoading(false);
        return false;
      }
      
      toast({
        title: "注册成功",
        description: "请登录您的账户",
      });
      
      setIsLoading(false);
      return true;
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 
        typeof err === 'object' && err !== null ? 
          (err as any).message || JSON.stringify(err) : 
          "注册过程中发生错误";
      setError(errorMessage);
      toast({
        title: "注册失败",
        description: errorMessage,
        variant: "destructive",
      });
      setIsLoading(false);
      return false;
    }
  };

  /**
   * 用户登出
   */
  const logout = () => {
    removeToken();
    setUser(null);
    toast({
      title: "已登出",
      description: "您已成功退出登录",
    });
    navigate('/');
  };

  const value = {
    user,
    isLoading,
    error,
    login,
    register,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// 自定义钩子
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth必须在AuthProvider内使用');
  }
  return context;
}; 