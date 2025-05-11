import InlineStyleCrowdSimulator from "../components/inline-style-solution"

export default function InlineSolutionPage() {
  return (
    <main
      style={{
        display: "flex",
        flexDirection: "column",
        minHeight: "100vh",
        width: "100%",
      }}
    >
      <h1
        style={{
          fontSize: "1.5rem",
          fontWeight: "bold",
          textAlign: "center",
          padding: "1rem",
          backgroundColor: "#2563eb",
          color: "white",
          width: "100%",
        }}
      >
        Modelado Dinámico de Multitudes en Espacios Urbanos: Un Enfoque en Ecuaciones Diferenciales y Simulación
        Interactiva para Prevenir Tragedias como la de Itaewon
      </h1>
      <div
        style={{
          display: "flex",
          flex: 1,
          height: "calc(100vh - 4rem)",
        }}
      >
        <InlineStyleCrowdSimulator />
      </div>
    </main>
  )
}
