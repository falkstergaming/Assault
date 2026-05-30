# 📜 **Assault on Grayskull / Sturm auf Grayskull – Dokumentation & Implementierungsstand**

*Letzte Aktualisierung: 30.05.2026*  
*Status: 🔄 Finalisiert für Implementierung*

---

## **📁 Datei-Ablagestruktur & Architektur**

```
Assault/
│
├── core/
│   ├── game/
│   │   └── board.py                          # Board-Klasse (Hexfelder, Entities, Nachbarn, Idle-Kontrolle)
│   │
│   ├── entities/
│   │   ├── base_entity.py                    # Basis-Klasse für alle Entities (id, name, type, base_might, buffs, tags, might_split, alt, alt_entity, mighty_threshold)
│   │   ├── buff.py                           # Buff-Klasse (value, target, target_type) + Serialisierung
│   │   ├── figure.py                         # Figuren (erbt von BaseEntity, + self_alt_activation, cost, faction, AP_credit, placing)
│   │   ├── location.py                       # Locations (erbt von BaseEntity, Self-Buffs wirken nur bei Figur-Präsenz)
│   │   ├── vehicle.py                        # Vehicles (erbt von BaseEntity, + capacity)
│   │   ├── effect.py                         # Effekte (erbt von BaseEntity, + duration, cost, activation_cost)
│   │   └── entity_loader.py                  # Lädt Entities aus JSON-Dateien (nutzt BaseEntity.from_dict())
│   │
│   ├── managers/
│   │   ├── might_calculator.py               # Zentrales Berechnungstool für Might (Prioritätenreihenfolge, Buff-Logik)
│   │   ├── ap_manager.py                     # AP-Konto (Grundbetrag, Übertrag, Überziehung mit credit)
│   │   ├── round_manager.py                  # Steuerung der 9 Phasen pro Runde
│   │   └── idle_control.py                   # Idle-Kontrolle (Might-Verteilung, Threshold-Regel)
│   │
│   ├── utils/
│   │   ├── hex_id.py                         # HexID-Logik (Validierung, Nachbarn-Berechnung, Bereichsaufteilung)
│   │   ├── global_constants.py               # Farben, Fonts, Hexfeld-Größen, Dateipfade, FACTION_COLORS
│   │   ├── settings.py                       # Einstellungen (Sprache, Lautstärke)
│   │   └── translations.py                   # Zentrale Übersetzungen für DE/EN (TRANSLATIONS-Dict, get_translation())
│   │
│   └── tests/
│       └── init_test.py                      # Initialisierungstests (1–6: test entities 0000 auf hex id 0000, 7–8)
│
├── data/
│   ├── figurenwerk.json                      # Figuren-Daten (inkl. Dummy 0000)
│   ├── eterniaorte.json                      # Locations-Daten (inkl. Dummy 0000)
│   ├── effekte.json                          # Effekte-Daten (inkl. Dummy 0000)
│   ├── fahrzeuge.json                        # Vehicle-Daten (inkl. Dummy 0000 mit capacity)
│   ├── factions.json                         # Faction-Pools (Liste der Figuren-IDs pro Faction: Adam, Skeletor, Hordak, Zodak)
│   └── matches/                              # (Neu) Export-Ordner für Match-Daten (JSON/CSV)
│
├── interfaces/
│   ├── game_controller.py                    # Event-Handling (Tasten, Zahleneingabe, Mausklicks)
│   │
│   └── renderer/
│       └── pygame/
│           ├── screen.py                      # Screen-Klasse (Hintergrund + Buttons, 720p-Fenster)
│           ├── audio.py                       # AudioManager (MP3-Wiedergabe für Hintergrundmusik und Effekte)
│           ├── artwork/                       # Hintergrundbilder (JPG) und Musik (MP3)
│           │   ├── background.jpg
│           │   └── music/
│           │       ├── title_theme.mp3
│           │       ├── adam_theme.mp3
│           │       ├── skeletor_theme.mp3
│           │       ├── hordak_theme.mp3
│           │       └── zodak_theme.mp3
│           │
│           └── components/
│               ├── button.py                  # HexButton-Klasse (für UI-Interaktion)
│               ├── console.py                 # InGameConsole (Textkonsole für Log-Meldungen)
│               ├── game_status.py             # Anzeige für Spielstand (AP, Might, Idle-Kontrolle)
│               └── settings_menu.py           # Kontextmenü für Einstellungen (Sprache, Musik, Lautstärke)
│
├── settings.ini                               # Einstellungen (Sprache, Musik-Lautstärke, Effekt-Lautstärke)
├── simulation.py                             # Haupt-Testumgebung (720p-Fenster, Tasten 1–8 für Tests, Action-/Settings-Button)
└── main.py                                   # Einstiegspunkt (startet simulation.py)
```

