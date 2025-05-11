"use client"

import { useState, useEffect, useRef } from "react"
import { Canvas } from "@react-three/fiber"
import { OrbitControls } from "@react-three/drei"
import SimulationControls from "./simulation-controls"
import UrbanEnvironment from "./urban-environment"
import AgentSystem from "./agent-system"
import AboutProject from "./about-project"
import ErrorBoundary from "./error-boundary"
import type { SimulationSettings } from "../lib/types"

// Corregir los tipos de las propiedades de estilo
const styles = {
  simulatorLayout: {
    display: "flex",
    width: "100%",
    height: "100%",
  },
  mapContainer: {
    flex: 1,
    position: "relative" as const,
    height: "100%",
    display: "flex",
    flexDirection: "column" as const,
  },
  mapCanvasContainer: {
    flex: 1,
    width: "100%",
    position: "relative" as const,
  },
  mapControls: {
    position: "absolute" as const,
    bottom: 0,
    left: 0,
    width: "calc(100% - 320px)",
    height: "60px",
    backgroundColor: "#f9fafb",
    borderTop: "1px solid #e5e7eb",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 10,
  },
  controlsButtons: {
    display: "flex",
    gap: "1rem",
    flexWrap: "wrap" as const,
    justifyContent: "center",
  },
  button: {
    padding: "0.75rem 1.25rem",
    fontSize: "1rem",
    borderRadius: "0.375rem",
    fontWeight: 600,
    cursor: "pointer",
    border: "none",
    color: "white",
  },
  blueButton: {
    backgroundColor: "#3b82f6",
  },
  greenButton: {
    backgroundColor: "#10b981",
  },
  redButton: {
    backgroundColor: "#ef4444",
  },
  grayButton: {
    backgroundColor: "#6b7280",
  },
  yellowButton: {
    backgroundColor: "#f59e0b",
  },
  disabledButton: {
    backgroundColor: "#9ca3af",
    cursor: "not-allowed",
  },
}

