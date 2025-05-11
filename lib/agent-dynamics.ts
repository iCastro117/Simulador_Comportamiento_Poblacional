import * as THREE from "three"

export interface Agent {
  position: THREE.Vector3
  velocity: THREE.Vector3
  desiredVelocity: THREE.Vector3
  acceleration: THREE.Vector3
  fallen: boolean
  fallenByTemperature: boolean
  mass: number
  radius: number
  maxSpeed: number
  color: THREE.Color
  temperature: number // Local temperature experienced by the agent
  heatStress: number // Accumulated heat stress
  timeInHighTemp: number // Time spent in high temperature
}

// Constants for the social force model based on Helbing, Budd, and Shi models
const RELAXATION_TIME = 0.5 // Time to reach desired velocity (τ in equations)
const SOCIAL_FORCE_A = 1000 // Reducido para menos repulsión entre agentes
const SOCIAL_FORCE_B = 0.08 // Repulsive force range
const OBSTACLE_FORCE_A = 1500 // Reducido para menos repulsión de obstáculos
const OBSTACLE_FORCE_B = 0.1 // Obstacle repulsive force range
const DESIRED_FORCE_FACTOR = 2.0 // Aumentado para dar más prioridad al movimiento hacia el objetivo
const FALL_THRESHOLD = 20.0 // Aumentado para que sea más difícil caerse
const DENSITY_SENSITIVITY = 0.04 // Reducido para menor efecto de la densidad
const TEMPERATURE_SENSITIVITY = 0.02 // Reducido para menor efecto de la temperatura
const OPTIMAL_TEMPERATURE = 22 // Optimal temperature in Celsius (T₀ in equations)
const OPTIMAL_DENSITY = 3.0 // Aumentado para permitir más densidad
const HIGH_TEMP_THRESHOLD = 35 // Aumentado para que sea más difícil sufrir por temperatura
const CRITICAL_HEAT_STRESS = 20 // Aumentado para que sea más difícil desmayarse por calor
const HEAT_STRESS_RECOVERY_RATE = 0.5 // Aumentado para recuperarse más rápido