---

## **🎮 Spielerlebnis & Programmstart**

---

### **📌 Startsequenz**

1. **Spielstart**
  - Spieler startet das Spiel über `main.py`.
  - **Hintergrund**: Initialisierung der Spiel-Engine (Pygame, Board, Entities) über `simulation.py`.
  - **Launch-Phase**:
    - **Automatisierte Tests** werden während des Starts durchgeführt (z. B. Board-Initialisierung, Entity-Loading).
    - **Ladebildschirm**: Optional (aktuell nicht nötig, da Ladezeit kurz).
2. **Spielerauswahl**
  - **Anzahl der Spieler**: Immer **2 Spieler** (Hotseat oder gegen KI oder KI gegen KI).
  - **Spielmodus**:
    - **Mensch vs. Mensch** (Hotseat).
    - **Mensch vs. Computer** (KI-Gegner).
    - **Computer vs. Computer** (für Simulationen und Balancing-Daten).
  - **Zweck von Computer vs. Computer**:
    - Ermöglicht **automatisierte Matches** zur Datenerfassung für **Balancing**. 
    - Wichtig für **Winrate-Analysen** pro Faction/Figur.
3. **Modus-Auswahl**
  - **Single Match**: Ein einzelnes Match entscheidet über Sieg/Verlust.
  - **Best of X Factions**:
    - **Win Condition**: Spieler muss mit **X verschiedenen Factions** gewinnen (X = 1, 2, 3, oder 4).
    - **Beispiel**:
      - **X = 1**: Single Match (1 Faction reicht).
      - **X = 2**: Spieler muss mit **2 verschiedenen Factions** gewinnen.
      - **X = 4**: Spieler muss mit **allen 4 Factions** gewinnen (Maximalvariante).
4. **Faction-Auswahl**
  - Beide Spieler wählen **jeweils eine Faction** aus den 4 verfügbaren Factions:
    - **Adam** (Good)
    - **Skeletor** (Evil)
    - **Hordak** (Evil, Horde)
    - **Zodak** (Neutral)
  - **Gleiche Faction erlaubt?**: **Ja, standardmäßig erlaubt** (wichtig für Simulationen!).  
  Optional: Einstellung, um **gleiche Factions zu verbieten** (z. B. für Balancing-Tests).
  - **Faction-Themes**:
    - **Musik**: Jede Faction hat ein **eigenes Musikthema** (MP3-Datei in `artwork/music/`).
    - **Farbschema**: Nutzt `FACTION_COLORS` aus `global_constants.py`.
5. **Match-Start**
  - Nach der Faction-Auswahl beginnt das **erste Match** (Runden 0–6).
  - **Siegbedingung pro Match**: Wer nach **7 Runden** (Runde 0–6) mehr Idle kontrolliert, gewinnt das Match.
6. **Spielende**
  - Nach jedem Match wird geprüft, ob die **Siegbedingung für das gesamte Spiel** erfüllt ist:
    - **Single Match (X=1)**: Sieg nach **1 Match**.
    - **Best of X Factions (X=2,3,4)**: Spiel endet, wenn ein Spieler mit **X verschiedenen Factions** gewonnen hat.
  - **Faction-Sperre**:
    - Wenn ein Spieler mit einer Faction gewonnen hat, **kann diese Faction nicht nochmal gewählt werden** (gilt für beide Spieler, auch in Simulation - diese verwendet nur single match).

---

### **📌 Interaktionsmöglichkeiten**


| **Element**         | **Interaktion**                                                           | **Status** | **Hinweise**                           |
| ------------------- | ------------------------------------------------------------------------- | ---------- | -------------------------------------- |
| **Tasten 1–8**      | Führt Tests in `simulation.py` aus.                                       | ✅          | Für Entwickler/Debugging.              |
| **Action-Button**   | Startet den nächsten Schritt im Spielablauf (z. B. Runde, Phase).         | ⏳          | UI-Integration nötig.                  |
| **Settings-Button** | Öffnet das Einstellungsmenü (Sprache, Musik, Lautstärke).                 | ✅          | Funktional in `settings_menu.py`.      |
| **Mausklicks**      | Auswahl von Hexfeldern/Figuren (Koordinaten werden in Konsole angezeigt). | ✅          | Konsolenausgabe mit `[USER]` markiert. |
| **Faction-Themes**  | Musik + Farbschema wechseln sofort nach Faction-Auswahl.                  | ⏳          | MP3-Dateien müssen vorhanden sein.     |
| **Effekte**         | Linksklick auf Button: Select → Deselect → Ausgegraut (deaktiviert).      | ⏳          | Rechtsklick wird nicht genutzt.        |


