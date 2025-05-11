npm init -y

# React y Three.js
npm install react react-dom three
npm install --save-dev @types/react @types/react-dom @types/three

# React Three Fiber y Drei (esenciales para tus componentes)
npm install @react-three/fiber @react-three/drei

# Librerías de UI (Radix + shadcn/ui + estilos)
npm install class-variance-authority tailwind-merge clsx
npm install @radix-ui/react-slot @radix-ui/react-label @radix-ui/react-slider @radix-ui/react-checkbox @radix-ui/react-scroll-area @radix-ui/react-dialog

npm install lucide-react


✅ 4. (Solo si no tienes Vite) Inicializa el proyecto con Vite

npm create vite@latest
Nombre del proyecto: escribe . para usar la carpeta actual


Framework: selecciona React

Variante: TypeScript


npm install --save-dev vite typescript

npm install --save-dev @vitejs/plugin-react


✅ SOLUCIÓN: Instalar los tipos de Node.js
Ejecuta este comando:
npm install --save-dev @types/node
npm install vite --save-dev



✅ 5. Ejecuta el proyecto
Con Vite:
npm run dev
Con Next.js:


npm run dev



Luego abre en el navegador:
📎 http://localhost:5173 (Vite)
📎 http://localhost:3000 (Next.js)



VER ERRORES DE CORIGO:
        Usando TypeScript:
        npm install -g typescript
        tsc --noEmit



import React from "react"
import ReactDOM from "react-dom/client"
import CrowdSimulator from "./app/page"
npm install -g react-devtools

npm install @radix-ui/react-slider

npm update vite
npm install @vitejs/plugin-react@latest --save-dev

npm install vite --save-dev




npm run dev



ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <CrowdSimulator />
  </React.StrictMode>
)
