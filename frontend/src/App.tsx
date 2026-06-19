import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'

import { Login } from '@/pages/Login'
import { Signup } from '@/pages/Signup'
import { Chats } from '@/pages/Chats'
import { ProtectedRoute } from '@/components/ProtectedRoute'

function App() {
  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        
        {/* Protected routes */}
        <Route 
          path="/chats" 
          element={
            <ProtectedRoute>
              <Chats />
            </ProtectedRoute>
          } 
        />
        
        {/* Redirect to login if no match */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  )
}

export default App