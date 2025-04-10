import { useState } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuth } from '@/context/auth-context'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()

  // 获取重定向地址，默认为仪表盘
  const from = (location.state as any)?.from || '/app'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!email || !password) {
      return
    }
    
    setIsSubmitting(true)
    
    try {
      const success = await login(email, password)
      if (success) {
        // 登录成功，重定向到之前尝试访问的页面或仪表盘
        navigate(from, { replace: true })
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-md p-8 space-y-8 bg-card rounded-lg shadow-md">
        <div className="text-center">
          <h1 className="text-3xl font-bold">登录</h1>
          <p className="text-muted-foreground mt-2">
            登录您的智能体平台账号
          </p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="email">邮箱</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isSubmitting}
              placeholder="请输入您的邮箱"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">密码</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isSubmitting}
              placeholder="请输入您的密码"
            />
          </div>
          <Button 
            type="submit" 
            className="w-full"
            disabled={isSubmitting}
          >
            {isSubmitting ? '登录中...' : '登录'}
          </Button>
        </form>
        <div className="text-center text-sm">
          还没有账号？{' '}
          <Link to="/register" className="text-primary hover:underline">
            立即注册
          </Link>
        </div>
      </div>
    </div>
  )
} 