export default function InlineStyleCrowdSimulator() {
  const [startPoint, setStartPoint] = useState<[number, number] | null>(null)
  const [meetingPoint, setMeetingPoint] = useState<[number, number] | null>(null)
  const [isSimulationRunning, setIsSimulationRunning] = useState(false)
  const [blockedAreas, setBlockedAreas] = useState<[number, number][]>([])
  const [standingCount, setStandingCount] = useState(0)
  const [fallenCount, setFallenCount] = useState(0)
  const [temperatureFallenCount, setTemperatureFallenCount] = useState(0)
  const [isBlockingMode, setIsBlockingMode] = useState(false)
  const [webGLError, setWebGLError] = useState(false)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  const [settings, setSettings] = useState<SimulationSettings>({
    desiredSpeed: 1.0,
    showFlow: true,
    showFallen: true,
    maxAgents: 50,
    temperature: 25, // Default temperature in Celsius
    showTemperatureFallen: true,
  })

  // Setup WebGL context loss handlers
  useEffect(() => {
    const handleContextLost = (event: Event) => {
      event.preventDefault()
      console.error("WebGL context lost")
      setWebGLError(true)
    }

    const handleContextRestored = () => {
      console.log("WebGL context restored")
      setWebGLError(false)
    }

    const canvas = canvasRef.current
    if (canvas) {
      canvas.addEventListener("webglcontextlost", handleContextLost)
      canvas.addEventListener("webglcontextrestored", handleContextRestored)
    }

    return () => {
      if (canvas) {
        canvas.removeEventListener("webglcontextlost", handleContextLost)
        canvas.removeEventListener("webglcontextrestored", handleContextRestored)
      }
    }
  }, [canvasRef])

  const handleStartPointSet = (point: [number, number]) => {
    setStartPoint(point)
  }

  const handleMeetingPointSet = (point: [number, number]) => {
    setMeetingPoint(point)
  }

  const handleStartSimulation = () => {
    if (startPoint && meetingPoint) {
      setIsSimulationRunning(true)
    } else {
      alert("Por favor, establece un punto de inicio y un punto de encuentro")
    }
  }

  const handleStopSimulation = () => {
    setIsSimulationRunning(false)
  }

  const handleResetSimulation = () => {
    setIsSimulationRunning(false)
    setStartPoint(null)
    setMeetingPoint(null)
    setBlockedAreas([])
    setStandingCount(0)
    setFallenCount(0)
    setTemperatureFallenCount(0)
  }

  const handleBlockArea = (point: [number, number]) => {
    if (isBlockingMode) {
      setBlockedAreas([...blockedAreas, point])
    }
  }

  const handleSettingsChange = (newSettings: Partial<SimulationSettings>) => {
    setSettings({ ...settings, ...newSettings })
  }

  const updateCounts = (standing: number, fallen: number, temperatureFallen: number) => {
    setStandingCount(standing)
    setFallenCount(fallen)
    setTemperatureFallenCount(temperatureFallen)
  }

  const canvasFallback = (
    <div
      style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: "#f3f4f6" }}
    >
      <div
        style={{
          padding: "1.5rem",
          maxWidth: "28rem",
          backgroundColor: "white",
          borderRadius: "0.5rem",
          boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        }}
      >
        <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: "#dc2626", marginBottom: "1rem" }}>
          Error de renderizado 3D
        </h2>
        <p style={{ marginBottom: "1rem" }}>
          No se pudo inicializar el contexto WebGL necesario para la simulación 3D. Esto puede deberse a:
        </p>
        <ul style={{ listStyleType: "disc", paddingLeft: "1.25rem", marginBottom: "1rem", lineHeight: 1.5 }}>
          <li>Tu navegador no soporta WebGL o está deshabilitado</li>
          <li>Tu tarjeta gráfica no es compatible o tiene controladores desactualizados</li>
          <li>Se ha agotado la memoria gráfica disponible</li>
        </ul>
        <button
          onClick={() => window.location.reload()}
          style={{
            display: "block",
            width: "100%",
            textAlign: "center",
            padding: "0.5rem",
            backgroundColor: "#3b82f6",
            color: "white",
            border: "none",
            borderRadius: "0.375rem",
            cursor: "pointer",
          }}
        >
          Intentar nuevamente
        </button>
      </div>
    </div>
  )

  return (
    <div style={styles.simulatorLayout}>
      {/* Mapa a la izquierda, grande y centrado */}
      <div style={styles.mapContainer}>
        <AboutProject />

        {/* Contenedor del mapa 3D */}
        <div style={styles.mapCanvasContainer}>
          <ErrorBoundary fallback={canvasFallback}>
            {webGLError ? (
              canvasFallback
            ) : (
              <Canvas
                ref={canvasRef}
                shadows
                camera={{ position: [0, 15, 15], fov: 50 }}
                style={{ width: "100%", height: "100%" }}
              >
                <ambientLight intensity={0.5} />
                <directionalLight
                  position={[10, 10, 10]}
                  intensity={1}
                  castShadow
                  shadow-mapSize-width={1024}
                  shadow-mapSize-height={1024}
                />
                <UrbanEnvironment blockedAreas={blockedAreas} />
                {isSimulationRunning && startPoint && meetingPoint && (
                  <AgentSystem
                    startPoint={startPoint}
                    meetingPoint={meetingPoint}
                    settings={settings}
                    blockedAreas={blockedAreas}
                    onUpdateCounts={updateCounts}
                  />
                )}
                <OrbitControls
                  enablePan={true}
                  enableZoom={true}
                  enableRotate={true}
                  minPolarAngle={0}
                  maxPolarAngle={Math.PI / 2.5}
                />
                {isBlockingMode && (
                  <mesh
                    rotation={[-Math.PI / 2, 0, 0]}
                    position={[0, 0.01, 0]}
                    onClick={(e) => {
                      const x = e.point.x
                      const z = e.point.z
                      handleBlockArea([x, z])
                    }}
                  >
                    <planeGeometry args={[100, 100]} />
                    <meshBasicMaterial transparent opacity={0} />
                  </mesh>
                )}
              </Canvas>
            )}
          </ErrorBoundary>
        </div>

        {/* Barra de botones - Con posición absoluta para estar al ras con el borde inferior */}
        <div style={styles.mapControls}>
          <div style={styles.controlsButtons}>
            <button
              onClick={() => {
                setIsBlockingMode(false)
                const handleClick = (e: MouseEvent) => {
                  const canvas = document.querySelector("canvas")
                  if (canvas) {
                    const rect = canvas.getBoundingClientRect()
                    const x = ((e.clientX - rect.left) / rect.width) * 2 - 1
                    const y = -((e.clientY - rect.top) / rect.height) * 2 + 1

                    // Convert to world coordinates (simplified)
                    const worldX = x * 10
                    const worldZ = y * 10

                    setStartPoint([worldX, worldZ])
                    document.removeEventListener("click", handleClick)
                  }
                }

                document.addEventListener("click", handleClick, { once: true })
              }}
              style={{ ...styles.button, ...styles.blueButton }}
            >
              Punto de inicio
            </button>
            <button
              onClick={() => {
                setIsBlockingMode(false)
                const handleClick = (e: MouseEvent) => {
                  const canvas = document.querySelector("canvas")
                  if (canvas) {
                    const rect = canvas.getBoundingClientRect()
                    const x = ((e.clientX - rect.left) / rect.width) * 2 - 1
                    const y = -((e.clientY - rect.top) / rect.height) * 2 + 1

                    // Convert to world coordinates (simplified)
                    const worldX = x * 10
                    const worldZ = y * 10

                    setMeetingPoint([worldX, worldZ])
                    document.removeEventListener("click", handleClick)
                  }
                }

                document.addEventListener("click", handleClick, { once: true })
              }}
              style={{ ...styles.button, ...styles.greenButton }}
            >
              Punto de encuentro
            </button>
            <button
              onClick={handleStartSimulation}
              disabled={!startPoint || !meetingPoint || isSimulationRunning}
              style={{
                ...styles.button,
                ...(!startPoint || !meetingPoint || isSimulationRunning ? styles.disabledButton : styles.redButton),
              }}
            >
              Start
            </button>
            <button
              onClick={handleStopSimulation}
              disabled={!isSimulationRunning}
              style={{
                ...styles.button,
                ...(!isSimulationRunning ? styles.disabledButton : styles.grayButton),
              }}
            >
              Stop
            </button>
            <button onClick={handleResetSimulation} style={{ ...styles.button, ...styles.yellowButton }}>
              Reset
            </button>
          </div>
        </div>
      </div>

      {/* Panel de configuración a la derecha */}
      <SimulationControls
        settings={settings}
        onSettingsChange={handleSettingsChange}
        standingCount={standingCount}
        fallenCount={fallenCount}
        temperatureFallenCount={temperatureFallenCount}
        onBlockStreet={() => {}}
        isBlockingMode={isBlockingMode}
        setIsBlockingMode={setIsBlockingMode}
      />
    </div>
  )
}
