"use client"

import { useEffect, useRef } from "react"
import { useThree } from "@react-three/fiber"

interface WebGLContextHandlerProps {
  onContextLost: () => void
  onContextRestored: () => void
}

export default function WebGLContextHandler({ onContextLost, onContextRestored }: WebGLContextHandlerProps) {
  const { gl } = useThree()
  const initialized = useRef(false)

  useEffect(() => {
    if (initialized.current) return
    initialized.current = true

    const canvas = gl.domElement

    const handleContextLost = (event: Event) => {
      event.preventDefault()
      console.log("WebGL context lost")
      onContextLost()
    }

    const handleContextRestored = () => {
      console.log("WebGL context restored")
      onContextRestored()
    }

    canvas.addEventListener("webglcontextlost", handleContextLost)
    canvas.addEventListener("webglcontextrestored", handleContextRestored)

    return () => {
      canvas.removeEventListener("webglcontextlost", handleContextLost)
      canvas.removeEventListener("webglcontextrestored", handleContextRestored)
    }
  }, [gl, onContextLost, onContextRestored])

  return null
}
