"""
Einstiegspunkt für Sturm auf Grayskull.
Startet die Simulation (später das vollständige Spiel).
"""
import os
import sys

# 1. Arbeitsverzeichnis auf den Projektordner setzen (unabhängig von VS Code)
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 2. Simulation starten (Import aus simulation.py)
from simulation import main as simulation_main

if __name__ == "__main__":
    simulation_main()  # Startet die Simulation aus simulation.py