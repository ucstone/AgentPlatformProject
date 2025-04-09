import { Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import Layout from '@/components/layout'
import {
  Home,
  Chat,
  Text2SQL,
  KnowledgeBase,
  ContentCreation,
  Login,
  Register
} from '@/pages'

function App() {
  return (
    <>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="chat" element={<Chat />} />
          <Route path="text2sql" element={<Text2SQL />} />
          <Route path="knowledge" element={<KnowledgeBase />} />
          <Route path="content" element={<ContentCreation />} />
        </Route>
      </Routes>
      <Toaster />
    </>
  )
}

export default App