---

### **📌 UI & Visuelles Feedback**

- **Konsolenausgabe**:
  - Benutzerinputs werden mit `[USER]` markiert.
  - Mausklicks zeigen Koordinaten an.
  - Schriftgröße der Konsole: **20%** (für bessere Lesbarkeit).
- **Hintergrund**: Statisches Bild (`background.jpg`).
- **Farben**: Definiert in `global_constants.py` (z. B. `FACTION_COLORS`).
- **Buttons**: HexButton-Klasse für UI-Interaktion (z. B. Action-, Settings-Button).
- **Sprache**: Zweisprachigkeit über `get_translation` in `utils.translations`.
- **Idle-Kontrolle**: Farblicher Rahmen (Faction-Farbe) für Hexfelder mit Idle.

---

## **🎯 Spielregeln & Ablauf**

---

### **📌 Grundregeln**

- **Spieler**: 2 Spieler (Mensch oder KI).
- **Runden**: Jedes Match besteht aus **7 Runden (0–6)**.
- **Idle-Felder**: 3 Idle-Felder (`3011`, `3012`, `3013`), die kontrolliert werden müssen.
- **Siegbedingung**:
  - **Match**: Wer nach 7 Runden **mehr Idle kontrolliert**, gewinnt das Match.
  - **Spiel**: Bei **Best of X Factions** gewinnt der Spieler, der zuerst **X verschiedene Factions** erfolgreich einsetzt.

---

### **📌 Rundenablauf (9 Phasen pro Runde)**


| **Phase** | **Name**           | **Aktion**                                                                     | **Might-Berechnung** | **Idle-Kontrolle** | **AP-Relevanz**                                 |
| --------- | ------------------ | ------------------------------------------------------------------------------ | -------------------- | ------------------ | ----------------------------------------------- |
| **0**     | Initialisierung    | Übertrage Endstand aus Vorrunde (Might-Werte, Idle-Kontrolle, AP-Restbestand). | ❌                    | ❌                  | ✅ **AP + Rundennummer** (z. B. Runde 4 → +4 AP) |
| **1**     | Figur wählen       | Wähle Figur aus Preview-Bereich (Kosten: `cost`).                              | ❌                    | ❌                  | ✅ `cost` wird abgezogen.                        |
| **2**     | Marsch             | Alle Figuren bewegen sich **1 Feld vor**. Neue Figur wird platziert.           | ✅ **Ja**             | ❌                  | ❌                                               |
| **3**     | Might-Berechnung   | Berechne Might für **alle Entities** (nach Marsch).                            | ✅ **Ja**             | ✅ **Ja**           | ❌                                               |
| **4**     | Positionskorrektur | 2 Figuren mit `placing: true` können Positionen tauschen (einmal pro Runde).   | ✅ **Ja**             | ❌                  | ❌                                               |
| **5**     | Might-Berechnung   | **Neuberechnung** nach Positionstausch.                                        | ✅ **Ja**             | ✅ **Ja**           | ❌                                               |
| **6**     | Effekte kaufen     | Kaufe Effekte mit `cost` (oder erhalte automatische Belohnungen).              | ❌                    | ❌                  | ✅ `cost` wird abgezogen.                        |
| **7**     | Effekte auslösen   | Aktiviere Effekte mit `activation_cost`.                                       | ✅ **Ja**             | ✅ **Ja**           | ✅ `activation_cost` wird abgezogen.             |
| **8**     | Might-Berechnung   | **Finale Berechnung** nach Effektauslösung.                                    | ✅ **Ja**             | ✅ **Ja**           | ❌                                               |
| **9**     | Auswertung         | **Wer kontrolliert welche Idle?** (Siegbedingung: Alle 3 Idle = Sieg).         | ❌                    | ✅ **Ja**           | ❌                                               |


---

### **📌 Idle-Kontrolle & Might-Verteilung**

- **Idle-Felder und angrenzende Felder**:
  - **3011**: Spieler: `1111`, `1112`, `1213` | Gegner: `2111`, `2112`, `2213`.
  - **3012**: Spieler: `1213`, `1114`, `1215` | Gegner: `2213`, `2114`, `2215`.
  - **3013**: Spieler: `1215`, `1116`, `1117` | Gegner: `2215`, `2116`, `2117`.
- **Might-Verteilung**:
  - Der **gesamte Might** einer Entity wird nach `might_split` auf die **angrenzenden Idle-Felder** verteilt.
  - **Beispiel**: Figur mit `might: 20` und `might_split: [0.7, 0.3]` → **Idle 3011: +14**, **Idle 3012: +6**.