// ODE solver for agent dynamics
export function updateAgentPositions(
  agents: Agent[],
  deltaTime: number,
  targetPoint: THREE.Vector3,
  desiredSpeed: number,
  obstacles: THREE.Vector3[],
  ambientTemperature = 25, // Default ambient temperature
) {
  // Calculate forces for each agent
  agents.forEach((agent) => {
    if (agent.fallen) return // Skip fallen agents

    // Reset acceleration
    agent.acceleration.set(0, 0, 0)

    // Update agent's local temperature based on ambient and crowd density
    updateAgentTemperature(agent, agents, ambientTemperature, deltaTime)

    // Calculate desired velocity (direction to target * desired speed)
    // This implements the first term in the proposed ODE (vdesired - vi)/τ
    const desiredDirection = new THREE.Vector3().subVectors(targetPoint, agent.position).normalize()

    // Usar el desiredSpeed pasado como parámetro para que los cambios en el slider tengan efecto
    agent.desiredVelocity = desiredDirection.multiplyScalar(agent.maxSpeed * desiredSpeed)

    // 1. Desired force (tendency to move toward target) - Budd model
    // This is the α(vdesired - vi) term
    const desiredForce = new THREE.Vector3().subVectors(agent.desiredVelocity, agent.velocity)
    desiredForce.divideScalar(RELAXATION_TIME)
    desiredForce.multiplyScalar(DESIRED_FORCE_FACTOR)

    // 2. Social forces (repulsion between agents) - Helbing model
    // This implements the β∑f(rij) term for interaction with other individuals
    const socialForce = new THREE.Vector3(0, 0, 0)

    agents.forEach((otherAgent) => {
      if (agent === otherAgent) return

      const distance = agent.position.distanceTo(otherAgent.position)
      const minDistance = agent.radius + otherAgent.radius

      if (distance < minDistance * 5) {
        // Only consider nearby agents
        const direction = new THREE.Vector3().subVectors(agent.position, otherAgent.position).normalize()

        // Calculate repulsive force using exponential decay
        const repulsiveForce = SOCIAL_FORCE_A * Math.exp((minDistance - distance) / SOCIAL_FORCE_B)

        // Add to total social force
        socialForce.add(direction.multiplyScalar(repulsiveForce))

        // Add velocity-dependent force component (for collision prediction)
        const velocityDifference = new THREE.Vector3().subVectors(otherAgent.velocity, agent.velocity)
        const velocityForce = velocityDifference.dot(direction) * 0.5
        if (velocityForce > 0) {
          socialForce.add(direction.multiplyScalar(velocityForce))
        }
      }
    })

    // 3. Obstacle forces (repulsion from obstacles) - Shi model
    // This implements the ζfobs(ri) term for obstacle avoidance
    const obstacleForce = new THREE.Vector3(0, 0, 0)

    obstacles.forEach((obstacle) => {
      const distance = agent.position.distanceTo(obstacle)
      const minDistance = agent.radius + 0.5 // Obstacle radius

      if (distance < minDistance * 3) {
        const direction = new THREE.Vector3().subVectors(agent.position, obstacle).normalize()
        const repulsiveForce = OBSTACLE_FORCE_A * Math.exp((minDistance - distance) / OBSTACLE_FORCE_B)
        obstacleForce.add(direction.multiplyScalar(repulsiveForce))
      }
    })

    // 4. Temperature and density effects - Shi model
    // Calculate local density based on nearby agents
    // This implements the δ∇(ρi - ρoptimal) term for density effects
    let localDensity = 0
    agents.forEach((otherAgent) => {
      if (agent === otherAgent) return
      const distance = agent.position.distanceTo(otherAgent.position)
      if (distance < 2.0) {
        localDensity += 1.0 / (distance + 0.1)
      }
    })

    // Temperature effect - reduces desired speed when temperature deviates from optimal
    // This implements the γ∇(Ti - T0) term for temperature effects
    const temperatureDeviation = agent.temperature - OPTIMAL_TEMPERATURE
    const temperatureForce = new THREE.Vector3()
    if (Math.abs(temperatureDeviation) > 5) {
      // Aumentado el umbral
      // Only apply when temperature deviates significantly
      // Direction away from high temperature areas (simplified gradient)
      const temperatureDirection = desiredDirection.clone().negate()
      const temperatureFactor = TEMPERATURE_SENSITIVITY * Math.abs(temperatureDeviation)
      temperatureForce.copy(temperatureDirection).multiplyScalar(temperatureFactor)
    }

    // Density effect - reduces desired speed in crowded areas
    // This is part of the δ∇(ρi - ρoptimal) term
    const densityDeviation = localDensity - OPTIMAL_DENSITY
    const densityForce = new THREE.Vector3()
    if (densityDeviation > 1) {
      // Aumentado el umbral
      // Only apply in overcrowded areas
      // Direction away from high density areas (simplified gradient)
      const densityDirection = desiredDirection.clone().negate()
      const densityFactor = DENSITY_SENSITIVITY * densityDeviation
      densityForce.copy(densityDirection).multiplyScalar(densityFactor)
    }

    // Apply temperature effect to desired force
    const temperatureFactor = Math.max(0.7, 1.0 - Math.abs(temperatureDeviation) * 0.01) // Reducido el impacto
    desiredForce.multiplyScalar(temperatureFactor)

    // Sum all forces
    const totalForce = new THREE.Vector3()
      .add(desiredForce)
      .add(socialForce)
      .add(obstacleForce)
      .add(temperatureForce)
      .add(densityForce)

    // F = ma, so a = F/m
    agent.acceleration.copy(totalForce.divideScalar(agent.mass))

    // Check if agent falls due to excessive force
    const forceMagnitude = totalForce.length()
    if (forceMagnitude > FALL_THRESHOLD * agent.mass) {
      agent.fallen = true
      agent.fallenByTemperature = false
    }

    // Check if agent falls due to heat stress
    if (agent.heatStress >= CRITICAL_HEAT_STRESS) {
      agent.fallen = true
      agent.fallenByTemperature = true
    }

    // Reducir drásticamente la probabilidad de caídas
    if (localDensity > 6.0 || Math.abs(temperatureDeviation) > 15) {
      const environmentalStress = (localDensity - 6.0) * 0.001 + Math.abs(temperatureDeviation) * 0.0005
      if (Math.random() < environmentalStress) {
        agent.fallen = true
        // Determine if the fall was primarily due to temperature
        agent.fallenByTemperature = Math.abs(temperatureDeviation) > 15
      }
    }
  })

  // Update positions using semi-implicit Euler integration
  agents.forEach((agent) => {
    if (agent.fallen) return // Skip fallen agents

    // Update velocity: v(t+dt) = v(t) + a(t) * dt
    agent.velocity.add(agent.acceleration.clone().multiplyScalar(deltaTime))

    // Limit speed based on current desiredSpeed setting
    const maxCurrentSpeed = agent.maxSpeed * desiredSpeed
    const speed = agent.velocity.length()
    if (speed > maxCurrentSpeed) {
      agent.velocity.multiplyScalar(maxCurrentSpeed / speed)
    }

    // Asegurar una velocidad mínima para que siempre se muevan
    if (speed < 0.1 * maxCurrentSpeed) {
      const dirToTarget = new THREE.Vector3().subVectors(targetPoint, agent.position).normalize()
      agent.velocity.copy(dirToTarget.multiplyScalar(0.1 * maxCurrentSpeed))
    }

    // Update position: x(t+dt) = x(t) + v(t+dt) * dt
    agent.position.add(agent.velocity.clone().multiplyScalar(deltaTime))

    // Check if agent has reached the target
    if (agent.position.distanceTo(targetPoint) < 0.5) {
      // Remove agent when it reaches the target
      agent.fallen = true // Use fallen state to remove from simulation
      agent.fallenByTemperature = false
    }
  })
}

