"use client"

import { useRef, useEffect, useState, useMemo } from "react"
import { useFrame, type RootState } from "@react-three/fiber"
import * as THREE from "three"
import type { SimulationSettings } from "../lib/types"
import { type Agent, updateAgentPositions } from "../lib/agent-dynamics"
import WebGLContextHandler from "../components/webgl-context-handler"

interface AgentSystemProps {
  startPoint: [number, number]
  meetingPoint: [number, number]
  settings: SimulationSettings
  blockedAreas: [number, number][]
  onUpdateCounts: (standing: number, fallen: number, temperatureFallen: number) => void
}

export default function AgentSystem({
  startPoint,
  meetingPoint,
  settings,
  blockedAreas,
  onUpdateCounts,
}: AgentSystemProps) {
  const agentsRef = useRef<Agent[]>([])
  const instancedMeshRef = useRef<THREE.InstancedMesh>(null)
  const flowLinesRef = useRef<THREE.Group>(null)
  const [spawnTimer, setSpawnTimer] = useState(0)
  const [contextLost, setContextLost] = useState(false)
  const settingsRef = useRef(settings)

  // Actualizar la referencia cuando cambian los settings
  useEffect(() => {
    settingsRef.current = settings
    console.log("Settings actualizados:", settings)
  }, [settings])

  // Create a dummy texture for agents
  const dummyTexture = useMemo(() => {
    const canvas = document.createElement("canvas")
    canvas.width = 128
    canvas.height = 128
    const ctx = canvas.getContext("2d")
    if (ctx) {
      ctx.fillStyle = "#FFFFFF"
      ctx.fillRect(0, 0, 128, 128)
      ctx.fillStyle = "#000000"
      ctx.beginPath()
      ctx.arc(64, 64, 32, 0, Math.PI * 2)
      ctx.fill()
    }
    return new THREE.CanvasTexture(canvas)
  }, [])

  // Initialize agents
  useEffect(() => {
    agentsRef.current = []

    // Create initial flow lines group
    if (flowLinesRef.current) {
      while (flowLinesRef.current.children.length > 0) {
        flowLinesRef.current.remove(flowLinesRef.current.children[0])
      }
    }

    return () => {
      agentsRef.current = []
    }
  }, [startPoint, meetingPoint])

  // Handle WebGL context events
  const handleContextLost = () => {
    setContextLost(true)
  }

  const handleContextRestored = () => {
    setContextLost(false)
  }

  // Update agent positions on each frame
  useFrame((state: RootState, delta: number) => {
    if (contextLost) return

    // Limit delta time to prevent large jumps if frame rate drops
    const cappedDelta = Math.min(delta, 0.1)

    // Spawn new agents periodically
    setSpawnTimer((prev: number) => {
      if (prev > 0.5) {
        // Spawn a new agent
        if (agentsRef.current.length < settingsRef.current.maxAgents) {
          const newAgent: Agent = {
            position: new THREE.Vector3(startPoint[0], 0, startPoint[1]),
            velocity: new THREE.Vector3(0, 0, 0),
            desiredVelocity: new THREE.Vector3(0, 0, 0),
            acceleration: new THREE.Vector3(0, 0, 0),
            fallen: false,
            fallenByTemperature: false,
            mass: 60 + Math.random() * 20, // 60-80 kg
            radius: 0.25 + Math.random() * 0.1, // 0.25-0.35 m
            maxSpeed: settingsRef.current.desiredSpeed * (0.8 + Math.random() * 0.4), // Variation in max speed
            color: new THREE.Color(0.1 + Math.random() * 0.3, 0.4 + Math.random() * 0.3, 0.6 + Math.random() * 0.3),
            temperature: settingsRef.current.temperature, // Initialize with ambient temperature
            heatStress: 0, // Initialize with no heat stress
            timeInHighTemp: 0, // Initialize with no time in high temperature
          }
          agentsRef.current.push(newAgent)
        }
        return 0
      }
      return prev + cappedDelta
    })

    // Update agent positions using ODE solver
    const meetingPointVec = new THREE.Vector3(meetingPoint[0], 0, meetingPoint[1])
    const obstacles = blockedAreas.map(([x, z]) => new THREE.Vector3(x, 0, z))

    try {
      updateAgentPositions(
        agentsRef.current,
        cappedDelta,
        meetingPointVec,
        settingsRef.current.desiredSpeed,
        obstacles,
        settingsRef.current.temperature, // Pass ambient temperature
      )
    } catch (error) {
      console.error("Error updating agent positions:", error)
    }

    // Update instanced mesh
    if (instancedMeshRef.current) {
      const dummy = new THREE.Object3D()
      let standingCount = 0
      let fallenCount = 0
      let temperatureFallenCount = 0

      agentsRef.current.forEach((agent, i) => {
        if (agent.fallen) {
          fallenCount++

          if (agent.fallenByTemperature) {
            temperatureFallenCount++

            // Show temperature-fallen agents in orange if enabled
            if (settingsRef.current.showTemperatureFallen) {
              dummy.position.set(agent.position.x, 0.05, agent.position.z)
              dummy.scale.set(1, 0.1, 1)
              dummy.updateMatrix()
              instancedMeshRef.current!.setMatrixAt(i, dummy.matrix)
              instancedMeshRef.current!.setColorAt(i, new THREE.Color("orange"))
            } else {
              dummy.scale.set(0, 0, 0) // Hide if not showing
              dummy.updateMatrix()
              instancedMeshRef.current!.setMatrixAt(i, dummy.matrix)
            }
          } else {
            // Show collision-fallen agents in red if enabled
            if (settingsRef.current.showFallen) {
              dummy.position.set(agent.position.x, 0.05, agent.position.z)
              dummy.scale.set(1, 0.1, 1)
              dummy.updateMatrix()
              instancedMeshRef.current!.setMatrixAt(i, dummy.matrix)
              instancedMeshRef.current!.setColorAt(i, new THREE.Color("red"))
            } else {
              dummy.scale.set(0, 0, 0) // Hide if not showing
              dummy.updateMatrix()
              instancedMeshRef.current!.setMatrixAt(i, dummy.matrix)
            }
          }
        } else {
          standingCount++

          // Color based on temperature (blue=cool, red=hot)
          const tempColor = new THREE.Color()
          const normalizedTemp = (agent.temperature - 15) / 25 // 15-40°C range
          tempColor.setHSL(0.6 * (1 - normalizedTemp), 0.8, 0.5)

          dummy.position.set(agent.position.x, agent.radius, agent.position.z)
          dummy.scale.set(agent.radius * 2, agent.radius * 2, agent.radius * 2)
          dummy.updateMatrix()
          instancedMeshRef.current!.setMatrixAt(i, dummy.matrix)
          instancedMeshRef.current!.setColorAt(i, tempColor)
        }
      })

      instancedMeshRef.current.instanceMatrix.needsUpdate = true
      if (instancedMeshRef.current.instanceColor) {
        instancedMeshRef.current.instanceColor.needsUpdate = true
      }

      // Update flow lines
      if (flowLinesRef.current && settingsRef.current.showFlow) {
        // Clear previous flow lines
        while (flowLinesRef.current.children.length > 0) {
          flowLinesRef.current.remove(flowLinesRef.current.children[0])
        }

        // Create new flow lines for each agent
        agentsRef.current.forEach((agent, i) => {
          if (!agent.fallen && i % 5 === 0) {
            // Only show some flow lines to avoid clutter
            const arrowLength = agent.velocity.length() * 0.5
            if (arrowLength > 0.1) {
              const arrowHelper = new THREE.ArrowHelper(
                agent.velocity.clone().normalize(),
                new THREE.Vector3(agent.position.x, agent.radius * 2, agent.position.z),
                arrowLength,
                0x00ff00,
                0.2,
                0.1,
              )
              flowLinesRef.current!.add(arrowHelper)
            }
          }
        })
      }

      // Update counts
      onUpdateCounts(standingCount, fallenCount, temperatureFallenCount)
    }
  })

  return (
    <group>
      <WebGLContextHandler onContextLost={handleContextLost} onContextRestored={handleContextRestored} />

      <instancedMesh
        ref={instancedMeshRef}
        args={[undefined, undefined, settings.maxAgents]} // Support up to maxAgents
        castShadow
        receiveShadow
      >
        <sphereGeometry args={[0.5, 16, 16]} />
        <meshStandardMaterial />
      </instancedMesh>

      {/* Meeting point marker - Más grande y visible */}
      <mesh position={[meetingPoint[0], 0.5, meetingPoint[1]]}>
        <cylinderGeometry args={[1, 1, 1, 32]} />
        <meshStandardMaterial color="green" emissive="green" emissiveIntensity={0.5} />
      </mesh>

      {/* Start point marker - Más grande y visible */}
      <mesh position={[startPoint[0], 0.5, startPoint[1]]}>
        <cylinderGeometry args={[1, 1, 1, 32]} />
        <meshStandardMaterial color="blue" emissive="blue" emissiveIntensity={0.5} />
      </mesh>

      {/* Flow lines group */}
      <group ref={flowLinesRef} />
    </group>
  )
}
