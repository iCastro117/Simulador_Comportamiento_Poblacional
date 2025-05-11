"use client"
import { useEffect } from "react"
import type { SimulationSettings } from "../lib/types"
import { Slider } from "../components/ui/slider" // ✅ esto debe estar bien
import { Checkbox } from "../components/ui/checkbox"
import { Label } from "../components/ui/label"

interface SimulationControlsProps {
  settings: SimulationSettings
  onSettingsChange: (settings: Partial<SimulationSettings>) => void
  standingCount: number
  fallenCount: number
  temperatureFallenCount: number
  onBlockStreet: () => void
  isBlockingMode: boolean
  setIsBlockingMode: (isBlocking: boolean) => void
}

export default function SimulationControls({
  settings,
  onSettingsChange,
  standingCount,
  fallenCount,
  temperatureFallenCount,
  onBlockStreet,
  isBlockingMode,
  setIsBlockingMode,
}: SimulationControlsProps) {
  // Verificar que los controles estén funcionando
  useEffect(() => {
    console.log("SimulationControls renderizado con settings:", settings)
  }, [settings])

  return (
    <div className="controls-panel">
      <h2 className="controls-title">Settings</h2>

      <div className="controls-section">
        <div className="control-group">
          <div className="control-header">
            <Label htmlFor="speed" className="control-label">
              Velocidad de desplazamiento
            </Label>
            <span className="control-value">{settings.desiredSpeed.toFixed(1)}</span>
          </div>
          <Slider
            id="speed"
            className="slider"
            min={0.1}
            max={2.0}
            step={0.1}
            value={[settings.desiredSpeed]}
            onValueChange={(value: number[]) => {
              console.log("Cambiando velocidad a:", value[0])
              onSettingsChange({ desiredSpeed: value[0] })
            }}
          />
        </div>

        <div className="control-group">
          <div className="control-header">
            <Label htmlFor="agents" className="control-label">
              Número de personas
            </Label>
            <span className="control-value">{settings.maxAgents}</span>
          </div>
          <Slider
            id="agents"
            className="slider"
            min={10}
            max={200}
            step={10}
            value={[settings.maxAgents]}
            onValueChange={(value: number[]) => {
              console.log("Cambiando número de agentes a:", value[0])
              onSettingsChange({ maxAgents: value[0] })
            }}
          />
          <p className="control-description">
            A mayor número de personas y velocidad, con menos espacio (calles bloqueadas), aumentará el número de caídas
          </p>
        </div>

        <div className="control-group">
          <div className="control-header">
            <Label htmlFor="temperature" className="control-label">
              Temperatura (°C)
            </Label>
            <span className="control-value">{settings.temperature}°C</span>
          </div>
          <Slider
            id="temperature"
            className="slider"
            min={15}
            max={40}
            step={1}
            value={[settings.temperature]}
            onValueChange={(value: number[]) => {
              console.log("Cambiando temperatura a:", value[0])
              onSettingsChange({ temperature: value[0] })
            }}
          />
          <p className="control-description">
            Temperaturas más altas aumentan el estrés, reducen la velocidad óptima y pueden causar desmayos o asfixia en
            áreas densas
          </p>
        </div>

        <div className="checkbox-group">
          <Checkbox
            id="showFlow"
            checked={settings.showFlow}
            onCheckedChange={(checked: boolean) => onSettingsChange({ showFlow: checked })}
          />
          <Label htmlFor="showFlow" className="control-label">
            Mostrar flujo de personas
          </Label>
        </div>

        <div className="checkbox-group">
          <Checkbox
            id="showFallen"
            checked={settings.showFallen}
            onCheckedChange={(checked: boolean) => onSettingsChange({ showFallen: checked })}
          />
          <Label htmlFor="showFallen" className="control-label">
            Mostrar personas caídas
          </Label>
        </div>

        <div className="checkbox-group">
          <Checkbox
            id="showTemperatureFallen"
            checked={settings.showTemperatureFallen}
            onCheckedChange={(checked: boolean) => onSettingsChange({ showTemperatureFallen: checked })}
          />
          <Label htmlFor="showTemperatureFallen" className="control-label">
            Mostrar caídas por temperatura
          </Label>
        </div>

        <div className="control-group" style={{ marginTop: "1.5rem" }}>
          <button
            onClick={() => setIsBlockingMode(!isBlockingMode)}
            className={`btn btn-block ${isBlockingMode ? "btn-red" : "btn-blue"}`}
          >
            {isBlockingMode ? "Cancelar bloqueo" : "Bloquear calles"}
          </button>
          <p className="control-description">
            {isBlockingMode ? "Haz clic en el mapa para bloquear una calle" : "Activa el modo para bloquear calles"}
          </p>
        </div>
      </div>

      <div className="stats-container">
        <div className="stat-row">
          <span className="stat-label">Personas en pie:</span>
          <span className="stat-value">{standingCount}</span>
        </div>
        <div className="stat-row">
          <span className="stat-label">Caídas por colisión:</span>
          <span className="stat-value stat-value-red">{fallenCount - temperatureFallenCount}</span>
        </div>
        <div className="stat-row">
          <span className="stat-label">Caídas por temperatura:</span>
          <span className="stat-value stat-value-orange">{temperatureFallenCount}</span>
        </div>
      </div>
    </div>
  )
}
