import { NavLink } from 'react-router-dom'
import { Home, MessageSquare, Database, Book, FileText, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'
import { buttonVariants } from '@/components/ui/button'

const navItems = [
  { name: '仪表盘', href: '/app', icon: Home, exact: true },
  { name: '智能客服', href: '/app/chat', icon: MessageSquare },
  { name: 'Text2SQL', href: '/app/text2sql', icon: Database },
  { name: '知识库', href: '/app/knowledge', icon: Book },
  { name: '文案创作', href: '/app/content', icon: FileText },
]

const settingsItems = [
  { name: '模型设置', href: '/app/model-settings', icon: Settings },
]

export default function Sidebar() {
  return (
    <div className="w-64 border-r bg-background p-4 flex flex-col">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">智能体平台</h1>
      </div>
      <nav className="flex-1 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            end={item.exact}
            className={({ isActive }) =>
              cn(
                buttonVariants({ variant: isActive ? 'secondary' : 'ghost' }),
                'w-full justify-start'
              )
            }
          >
            <item.icon className="mr-2 h-4 w-4" />
            {item.name}
          </NavLink>
        ))}
      </nav>
      
      <div className="border-t mt-4 pt-4">
        <h2 className="text-xs uppercase tracking-wider text-muted-foreground mb-2 px-2">设置</h2>
        <nav className="space-y-1">
          {settingsItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              end={item.exact}
              className={({ isActive }) =>
                cn(
                  buttonVariants({ variant: isActive ? 'secondary' : 'ghost' }),
                  'w-full justify-start'
                )
              }
            >
              <item.icon className="mr-2 h-4 w-4" />
              {item.name}
            </NavLink>
          ))}
        </nav>
      </div>
    </div>
  )
} 