- **Threshold-Regel**:
  - Wenn ein Spieler an einem Idol `**Might >= 30**` erreicht, behält er dieses Idol **dauerhaft** (auch wenn der Gegner später mehr Might hat).
  - **Falls kein Threshold gerissen wurde**: Der Spieler mit der **höheren Might** am Rundenende kontrolliert das Idol.

---

## **🎮 Kernmechaniken**

---

### **🔹 1. Might-Berechnung**

**Definition**:  
`Might = base_might + Summe aller Buff-Values` (nach strikter **Prioritätenreihenfolge**).


| **Priorität** | **Buff-Typ** | **Beschreibung**                                                                     | **Beispiel**                              |
| ------------- | ------------ | ------------------------------------------------------------------------------------ | ----------------------------------------- |
| 1             | `base_might` | Grundstärke der Entity.                                                              | Figur: `10`, Location: `5`                |
| 2             | `neighbor`   | Buffs von **angrenzenden Entities (links/rechts)**.                                  | `{"value": +1, "target_type": "faction"}` |
| 3             | `opponent`   | Buffs von **gegenüberliegender Entity** (spiegelbildlich, auch bei Idol dazwischen). | `{"value": -1, "target": "Evil"}`         |
| 4             | `faction`    | Buffs für alle Entities der gleichen Faction.                                        | `{"value": +3, "target": "Good"}`         |
| 5             | `targeted`   | Buffs für spezifische Entities (per ID oder Name).                                   | `{"value": +5, "target": "1111"}`         |
| 6             | `self`       | **Sonderfall**: Buffs der Entity selbst (wirken **nur bei Alt-State**).              | `{"value": +2, "target": "self"}`         |


**Hinweise zur Buff-Logik**:

- **Neighbor-Buffs**: Nur **links und rechts** (maximal 2 Nachbarn pro Hexfeld).
- **Opponent-Buffs**: Nur das **direkt gegenüberliegende Hexfeld** (auch wenn ein Idol dazwischenliegt).
- **Buffs wirken auf die Entity selbst** (nicht auf das Hexfeld).
- **Self-Buffs**: Nur aktiv, wenn die Entity im **Alt-State** ist (gilt für Figuren und Effekte; Locations/Vehicles haben keinen Alt-State).

**Might-Split**:

- Jede Entity hat ein `might_split: List[float]` (Default: `[0.5, 0.5]`).
- **Maximalwerte** der `might_split`-Listen der Entities auf dem Feld werden genommen.
  - **Beispiel**: Figur: `[0.5, 0.5]`, Location: `[1.0, 1.0]`, Effekt: `[0.3, 0.7]` → `**might_split = [1.0, 1.0]**` (Maxima).

**Mighty-Status**:

- Ab `**Might >= 20**` gilt eine Entity als **"Mighty"** und erhält **Immunitäten** (z. B. gegen negative Buffs).

---

### **🔹 2. Alt-State von Entities**

**Definition**: Jede Entity hat einen **alternativen Zustand** (`alt = True/False`), der **andere Buff-Values** aktiviert.


| **Entity-Typ** | **Aktivierungsbedingung**                       | **Kosten**                                        | **Self-Buff wirkt**      |
| -------------- | ----------------------------------------------- | ------------------------------------------------- | ------------------------ |
| **Figur**      | `self_alt_activation: true` + `activation_cost` | `activation_cost` (einmalig)                      | Nur wenn `alt = True`.   |
| **Effekt**     | Kauf (`cost`) + Aktivierung (`activation_cost`) | `cost` (einmalig) + `activation_cost` (pro Runde) | Nur wenn `alt = True`.   |
| **Location**   | **Automatisch**, wenn Figur darauf steht.       | **Keine Kosten**                                  | Ja (wenn Figur präsent). |


**Standardwert für `self_alt_activation**`:

- `**false**` für die meisten Figuren.
- `**true**` für bestimmte Figuren (in `figurenwerk.json` explizit markiert, z. B. Helden).

---

### **🔹 3. Buff-System**

**Buff-Klasse (`core/entities/buff.py`):**

```python
@dataclass
class Buff:
    value: int                  # Buff-Value (positiv/negativ)
    target: Optional[str] = None  # Ziel: "self", "Good", "Evil", ID, etc.
    target_type: Optional[str] = None  # Typ: "self", "faction", "pool", "tag", "id"
```


