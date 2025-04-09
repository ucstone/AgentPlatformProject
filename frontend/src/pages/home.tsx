import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'

export default function Home() {
  return (
    <div className="container mx-auto py-10 text-center">
      <h1 className="text-5xl font-extrabold mb-4 tracking-tight lg:text-6xl">
        欢迎使用 智能体综合应用平台
      </h1>
      <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
        一个集成了多种先进智能体能力的企业级平台，旨在赋能您的业务，提升效率，并开启智能化新篇章。
      </p>

      <div className="flex justify-center gap-4 mb-12">
        <Button asChild size="lg">
          <Link to="/register">立即注册</Link>
        </Button>
        <Button asChild variant="outline" size="lg">
          <Link to="/login">登录</Link>
        </Button>
      </div>

      <h2 className="text-3xl font-bold mb-8">平台核心功能</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 text-left">
        <div className="p-6 bg-card rounded-lg shadow-md border">
          <h3 className="text-xl font-semibold mb-3">智能客服</h3>
          <p className="text-muted-foreground">
            提供 24/7 智能化的客户服务支持，快速响应并解决客户需求。
          </p>
        </div>
        <div className="p-6 bg-card rounded-lg shadow-md border">
          <h3 className="text-xl font-semibold mb-3">Text2SQL 数据分析</h3>
          <p className="text-muted-foreground">
            通过自然语言生成 SQL 查询，让数据分析变得前所未有的简单直观。
          </p>
        </div>
        <div className="p-6 bg-card rounded-lg shadow-md border">
          <h3 className="text-xl font-semibold mb-3">知识库问答</h3>
          <p className="text-muted-foreground">
            构建智能化的企业知识库，员工可以快速、准确地获取所需信息。
          </p>
        </div>
        <div className="p-6 bg-card rounded-lg shadow-md border">
          <h3 className="text-xl font-semibold mb-3">自动化内容创作</h3>
          <p className="text-muted-foreground">
            智能生成营销文案、报告摘要、邮件草稿等多种内容，提高创作效率。
          </p>
        </div>
      </div>
    </div>
  )
} 