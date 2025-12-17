"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { getUser } from "@/lib/api"

interface User {
  id: number
  name: string
}

interface AuthContextType {
  user: User | null
  login: (userId: number) => Promise<boolean>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Load user from localStorage on mount
  useEffect(() => {
    const storedUserId = localStorage.getItem("movieRec_userId")
    if (storedUserId) {
      const userId = Number.parseInt(storedUserId)
      // Verify user exists in database
      getUser(userId)
        .then((userData) => {
          setUser({
            id: userData.userId,
            name: userData.username || `User ${userData.userId}`
          })
        })
        .catch(() => {
          // User not found, clear storage
          localStorage.removeItem("movieRec_userId")
        })
        .finally(() => setIsLoading(false))
    } else {
      setIsLoading(false)
    }
  }, [])

  const login = async (userId: number): Promise<boolean> => {
    try {
      const userData = await getUser(userId)
      setUser({
        id: userData.userId,
        name: userData.username || `User ${userData.userId}`
      })
      localStorage.setItem("movieRec_userId", userId.toString())
      return true
    } catch {
      return false
    }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem("movieRec_userId")
  }

  return <AuthContext.Provider value={{ user, login, logout, isLoading }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