| **Buff-Typ**      | **Aktivierungsbedingung**                                                         | **Beispiel**                                                |
| ----------------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| **Self-Buff**     | Nur aktiv, wenn die Entity im **Alt-State** ist.                                  | `{"value": +2, "target": "self", "target_type": "self"}`    |
| **Neighbor-Buff** | Aktiv, wenn die Entity **angrenzend (links/rechts)** zu einer anderen Entity ist. | `{"value": +1, "target": "Good", "target_type": "faction"}` |
| **Opponent-Buff** | Aktiv, wenn die Entity **gegenüber** einer anderen Entity steht.                  | `{"value": -1, "target": "Evil", "target_type": "faction"}` |
| **Faction-Buff**  | Aktiv, wenn die Entity zur **Faction/Tag** des Buffs gehört.                      | `{"value": +3, "target": "Good", "target_type": "faction"}` |
| **Targeted-Buff** | Aktiv, wenn die Entity **explizit das Ziel** des Buffs ist (ID/Name).             | `{"value": +5, "target": "1111", "target_type": "id"}`      |


---

### **🔹 4. AP-System (Assault Points)**

**AP-Konto:**

- **Pro Match** (nicht pro Runde).
- **Grundbetrag pro Runde**: Runde 0: 0 AP, Runde 1: +1 AP, Runde 2: +2 AP, ..., Runde 6: +6 AP.
- **Übertrag**: Nicht verbrauchte AP bleiben auf dem Konto (kumulativ).
- **Anzeige**: `"AP: X"` (z. B. `"AP: 6"` in Runde 4 mit 2 AP Restbestand aus Runde 3).

**AP-Kosten:**


| **Aktion**           | **Kosten**        | **Entity-Typ** |
| -------------------- | ----------------- | -------------- |
| Figur platzieren     | `cost`            | Figur          |
| Alt-State aktivieren | `activation_cost` | Figur/Effekt   |
| Effekt kaufen        | `cost`            | Effekt         |
| Effekt aktivieren    | `activation_cost` | Effekt         |


**AP-Überziehung mit `credit`:**

- **Jedes Entity** (Figur, Effekt, Location, Vehicle) kann `AP_credit` verschaffen.
- **Alternative**: `AP_credit` kann **pro Hexfeld** überwacht werden (nicht zwingend an Figuren gebunden).
- **Wirkung**: Ermöglicht **AP-Überziehung** (AP-Konto kann negativ sein).

**Kostenlose Figuren**:

- **4 Heroes** (je eine pro Faction: Adam, Skeletor, Hordak, Zodak) + **generische Figuren** (Royal Guard, Horda, Biest, Energiewesen) haben `**cost: 0**`. 
- **Zweck**: Jeder Spieler kann **jede Runde mindestens eine Figur platzieren**, selbst bei 0 AP.

**Effekte**:

- **Kaufkosten (`cost`)**: Einmalig, um den Effekt freizuschalten.
- **Aktivierungskosten (`activation_cost`)**: Pro Runde fällig, wenn der Effekt **dauerhaft** aktiv ist.
- **Deaktivierung**: Bei Deaktivierung (per Linksklick: Select → Deselect → Ausgegraut) werden die AP-Kosten **sofort zurückerstattet**. 
- **Duration**:
  - **Standard**: Dauerhaft (Kosten pro Runde).
  - `**duration: 1**`: Effekt wirkt nur in der **aktuellen Runde** (in Folgerunden ausgegraut).

---

### **🏷️ Spiel-Entitäten**


| **Entity-Typ** | **Attribute**                                                                                 | **Spezifika**                                                                              |
| -------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **Figur**      | `base_might`, `might_split`, `faction`, `AP_credit`, `self_alt_activation`, `cost`, `placing` | Kann Positionen tauschen (`placing: true`). Alt-State aktivierbar.                         |
| **Location**   | `base_might`, `might_split`, `buffs` (Self-Buffs wirken nur bei Figur-Präsenz)                | Keine Kosten, keine Aktivierung. Self-Buffs wirken automatisch, wenn Figur darauf steht.   |
| **Effekt**     | `base_might`, `might_split`, `cost`, `activation_cost`, `duration` (dauerhaft?)               | `cost`: Kaufkosten. `activation_cost`: Kosten pro Aktivierung (pro Runde, wenn dauerhaft). |
| **Vehicle**    | `base_might`, `might_split`, `capacity` (Anzahl Figuren)                                      | Kein Alt-State, keine Aktivierungskosten.                                                  |


**Gemeinsame Attribute für alle Entities:**  
`id`, `name`, `type`, `base_might`, `buffs`, `tags`, `might_split`, `alt`, `alt_entity`, `mighty_threshold`.

---

## **🏆 Siegbedingungen**

