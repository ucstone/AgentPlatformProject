import { Outlet } from 'react-router-dom'
import { ThemeProvider } from '@/components/theme-provider'
import Header from './header'
import Sidebar from './sidebar'

export default function Layout() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <div className="flex h-screen bg-background">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-y-auto p-4">
            <Outlet />
          </main>
        </div>
      </div>
    </ThemeProvider>
  )
} 