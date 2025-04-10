import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuth } from '@/context/auth-context'
import { useToast } from '@/components/ui/use-toast'

export default function Register() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const navigate = useNavigate()
  const { register } = useAuth()
  const { toast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // 表单验证
    if (!email || !password || !confirmPassword) {
      return
    }
    
    // 检查密码是否匹配
    if (password !== confirmPassword) {
      toast({
        title: "密码不匹配",
        description: "请确保两次输入的密码相同",
        variant: "destructive",
      })
      return
    }
    
    // 检查密码长度
    if (password.length < 8) {
      toast({
        title: "密码太短",
        description: "密码长度至少需要8个字符",
        variant: "destructive",
      })
      return
    }
    
    setIsSubmitting(true)
    
    try {
      const success = await register(email, password)
      if (success) {
        // 注册成功，重定向到登录页面
        navigate('/login')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-md p-8 space-y-8 bg-card rounded-lg shadow-md">
        <div className="text-center">
          <h1 className="text-3xl font-bold">注册账号</h1>
          <p className="text-muted-foreground mt-2">
            创建您的智能体平台账号
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
              placeholder="请输入至少8位密码"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="confirmPassword">确认密码</Label>
            <Input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              disabled={isSubmitting}
              placeholder="请再次输入密码"
            />
          </div>
          <Button 
            type="submit" 
            className="w-full"
            disabled={isSubmitting}
          >
            {isSubmitting ? '注册中...' : '注册'}
          </Button>
        </form>
        <div className="text-center text-sm">
          已有账号？{' '}
          <Link to="/login" className="text-primary hover:underline">
            立即登录
          </Link>
        </div>
      </div>
    </div>
  )
} 