- **Idle-Kontrolle**: Nach jeder Runde wird geprüft, wer welche Idle kontrolliert.
- **Match-Sieg**: Ein Spieler gewinnt, wenn er **alle 3 Idle in einer Runde** kontrolliert.
- **Spiel-Sieg**: Ein Spieler gewinnt, wenn er **X verschiedene Factions** erfolgreich einsetzt (X = 1–4).

---

## **📊 Match-Export & Datenanalyse**

---

### **📌 Export-Datei pro Match**

- **Zweck**: Erfassung von **Balancing-Daten** (Winrates pro Faction/Figur).
- **Dateiformat**: **JSON**. 
- **Speicherort**: `data/matches/` (neuer Ordner).

### **📌 Struktur der Export-Datei**

```json
{
  "metadata": {
    "timestamp": "2026-05-30T12:00:00Z",
    "match_id": "unique_id_12345",
    "game_mode": "Single Match",
    "players": [
      {"type": "human", "faction": "Adam", "difficulty": null},
      {"type": "ai", "faction": "Skeletor", "difficulty": "random"}
    ],
    "duration": "00:05:23"
  },
  "results": {
    "winner": "player1",
    "win_condition": "Alle 3 Idle kontrolliert",
    "factions_used": ["Adam"],
    "battles": [
      {
        "battle_id": 1,
        "player1_faction": "Adam",
        "player2_faction": "Skeletor",
        "winner": "player1",
        "rounds": 7,
        "idle_control": {"3011": "player1", "3012": "player1", "3013": "player2"},
        "figures_played": {
          "player1": ["1110", "1111", "1112"],
          "player2": ["2110", "2111", "2112"]
        },
        "might_history": [
          {"round": 0, "player1_might": [10, 5, 0], "player2_might": [8, 6, 0]},
          {"round": 1, "player1_might": [12, 7, 0], "player2_might": [9, 4, 0]}
        ]
      }
    ],
    "figure_stats": {},
    "faction_stats": {}
  }
}
```

### **📌 Anforderungen an den Export**

- **Header**: Metadaten (Timestamp, Spieler, Modus, Schwierigkeit).
- **Match-Daten**:
  - **Battles**: Liste aller gespielten Matches (inkl. Runden, Idle-Kontrolle, gespielte Figuren).
  - **Figure Stats**: Winrate pro Figur (für Balancing) – *post-hoc* berechnet.
  - **Faction Stats**: Winrate pro Faction (für Balancing) – *post-hoc* berechnet.
- **Automatisierung**:
  - Export **automatisch nach jedem Match** (nicht erst am Spielende).
  - **Dateiname**: `match_{timestamp}_{match_id}.json`.

---

## **🤖 KI-Gegner (für Simulationen)**


| **Anforderung**            | **Details**                                                             | **Status** | **Notizen**                    |
| -------------------------- | ----------------------------------------------------------------------- | ---------- | ------------------------------ |
| **KI-Schwierigkeitsgrade** | `random` (zufällig), `maxed` (high) oder `refined` (optimiert, später). | ⏳          | `random` für erste Tests.      |
| **KI-Entscheidungen**      | **Zufällig**: Faction-Wahl, Figurenauswahl, Effekte, Züge.              | ✅          | Keine Strategie in Phase 1.    |
| **Simulationen**           | **Computer vs. Computer**: Automatisierte Matches für Balancing-Daten.  | ⏳          | Export der Ergebnisse in JSON. |


---

## **📜 Anforderungen & Implementierungsstand**

---

### **🎯 Grundlegendes**


| **Anforderung**                    | **Details**                                               | **Status** | **Notizen**                      |
| ---------------------------------- | --------------------------------------------------------- | ---------- | -------------------------------- |
| **Titel**                          | *Assault on Grayskull* (EN) / *Sturm auf Grayskull* (DE). | ✅          | Zweideutigkeit gewollt.          |
| **Sprachunterstützung**            | Englisch (Standard) + Deutsch (optional).                 | ✅          | JSON-Daten unterstützen beide.   |
| **Spielmodi**                      | Single Match, Best of X Factions.                         | ✅          | &nbsp;                           |
| **Übersetzungen**                  | Zentrale Übersetzungen in `translations.py`.              | ✅          | Neu hinzugefügt.                 |
| **Sprachauswahl (UI)**             | Deutsch/Englisch (Standard: Englisch).                    | ✅          | In `settings.ini` speichern.     |
| **Musik-Einstellung (UI)**         | An/Aus + Lautstärke (Schieberegler).                      | ✅          | In `settings.ini` speichern.     |
| **Hintergrundmusik**               | Titelmusik + Faction-Themes.                              | ⏳          | MP3-Dateien in `artwork/music/`. |
| **Faction-Themes (Musik + Farbe)** | Musik + Farbschema wechseln je nach Faction.              | ⏳          | Nutzt `FACTION_COLORS`.          |


