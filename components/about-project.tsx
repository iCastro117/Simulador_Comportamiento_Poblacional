"use client"
import { useState } from "react"

export default function AboutProject() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <button className="about-project-btn" onClick={() => setIsOpen(true)}>
        Acerca del Proyecto
      </button>

      {isOpen && (
        <div className="modal-overlay" onClick={() => setIsOpen(false)}>
          <div className="modal-container" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setIsOpen(false)}>
              ×
            </button>
            <h2 className="modal-title">
              Modelado Dinámico de Multitudes en Espacios Urbanos: Un Enfoque en Ecuaciones Diferenciales y Simulación
              Interactiva para Prevenir Tragedias como la de Itaewon
            </h2>

            <div className="modal-content">
              <div className="modal-section">
                <h3 className="modal-section-title">Autores</h3>
                <ul className="modal-list">
                  <li>Mauricio Jesus Iturriza Medina</li>
                  <li>Isabella Castro Camacho</li>
                  <li>Paula Andrea Corredor Gonzalez</li>
                  <li>Julian Peñalosa</li>
                  <li>Juan Gomez Gonzalez</li>
                </ul>
              </div>

              <div className="modal-section">
                <h3 className="modal-section-title">Introducción</h3>
                <p>
                  El trágico suceso ocurrido en Seúl, Corea del Sur, el 29 de octubre de 2022, evidenció la peligrosidad
                  de la alta concentración de personas en espacios reducidos sin una adecuada gestión del flujo de
                  multitudes (Ministry of the Interior and Safety, 2022; Seoul Metropolitan Government, 2023). Durante
                  la celebración de Halloween en el barrio de Itaewon, miles de jóvenes se reunieron en calles estrechas
                  y mal reguladas, lo que provocó una aglomeración incontrolable. Como resultado, más de 150 personas
                  perdieron la vida y decenas más resultaron heridas debido a la falta de oxígeno y la presión generada
                  por la multitud.
                </p>
                <p style={{ marginTop: "0.5rem" }}>
                  Es por eso que se vio la necesidad de desarrollar una herramienta de simulación que integre modelos
                  matemáticos avanzados para simular escenarios críticos. En este proyecto, se propone crear un
                  simulador basado en ecuaciones diferenciales ordinarias (EDOs) que modele la dinámica de multitudes,
                  incorporando factores como la densidad poblacional, la temperatura ambiental y las interacciones de
                  atracción-repulsión entre individuos.
                </p>
              </div>

              <div className="modal-section">
                <h3 className="modal-section-title">Objeto de Estudio</h3>
                <p>
                  El objeto de estudio es el comportamiento de las multitudes en espacios reducidos, donde factores como
                  la densidad de personas, el flujo de movimiento y las condiciones ambientales (como la temperatura)
                  influyen en el riesgo de estampidas.
                </p>
                <p style={{ marginTop: "0.5rem" }}>
                  <strong>Tasas de cambio:</strong>
                  <br />• Variación de la temperatura ambiental en función del número de personas.
                  <br />• Tiempo de desplazamiento en función de la densidad poblacional.
                </p>
                <p style={{ marginTop: "0.5rem" }}>
                  <strong>Interacciones dinámicas:</strong>
                  <br />• Fuerzas de atracción (hacia puntos de interés) y repulsión (evitación de colisiones).
                  <br />• Efectos de la temperatura en la velocidad individual y el estrés colectivo.
                </p>
              </div>

              <div className="modal-section">
                <h3 className="modal-section-title">Implementación</h3>
                <p>
                  Este simulador implementa los modelos de fuerza social de Helbing y Molnár (1995), Hughes (2002), Budd
                  (2018) y Shi et al. (2021), integrando variables como la temperatura ambiental y la densidad
                  poblacional para mejorar la precisión en contextos urbanos complejos.
                </p>
                <p style={{ marginTop: "0.5rem" }}>
                  Las ecuaciones diferenciales ordinarias (EDOs) implementadas modelan:
                  <br />• La evolución de la posición de cada individuo según su velocidad actual.
                  <br />• El cambio de velocidad debido a diferentes fuerzas: intención global, interacción social y
                  obstáculos.
                  <br />• Los efectos de la temperatura y densidad en el comportamiento colectivo.
                </p>
              </div>

              <div className="modal-section">
                <h3 className="modal-section-title">Referencias</h3>
                <ol className="modal-reference-list">
                  <li className="modal-reference-item">
                    Christopher B. (2018). Can You Do Mathematics In A Crowd?. Gresham College.
                    https://www.gresham.ac.uk/sites/default/files/2018-04-24_ChrisBudd_MathsInACrowd-T.pdf
                  </li>
                  <li className="modal-reference-item">
                    Helbing, D., & Molnar, P. (1995). Social Force Model for Pedestrian Dynamics. Physical Review E,
                    51(5), 4282–4286. https://journals.aps.org/pre/abstract/10.1103/PhysRevE.51.4282
                  </li>
                  <li className="modal-reference-item">
                    Helbing, D., et al. (2005). Self-organized pedestrian crowd dynamics: Experiments, simulations, and
                    design solutions. Transportation Science, 39(1), 1–24.
                    https://pubsonline.informs.org/doi/10.1287/trsc.1040.0108
                  </li>
                  <li className="modal-reference-item">
                    Ministry of the Interior and Safety, South Korea. (2022). Official Report on the Itaewon Crowd
                    Disaster. https://www.mois.go.kr/
                  </li>
                  <li className="modal-reference-item">
                    Seoul Metropolitan Government. (2023). Urban Crowd Management Guidelines Post-Itaewon.
                    https://www.seoul.go.kr/
                  </li>
                </ol>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