// Update agent's local temperature based on ambient temperature and crowd density
function updateAgentTemperature(agent: Agent, agents: Agent[], ambientTemperature: number, deltaTime: number) {
  // Calculate local crowd density around the agent
  let nearbyAgents = 0
  agents.forEach((otherAgent) => {
    if (agent === otherAgent) return
    const distance = agent.position.distanceTo(otherAgent.position)
    if (distance < 1.5) {
      nearbyAgents++
    }
  })

  // Temperature increases with crowd density (body heat)
  // This implements a simplified version of the temperature diffusion equation
  const crowdHeatContribution = nearbyAgents * 0.1 // Reducido: cada persona añade 0.1°C

  // Temperature approaches ambient + crowd heat with some lag
  const targetTemperature = ambientTemperature + crowdHeatContribution
  agent.temperature = agent.temperature * 0.9 + targetTemperature * 0.1 // Gradual adjustment

  // Update heat stress based on temperature and time
  if (agent.temperature > HIGH_TEMP_THRESHOLD) {
    // Accumulate heat stress in high temperatures
    // More stress in higher temperatures and denser crowds
    const tempFactor = (agent.temperature - HIGH_TEMP_THRESHOLD) / 10 // Normalized factor
    const densityFactor = Math.min(1, nearbyAgents / 5) // Normalized factor

    // Heat stress increases faster in high temps and dense crowds
    agent.heatStress += (tempFactor * densityFactor + 0.05) * deltaTime // Reducido
    agent.timeInHighTemp += deltaTime
  } else {
    // Recover from heat stress in normal temperatures
    agent.heatStress = Math.max(0, agent.heatStress - HEAT_STRESS_RECOVERY_RATE * deltaTime)
    agent.timeInHighTemp = 0
  }
}
