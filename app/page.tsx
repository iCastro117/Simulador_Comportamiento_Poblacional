import CrowdSimulator from "../components/crowd-simulator"
import "../styles/reset-simulator.css" // Importamos el nuevo CSS

export default function Home() {
  return (
    <main className="simulator-main">
      <h1 className="simulator-title">
        Modelado Dinámico de Multitudes en Espacios Urbanos: Un Enfoque en Ecuaciones Diferenciales y Simulación
        Interactiva para Prevenir Tragedias como la de Itaewon
      </h1>
      <div className="simulator-container">
        <CrowdSimulator />
      </div>
    </main>
  )
}