---

### **🎮 Spielerlebnis & UI**


| **Anforderung**             | **Details**                                              | **Status** | **Notizen**                    |
| --------------------------- | -------------------------------------------------------- | ---------- | ------------------------------ |
| **Menü & Einstellungen**    | Sprachauswahl, Musik, Lautstärke.                        | ✅          | `settings_menu.py` funktional. |
| **Hintergrundbild**         | Statisches Bild (keine Animation).                       | ✅          | JPG in `artwork/`.             |
| **Konsolenausgabe**         | Benutzerinputs mit `[USER]`, Mausklicks mit Koordinaten. | ✅          | Schriftgröße: 20%.             |
| **720p-Fenster**            | Standardgröße für UI.                                    | ✅          | &nbsp;                         |
| **Action-/Settings-Button** | UI-Buttons für Spielsteuerung.                           | ✅          | `button.py` implementiert.     |
| **Idle-Kontrolle (UI)**     | Farblicher Rahmen (Faction-Farbe) für Idle-Felder.       | ⏳          | &nbsp;                         |


---

### **🎮 Kernmechaniken**


| **Anforderung**      | **Details**                             | **Status** | **Notizen**                              |
| -------------------- | --------------------------------------- | ---------- | ---------------------------------------- |
| **Might-Berechnung** | Prioritätenreihenfolge, Buff-Logik.     | ⏳          | `might_calculator.py` zu implementieren. |
| **Might-Split**      | Maximalwerte der Entities auf dem Feld. | ⏳          | &nbsp;                                   |
| **Mighty-Status**    | Immunitäten ab `Might >= 20`.           | ⏳          | &nbsp;                                   |
| **Alt-State**        | Alternativer Zustand für Entities.      | ⏳          | `self_alt_activation` in JSON.           |
| **Buff-System**      | Buff-Klasse implementiert.              | ⏳          | `buff.py` zu finalisieren.               |
| **AP-System**        | AP-Konto, Kostenabzug, Überziehung.     | ⏳          | `ap_manager.py` zu implementieren.       |
| **Idle-Kontrolle**   | Might-Verteilung, Threshold-Regel.      | ⏳          | `idle_control.py` zu implementieren.     |


---

### **🔄 Spielablauf & Phasen**


| **Anforderung**        | **Details**                                              | **Status** | **Notizen**                           |
| ---------------------- | -------------------------------------------------------- | ---------- | ------------------------------------- |
| **9 Phasen pro Runde** | Initialisierung, Marsch, Might-Berechnung, Effekte, etc. | ⏳          | `round_manager.py` zu implementieren. |
| **Rundenablauf (0–6)** | 7 Runden pro Match.                                      | ⏳          | &nbsp;                                |
| **Siegbedingungen**    | Alle 3 Idle kontrollieren = Match-Sieg.                  | ⏳          | Threshold: `Might >= 30`.             |


---

### **🏷️ Spiel-Entitäten**


| **Entity-Typ** | **Status** | **Notizen**                           |
| -------------- | ---------- | ------------------------------------- |
| **Figure**     | ✅          | `figure.py` implementiert.            |
| **Location**   | ✅          | `location.py` implementiert.          |
| **Effect**     | ✅          | `effect.py` implementiert.            |
| **Vehicle**    | ⏳          | `vehicle.py` vorhanden, Daten fehlen. |


---

### **📋 JSON-Datenbanken**


| **Datei**          | **Status** | **Notizen**                     |
| ------------------ | ---------- | ------------------------------- |
| `figurenwerk.json` | ✅          | Figuren (inkl. Dummy `0000`).   |
| `eterniaorte.json` | ✅          | Locations (inkl. Dummy `0000`). |
| `effekte.json`     | ✅          | Effekte (inkl. Dummy `0000`).   |
| `fahrzeuge.json`   | ⏳          | Vehicles (inkl. Dummy `0000`).  |
| `factions.json`    | ✅          | Faction-Pools.                  |


---

### **📁 Module & Klassen**


