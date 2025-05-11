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

// Valores predeterminados para los ajustes
const DEFAULT_SETTINGS: SimulationSettings = {
  desiredSpeed: 1.0,
  showFlow: true,
  showFallen: true,
  maxAgents: 50,
  temperature: 25,
  showTemperatureFallen: true,
}

export default function CrowdSimulator() {
  const [startPoint, setStartPoint] = useState<[number, number] | null>(null)
  const [meetingPoint, setMeetingPoint] = useState<[number, number] | null>(null)
  const [isSimulationRunning, setIsSimulationRunning] = useState(false)
  const [blockedAreas, setBlockedAreas] = useState<[number, number][]>([])
  const [standingCount, setStandingCount] = useState(0)
  const [fallenCount, setFallenCount] = useState(0)
  const [temperatureFallenCount, setTemperatureFallenCount] = useState(0)
  const [isBlockingMode, setIsBlockingMode] = useState(false)
  const [webGLError, setWebGLError] = useState(false)
  const [isSettingStartPoint, setIsSettingStartPoint] = useState(false)
  const [isSettingMeetingPoint, setIsSettingMeetingPoint] = useState(false)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  // Usar los valores predeterminados
  const [settings, setSettings] = useState<SimulationSettings>({ ...DEFAULT_SETTINGS })

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
    console.log("Punto de inicio establecido en:", point)
  }

  const handleMeetingPointSet = (point: [number, number]) => {
    setMeetingPoint(point)
    console.log("Punto de encuentro establecido en:", point)
  }

  const handleStartSimulation = () => {
    if (startPoint && meetingPoint) {
      setIsSimulationRunning(true)
      console.log("Iniciando simulación con punto de inicio:", startPoint, "y punto de encuentro:", meetingPoint)
      console.log("Configuración actual:", settings)
    } else {
      alert("Por favor, establece un punto de inicio y un punto de encuentro")
    }
  }

  const handleStopSimulation = () => {
    setIsSimulationRunning(false)
  }

  const handleResetSimulation = () => {
    // Detener la simulación
    setIsSimulationRunning(false)

    // Limpiar puntos y áreas bloqueadas
    setStartPoint(null)
    setMeetingPoint(null)
    setBlockedAreas([])

    // Restablecer contadores
    setStandingCount(0)
    setFallenCount(0)
    setTemperatureFallenCount(0)

    // Restablecer configuración a valores predeterminados
    setSettings({ ...DEFAULT_SETTINGS })

    // Desactivar modos de selección
    setIsBlockingMode(false)
    setIsSettingStartPoint(false)
    setIsSettingMeetingPoint(false)

    console.log("Simulación reiniciada, configuración restablecida a valores predeterminados")
  }

  const handleBlockArea = (point: [number, number]) => {
    if (isBlockingMode) {
      console.log("Bloqueando área en:", point)
      setBlockedAreas([...blockedAreas, point])
    }
  }

  const handleCanvasClick = (event: any) => {
    if (!isSettingStartPoint && !isSettingMeetingPoint && !isBlockingMode) return

    // Obtener las coordenadas del clic en el mundo 3D
    const x = event.point.x
    const z = event.point.z

    if (isSettingStartPoint) {
      handleStartPointSet([x, z])
      setIsSettingStartPoint(false)
    } else if (isSettingMeetingPoint) {
      handleMeetingPointSet([x, z])
      setIsSettingMeetingPoint(false)
    } else if (isBlockingMode) {
      handleBlockArea([x, z])
    }
  }

  const handleSettingsChange = (newSettings: Partial<SimulationSettings>) => {
    setSettings((prevSettings) => {
      const updatedSettings = { ...prevSettings, ...newSettings }
      console.log("Configuración actualizada:", updatedSettings)
      return updatedSettings
    })
  }

  const updateCounts = (standing: number, fallen: number, temperatureFallen: number) => {
    setStandingCount(standing)
    setFallenCount(fallen)
    setTemperatureFallenCount(temperatureFallen)
  }

  const canvasFallback = (
    <div className="error-container">
      <div className="error-box">
        <h2 className="error-title">Error de renderizado 3D</h2>
        <p className="error-message">
          No se pudo inicializar el contexto WebGL necesario para la simulación 3D. Esto puede deberse a:
        </p>
        <ul className="error-list">
          <li>Tu navegador no soporta WebGL o está deshabilitado</li>
          <li>Tu tarjeta gráfica no es compatible o tiene controladores desactualizados</li>
          <li>Se ha agotado la memoria gráfica disponible</li>
        </ul>
        <button onClick={() => window.location.reload()} className="btn btn-blue btn-block">
          Intentar nuevamente
        </button>
      </div>
    </div>
  )

  return (
    <div className="simulator-layout">
      {/* Mapa a la izquierda, grande y centrado */}
      <div className="map-container">
        <AboutProject />

        {/* Contenedor del mapa 3D */}
        <div className="map-canvas-container">
          <ErrorBoundary fallback={canvasFallback}>
            {webGLError ? (
              canvasFallback
            ) : (
              <Canvas ref={canvasRef} shadows camera={{ position: [0, 15, 15], fov: 50 }} className="map-canvas">
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
                {/* Mostrar marcadores incluso cuando la simulación no está corriendo */}
                {!isSimulationRunning && startPoint && (
                  <mesh position={[startPoint[0], 0.5, startPoint[1]]}>
                    <cylinderGeometry args={[1, 1, 1, 32]} />
                    <meshStandardMaterial color="blue" emissive="blue" emissiveIntensity={0.5} />
                  </mesh>
                )}
                {!isSimulationRunning && meetingPoint && (
                  <mesh position={[meetingPoint[0], 0.5, meetingPoint[1]]}>
                    <cylinderGeometry args={[1, 1, 1, 32]} />
                    <meshStandardMaterial color="green" emissive="green" emissiveIntensity={0.5} />
                  </mesh>
                )}
                <OrbitControls
                  enablePan={true}
                  enableZoom={true}
                  enableRotate={true}
                  minPolarAngle={0}
                  maxPolarAngle={Math.PI / 2.5}
                />
                {/* Plano invisible para detectar clics */}
                <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]} onClick={handleCanvasClick}>
                  <planeGeometry args={[100, 100]} />
                  <meshBasicMaterial transparent opacity={0} />
                </mesh>
              </Canvas>
            )}
          </ErrorBoundary>
        </div>

        {/* Barra de botones - Ahora con posición absoluta para estar al ras con el borde inferior */}
        <div className="map-controls">
          <div className="controls-buttons">
            <button
              onClick={() => {
                setIsBlockingMode(false)
                setIsSettingMeetingPoint(false)
                setIsSettingStartPoint(true)
                alert("Haz clic en el mapa para establecer el punto de inicio")
              }}
              className={`btn ${isSettingStartPoint ? "btn-red" : "btn-blue"}`}
            >
              Punto de inicio
            </button>
            <button
              onClick={() => {
                setIsBlockingMode(false)
                setIsSettingStartPoint(false)
                setIsSettingMeetingPoint(true)
                alert("Haz clic en el mapa para establecer el punto de encuentro")
              }}
              className={`btn ${isSettingMeetingPoint ? "btn-red" : "btn-green"}`}
            >
              Punto de encuentro
            </button>
            <button
              onClick={handleStartSimulation}
              disabled={!startPoint || !meetingPoint || isSimulationRunning}
              className="btn btn-red"
            >
              Start
            </button>
            <button onClick={handleStopSimulation} disabled={!isSimulationRunning} className="btn btn-gray">
              Stop
            </button>
            <button onClick={handleResetSimulation} className="btn btn-yellow">
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
