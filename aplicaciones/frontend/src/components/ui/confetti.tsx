import React, { useEffect, useRef } from "react"
import { cn } from "../../utilidades/cn"

interface ConfettiProps {
  active?: boolean
  config?: {
    angle?: number
    spread?: number
    startVelocity?: number
    elementCount?: number
    dragFriction?: number
    duration?: number
    stagger?: number
    width?: string
    height?: string
    perspective?: string
    colors?: string[]
  }
  className?: string
}

export function Confetti({
  active = false,
  config = {},
  className,
}: ConfettiProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number>()

  const defaultConfig = {
    angle: 90,
    spread: 45,
    startVelocity: 45,
    elementCount: 50,
    dragFriction: 0.1,
    duration: 3000,
    stagger: 0,
    width: "10px",
    height: "10px",
    perspective: "500px",
    colors: ["#a78bfa", "#34d399", "#fbbf24", "#f87171", "#60a5fa"],
    ...config,
  }

  useEffect(() => {
    if (!active || !canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    canvas.width = window.innerWidth
    canvas.height = window.innerHeight

    const particles: Array<{
      x: number
      y: number
      vx: number
      vy: number
      color: string
      life: number
      maxLife: number
    }> = []

    const createParticle = (x: number, y: number) => {
      const angle = (defaultConfig.angle + (Math.random() - 0.5) * defaultConfig.spread) * (Math.PI / 180)
      const velocity = defaultConfig.startVelocity * (0.5 + Math.random() * 0.5)
      
      return {
        x,
        y,
        vx: Math.cos(angle) * velocity,
        vy: Math.sin(angle) * velocity,
        color: defaultConfig.colors[Math.floor(Math.random() * defaultConfig.colors.length)],
        life: 0,
        maxLife: defaultConfig.duration,
      }
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Create new particles
      if (particles.length < defaultConfig.elementCount) {
        particles.push(createParticle(canvas.width / 2, canvas.height / 2))
      }

      // Update and draw particles
      for (let i = particles.length - 1; i >= 0; i--) {
        const particle = particles[i]
        
        particle.x += particle.vx
        particle.y += particle.vy
        particle.vy += 0.5 // gravity
        particle.vx *= (1 - defaultConfig.dragFriction)
        particle.vy *= (1 - defaultConfig.dragFriction)
        particle.life += 16

        const alpha = 1 - (particle.life / particle.maxLife)
        
        ctx.save()
        ctx.globalAlpha = alpha
        ctx.fillStyle = particle.color
        ctx.fillRect(particle.x, particle.y, 4, 4)
        ctx.restore()

        if (particle.life >= particle.maxLife || particle.y > canvas.height) {
          particles.splice(i, 1)
        }
      }

      if (particles.length > 0) {
        animationRef.current = requestAnimationFrame(animate)
      }
    }

    animate()

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [active, defaultConfig])

  if (!active) return null

  return (
    <canvas
      ref={canvasRef}
      className={cn("fixed inset-0 pointer-events-none z-50", className)}
      style={{
        width: "100vw",
        height: "100vh",
      }}
    />
  )
}