| **Modul/Klasse**  | **Status** | **Beschreibung**                | **Datei**                               |
| ----------------- | ---------- | ------------------------------- | --------------------------------------- |
| `BaseEntity`      | ✅          | Basis-Klasse für alle Entities. | `core/entities/base_entity.py`          |
| `Buff`            | ⏳          | Buff-Klasse + Serialisierung.   | `core/entities/buff.py`                 |
| `Figure`          | ✅          | Figuren-Logik.                  | `core/entities/figure.py`               |
| `Location`        | ✅          | Locations-Logik.                | `core/entities/location.py`             |
| `Effect`          | ✅          | Effekte-Logik.                  | `core/entities/effect.py`               |
| `Vehicle`         | ✅          | Vehicles-Logik.                 | `core/entities/vehicle.py`              |
| `HexID`           | ✅          | Hexfeld-ID-Logik.               | `core/game/hex_id.py`                   |
| `Board`           | ✅          | Hexfeld-Verwaltung.             | `core/game/board.py`                    |
| `MightCalculator` | ⏳          | Zentrale Might-Berechnung.      | `core/managers/might_calculator.py`     |
| `APManager`       | ⏳          | AP-Konto.                       | `core/managers/ap_manager.py`           |
| `RoundManager`    | ⏳          | Steuerung der 9 Phasen.         | `core/managers/round_manager.py`        |
| `IdleControl`     | ⏳          | Idle-Kontrolle.                 | `core/managers/idle_control.py`         |
| `EntityLoader`    | ⏳          | Lädt Entities aus JSON.         | `core/entities/entity_loader.py`        |
| `GlobalConstants` | ✅          | Farben, Fonts, Pfade.           | `core/utils/global_constants.py`        |
| `Translations`    | ✅          | Übersetzungen für DE/EN.        | `core/utils/translations.py`            |
| `Settings`        | ✅          | Einstellungen.                  | `core/utils/settings.py`                |
| `GameController`  | ✅          | Eingabe-Handling.               | `interfaces/game_controller.py`         |
| `Screen`          | ✅          | Pygame-Screen.                  | `interfaces/renderer/pygame/screen.py`  |
| `Console`         | ✅          | Textkonsole.                    | `interfaces/renderer/pygame/console.py` |
| `AudioManager`    | ✅          | MP3-Wiedergabe.                 | `interfaces/renderer/pygame/audio.py`   |
| `Simulation`      | ✅          | Testumgebung.                   | `simulation.py`                         |
| `Main`            | ✅          | Einstiegspunkt.                 | `main.py`                               |


---

### **🎯 Offene Aufgaben (Priorisiert)**


| **Aufgabe**                          | **Priorität** | **Abhängigkeiten**               | **Notizen**                                  |
| ------------------------------------ | ------------- | -------------------------------- | -------------------------------------------- |
| `fahrzeuge.json` erweitern           | 🟢 Niedrig    | Keine                            | Dummy-Vehicle `0000` mit `capacity`.         |
| `**MightCalculator` implementieren** | 🔴 **Hoch**   | `BaseEntity`, `Board`, `HexID`   | Might pro Hexfeld + Buff-Logik.              |
| `**APManager` implementieren**       | 🔴 **Hoch**   | `BaseEntity`, `Figure`, `Effect` | AP-Konto + Überziehung (`AP_credit`).        |
| `**RoundManager` implementieren**    | 🔴 **Hoch**   | `MightCalculator`, `APManager`   | Steuerung der 9 Phasen.                      |
| `**IdleControl` implementieren**     | 🔴 **Hoch**   | `MightCalculator`, `Board`       | Might-Verteilung + Threshold-Regel (`>=30`). |
| **UI für Faction-Themes**            | 🟡 Mittel     | `FACTION_COLORS`, `AudioManager` | Musik + Rahmenfarben für Idle-Kontrolle.     |
| **KI-Implementierung (`random`)**    | 🟡 Mittel     | Keine                            | Zufällige Entscheidungen.                    |
| **Match-Export-Funktionalität**      | 🟡 Mittel     | Keine                            | JSON-Export nach jedem Match.                |


---

## **💡 Legende**

- ✅ **Done**: Implementiert und getestet.
- ⏳ **In Progress**: Teilweise implementiert oder in Arbeit.
- 🔴 **Hoch**: Kritisch für lauffähigen Prototypen.
- 🟡 **Mittel**: Wichtig, aber nicht blockierend.
- 🟢 **Niedrig**: Kann später folgen.

---

## **📅 Nächste Schritte**

1. `**MightCalculator` implementieren** (Might pro Hexfeld + Buff-Logik).
2. `**APManager` implementieren** (AP-Konto + Überziehung).
3. `**RoundManager` implementieren** (Steuerung der 9 Phasen).
4. `**IdleControl` implementieren** (Might-Verteilung + Threshold-Regel).
5. **UI für Faction-Themes** (Musik + Rahmenfarben für Idle-Kontrolle).
6. **KI-Implementierung (`random`)** für erste Tests.
7. **Match-Export-Funktionalität** für Balancing-Daten.
8. `**fahrzeuge.json` finalisieren** (Dummy-Daten für Vehicles).