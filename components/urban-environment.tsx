"use client"

import { useEffect, useMemo, useState } from "react"
import * as THREE from "three"

interface UrbanEnvironmentProps {
  blockedAreas: [number, number][]
}

export default function UrbanEnvironment({ blockedAreas }: UrbanEnvironmentProps) {
  // Create an urban grid inspired by Itaewon's narrow streets
  const gridSize = 20
  const [textures, setTextures] = useState<{
    road: THREE.Texture | null
    building: THREE.Texture | null
    blockade: THREE.Texture | null
  }>({
    road: null,
    building: null,
    blockade: null,
  })

  // Create fallback textures programmatically
  useEffect(() => {
    // Create road texture
    const roadCanvas = document.createElement("canvas")
    roadCanvas.width = 512
    roadCanvas.height = 512
    const roadCtx = roadCanvas.getContext("2d")
    if (roadCtx) {
      roadCtx.fillStyle = "#888888"
      roadCtx.fillRect(0, 0, 512, 512)
      roadCtx.strokeStyle = "#FFFFFF"
      roadCtx.lineWidth = 2
      roadCtx.beginPath()
      roadCtx.moveTo(0, 256)
      roadCtx.lineTo(512, 256)
      roadCtx.stroke()
    }
    const roadTexture = new THREE.CanvasTexture(roadCanvas)
    roadTexture.wrapS = roadTexture.wrapT = THREE.RepeatWrapping

    // Create building texture
    const buildingCanvas = document.createElement("canvas")
    buildingCanvas.width = 512
    buildingCanvas.height = 512
    const buildingCtx = buildingCanvas.getContext("2d")
    if (buildingCtx) {
      buildingCtx.fillStyle = "#555555"
      buildingCtx.fillRect(0, 0, 512, 512)
      buildingCtx.strokeStyle = "#333333"
      buildingCtx.lineWidth = 10
      buildingCtx.strokeRect(0, 0, 512, 512)
      // Add some windows
      buildingCtx.fillStyle = "#CCCCCC"
      for (let i = 0; i < 5; i++) {
        for (let j = 0; j < 5; j++) {
          buildingCtx.fillRect(i * 100 + 20, j * 100 + 20, 60, 60)
        }
      }
    }
    const buildingTexture = new THREE.CanvasTexture(buildingCanvas)
    buildingTexture.wrapS = buildingTexture.wrapT = THREE.RepeatWrapping

    // Create blockade texture
    const blockadeCanvas = document.createElement("canvas")
    blockadeCanvas.width = 512
    blockadeCanvas.height = 512
    const blockadeCtx = blockadeCanvas.getContext("2d")
    if (blockadeCtx) {
      blockadeCtx.fillStyle = "#FF0000"
      blockadeCtx.fillRect(0, 0, 512, 512)
      blockadeCtx.strokeStyle = "#FFFFFF"
      blockadeCtx.lineWidth = 20
      // Draw an X
      blockadeCtx.beginPath()
      blockadeCtx.moveTo(0, 0)
      blockadeCtx.lineTo(512, 512)
      blockadeCtx.moveTo(512, 0)
      blockadeCtx.lineTo(0, 512)
      blockadeCtx.stroke()
    }
    const blockadeTexture = new THREE.CanvasTexture(blockadeCanvas)

    setTextures({
      road: roadTexture,
      building: buildingTexture,
      blockade: blockadeTexture,
    })
  }, [])

  const cityMap = useMemo(() => {
    // 0 = road, 1 = building
    const map = Array(gridSize)
      .fill(0)
      .map(() => Array(gridSize).fill(0))

    // Create a main street with narrow alleys (Itaewon-inspired layout)
    // Main street
    for (let x = 0; x < gridSize; x++) {
      for (let z = 9; z <= 11; z++) {
        map[x][z] = 0 // Road
      }
    }

    // Narrow side alleys
    for (let z = 0; z < gridSize; z++) {
      for (let x = 4; x <= 5; x++) {
        map[x][z] = 0 // Road
      }
      for (let x = 14; x <= 15; x++) {
        map[x][z] = 0 // Road
      }
    }

    // Add buildings in the remaining space
    for (let x = 0; x < gridSize; x++) {
      for (let z = 0; z < gridSize; z++) {
        // If not already a road, make it a building
        if (
          !(
            (z >= 9 && z <= 11) || // Main street
            (x >= 4 && x <= 5) || // First alley
            (x >= 14 && x <= 15)
          ) // Second alley
        ) {
          map[x][z] = 1 // Building
        }
      }
    }

    return map
  }, [])

  // Add blocked areas to the map
  useEffect(() => {
    blockedAreas.forEach(([x, z]) => {
      const gridX = Math.floor((x + gridSize / 2) / 1)
      const gridZ = Math.floor((z + gridSize / 2) / 1)

      if (gridX >= 0 && gridX < gridSize && gridZ >= 0 && gridZ < gridSize) {
        cityMap[gridX][gridZ] = 2 // 2 = blocked area
      }
    })
  }, [blockedAreas, cityMap])

  // If textures aren't loaded yet, don't render anything
  if (!textures.road || !textures.building || !textures.blockade) {
    return null
  }

  return (
    <group>
      {/* Ground plane */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.1, 0]} receiveShadow>
        <planeGeometry args={[gridSize, gridSize]} />
        <meshStandardMaterial color="#555555" />
      </mesh>

      {/* City grid */}
      {cityMap.map((row, x) =>
        row.map((cell, z) => {
          const posX = x - gridSize / 2 + 0.5
          const posZ = z - gridSize / 2 + 0.5

          if (cell === 1) {
            // Building
            const height = Math.random() * 3 + 1
            return (
              <mesh key={`building-${x}-${z}`} position={[posX, height / 2, posZ]} castShadow receiveShadow>
                <boxGeometry args={[0.9, height, 0.9]} />
                <meshStandardMaterial
                  map={textures.building}
                  color={new THREE.Color().setHSL(Math.random() * 0.1 + 0.05, 0.5, 0.5)}
                />
              </mesh>
            )
          } else if (cell === 2) {
            // Blocked area
            return (
              <mesh key={`blockade-${x}-${z}`} position={[posX, 0.1, posZ]} rotation={[-Math.PI / 2, 0, 0]}>
                <planeGeometry args={[0.9, 0.9]} />
                <meshStandardMaterial map={textures.blockade} color="red" transparent opacity={0.7} />
              </mesh>
            )
          } else {
            // Road
            return (
              <mesh key={`road-${x}-${z}`} position={[posX, 0, posZ]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
                <planeGeometry args={[1, 1]} />
                <meshStandardMaterial map={textures.road} color="#888888" />
              </mesh>
            )
          }
        }),
      )}
    </group>
  )
}
