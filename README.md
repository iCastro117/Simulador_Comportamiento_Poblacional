# Simulador_Comportamiento_Poblacional# Population Behavior Simulator

A comprehensive simulation tool for modeling and visualizing crowd behavior in urban environments. This simulator demonstrates how individuals navigate through city streets, interact with obstacles, and respond to dynamic conditions.

## Features

- Advanced crowd movement simulation with realistic human behavior
- Interactive map with obstacles and navigation paths
- Multiple visualization modes for density, velocity, and acceleration
- Real-time statistics and performance metrics
- Customizable simulation parameters
- Improved path-finding algorithm with obstacle avoidance
- Density-based behavior and emergency situation modeling
- User-friendly controls with intuitive interface

## Getting Started

1. Ensure you have Python 3.6+ installed
2. Install the required dependencies:

```
pip install pygame numpy
```

3. Run the simulator:

```
python main.py
```

## How to Use

1. Set a starting point by clicking the "Start Point" button, then clicking on the map
2. Add meeting/destination points by clicking the "Meeting Points" button, then clicking on the map
3. Enter the number of people to simulate
4. Click "Start" to run the simulation
5. Use the controls in the right panel to adjust visualization options and simulation parameters

## Controls

- Use the simulation speed slider to speed up or slow down the simulation
- Toggle "Debug Mode" to view pathfinding and obstacle boundaries
- Choose different visualization modes from the dropdown menu
- Reset the simulation at any time with the "Reset" button
- Press Space to start/pause, R to reset, D to toggle debug mode

## Project Structure

- `main.py`: Main application entry point
- `person.py`: Person behavior simulation
- `map_utils.py`: Map handling and pathfinding
- `ui.py`: User interface components
- `config.py`: Configuration settings
- `assets/`: Directory containing map images

## Customization

You can customize the simulation by modifying the parameters in `config.py`:

- Change colors and visual styles
- Adjust default simulation parameters
- Add new visualization modes
- Modify the map by replacing the map image in the assets directory

## License

This project is open source and available under the MIT License.


#pip install pygame , .venv\Scripts\activate , pip install pygame , python main.py

# Ejecuta lo siguiente en PowerShell como administrador:
     #Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    
        # navega a la carpeta correcta, y luego intenta activar el entorno virtual:
            #cd C:\Users\usuario\Music\SIMULADOR_COMPORTAMIENTO_POBLACIONAL (cambia segun se descrageue o la direccion del archivo del juego de vsc))

           # en vsc:
                #python -m venv .venv

           # en powershell
              #& C:/Users/usuario/AppData/Local/Microsoft/WindowsApps/python3.12.exe
              #exit()

              # python -m venv .venv


              #.venv\Scripts\activate 


#pip install pk





