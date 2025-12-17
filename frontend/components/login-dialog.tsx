"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useAuth } from "@/contexts/auth-context"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { LogIn, User, Loader2 } from "lucide-react"

interface LoginDialogProps {
  trigger?: React.ReactNode
}

// Sample user IDs for quick login (from MongoDB data)
const sampleUsers = [
  { id: 1, name: "User 1" },
  { id: 2, name: "User 2" },
  { id: 3, name: "User 3" },
  { id: 10, name: "User 10" },
  { id: 100, name: "User 100" },
]

export function LoginDialog({ trigger }: LoginDialogProps) {
  const { login } = useAuth()
  const [userId, setUserId] = useState("")
  const [error, setError] = useState("")
  const [open, setOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleLogin = async () => {
    const id = Number.parseInt(userId)
    if (isNaN(id) || id <= 0) {
      setError("Vui lòng nhập User ID hợp lệ (số dương)")
      return
    }

    setIsLoading(true)
    setError("")

    try {
      const success = await login(id)
      if (success) {
        setOpen(false)
        setUserId("")
        setError("")
      } else {
        setError("Không tìm thấy User ID này trong hệ thống")
      }
    } catch {
      setError("Lỗi kết nối. Vui lòng thử lại.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleQuickLogin = async (id: number) => {
    setIsLoading(true)
    try {
      const success = await login(id)
      if (success) {
        setOpen(false)
        setUserId("")
        setError("")
      } else {
        setError(`User ID ${id} không tồn tại`)
      }
    } catch {
      setError("Lỗi kết nối")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button variant="outline" size="sm" className="gap-2 bg-transparent">
            <LogIn className="h-4 w-4" />
            Đăng nhập
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Đăng nhập</DialogTitle>
          <DialogDescription>Nhập User ID của bạn để đăng nhập vào hệ thống gợi ý phim</DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Manual Input */}
          <div className="space-y-2">
            <Label htmlFor="userId">User ID</Label>
            <div className="flex gap-2">
              <Input
                id="userId"
                type="number"
                placeholder="Nhập User ID (1-6747)..."
                value={userId}
                onChange={(e) => {
                  setUserId(e.target.value)
                  setError("")
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !isLoading) handleLogin()
                }}
                disabled={isLoading}
              />
              <Button onClick={handleLogin} disabled={isLoading}>
                {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Đăng nhập"}
              </Button>
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
          </div>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 text-muted-foreground">Hoặc chọn nhanh</span>
            </div>
          </div>

          {/* Quick Select Users */}
          <div className="grid grid-cols-1 gap-2">
            {sampleUsers.map((sampleUser) => (
              <Button
                key={sampleUser.id}
                variant="outline"
                className="justify-start gap-3 bg-transparent"
                onClick={() => handleQuickLogin(sampleUser.id)}
                disabled={isLoading}
              >
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                  <User className="h-4 w-4 text-primary" />
                </div>
                <div className="text-left">
                  <p className="font-medium">{sampleUser.name}</p>
                  <p className="text-xs text-muted-foreground">ID: {sampleUser.id}</p>
                </div>
              </Button>
            ))}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
