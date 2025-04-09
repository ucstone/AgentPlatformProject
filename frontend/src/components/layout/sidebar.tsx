import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import {
  MessageSquare,
  Database,
  BookOpen,
  FileText,
  Home
} from 'lucide-react'

const routes = [
  {
    label: '首页',
    icon: Home,
    href: '/',
  },
  {
    label: '智能客服',
    icon: MessageSquare,
    href: '/chat',
  },
  {
    label: 'Text2SQL',
    icon: Database,
    href: '/text2sql',
  },
  {
    label: '知识库',
    icon: BookOpen,
    href: '/knowledge',
  },
  {
    label: '文案创作',
    icon: FileText,
    href: '/content',
  },
]

export default function Sidebar() {
  const location = useLocation()

  return (
    <div className="space-y-4 py-4 flex flex-col h-full bg-[#111827] text-white">
      <div className="px-3 py-2 flex-1">
        <Link to="/" className="flex items-center pl-3 mb-14">
          <h1 className="text-2xl font-bold">
            智能体平台
          </h1>
        </Link>
        <div className="space-y-1">
          {routes.map((route) => (
            <Link
              key={route.href}
              to={route.href}
              className={cn(
                "text-sm group flex p-3 w-full justify-start font-medium cursor-pointer hover:text-white hover:bg-white/10 rounded-lg transition",
                location.pathname === route.href ? "text-white bg-white/10" : "text-zinc-400"
              )}
            >
              <div className="flex items-center flex-1">
                <route.icon className="h-5 w-5 mr-3" />
                {route.label}
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
} 