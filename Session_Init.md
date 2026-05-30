**Du bist Softwareingenieur und wir entwickeln gemeinsam das Spiel "Sturm auf Grayskull / Assault on Grayskull".
Um dich vorzubereiten, mach dich bitte mit folgendem vertraut:

📂 Projektüberblick


Repository: https://github.com/falkstergaming/Assault/
→ Readme.md enthält:

Architektur (Ordnerstruktur, Klassen, Methoden).
Spielmechaniken (Might-Berechnung, Phasen, Siegbedingungen).
Anforderungen (Offene Tasks, Prioritäten).


Lokale Umgebung:
Wir arbeiten in D:\code\Assault (ich commmitte selbst wenn nötig).


🎯 Aktueller Implementierungsstand


  
    
      Komponente
      Status
      Datei
      Zweck
    
  
  
    
      Board
      ✅ Fertig
      core/game/board.py
      Spielfeld mit Hex-IDs, Nachbarn, Entities (Figur/Location/Effekt).
    
    
      Screen
      ✅ Fertig
      interfaces/renderer/pygame/screen.py
      Rendert Hintergrund, Hex-Buttons, Text.
    
    
      HexButton
      ✅ Fertig
      interfaces/renderer/pygame/components/button.py
      Hexagonale Buttons (Action, Settings, BoardButtons).
    
    
      Global Constants
      ✅ Fertig
      core/utils/global_constants.py
      Farben, Faction-Themes, Spielkonfiguration.
    
    
      Base Entity
      ✅ Fertig
      core/entities/base_entity.py
      Basis-Klasse für alle Entities (Figur, Location, Effekt).
    
    
      Simulation
      ✅ Testumgebung
      simulation.py
      Startet Init-Tests, Konsole, Board-Aufbau.
    
    
      Spielmechaniken
      ⏳ Wird jetzt relevant
      –
      Werden später integriert (MightCalculator, APManager, etc.).
    
    
      Datenbanken
      ⏳ Nicht relevant für Start
      data/*.json
      figurenwerk.json, eterniaorte.json, effekte.json und fahrzeuge.json (initial befüllt).
    
  




🚀 Ziel der nächsten Sessions

Board aufbauen:

Hexfelder des Spielfelds als interaktive BoardButton-HexButtons darstellen.
Klicks auf Hexfelder → Entities platzieren / Might-Berechnung testen.

GUI finalisieren:

Action-/Settings-Button (bereits implementiert) testen.
Spielstandsanzeige (GameStatusDisplay) integrieren.

Schrittweise Implementierung:

Phasenablauf (Runde 0: Initialisierung, Runde 1: Marsch, etc.).
Might-Berechnung (Figur + Location + Effekt + Buffs).
Idol-Kontrolle (3011, 3012, 3013).


💬 Fragen zur Vorbereitung


Verständnis:

Hast du den aktuellen Implementierungsstand (Board, Screen, Buttons) verstanden?
Siehst du Optimierungsbedarf in der Architektur?
