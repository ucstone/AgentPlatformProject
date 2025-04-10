import { Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import Layout from '@/components/layout'
import { AuthProvider } from '@/context/auth-context'
import { ProtectedRoute } from '@/components/protected-route'
import {
  Home,
  Dashboard,
  Chat,
  Text2SQL,
  KnowledgeBase,
  ContentCreation,
  Login,
  Register
} from '@/pages'

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/app"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="chat" element={<Chat />} />
          <Route path="text2sql" element={<Text2SQL />} />
          <Route path="knowledge" element={<KnowledgeBase />} />
          <Route path="content" element={<ContentCreation />} />
        </Route>
      </Routes>
      <Toaster />
    </AuthProvider>
  )
}

export default App
