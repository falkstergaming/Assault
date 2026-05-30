# 📜 **Anforderungen & Implementierungsstand - Assault on Grayskull / Sturm auf Grayskull**

*Letzte Aktualisierung: 29.05.2026*  
*Status: ✅ Finalisiert für Implementierung*

---

## **📁 Datei-Ablagestruktur**

```
Assault/
│
├── core/
│   ├── game/
│   │   └── board.py                  # Board-Klasse (Hexfelder, Entities)
│   │
│   ├── entities/
│   │   ├── base_entity.py            # Basis-Klasse für Entities
│   │   ├── figure.py                 # Figuren
│   │   ├── location.py               # Locations
│   │   └── effect.py                 # Effekte
│   │
│   ├── utils/
│   │   ├── hex_id.py                 # HexID-Logik
│   │   └── global_constants.py       # Farben, Konstanten
│   │
│   └── tests/                        # ✅ NEU: Test-Module
│       └── init_test.py              # Initialisierungstests (1–5, 7–8)
│
├── data/
│   ├── figurenwerk.json              # Figuren-Daten
│   ├── eterniaorte.json              # Locations-Daten
│   ├── effekte.json                  # Effekte-Daten
│   └── fahrezuge.json                # Vehicle-Daten
│
├── interfaces/
│   ├── game_controller.py            # Event-Handling (später)
│   │
│   └── renderer/
│       └── pygame/
│           ├── screen.py              # Screen-Klasse (Hintergrund + Buttons)
│           ├── artwork/               # Hintergrundbilder (JPG)
│           │   └── background.jpg
│           │
│           └── components/
│               ├── button.py          # HexButton-Klasse
│               └── console.py         # InGameConsole (bestehend)
│
├── simulation.py                     # Haupt-Testumgebung (mit Action-/Settings-Button)
└── main.py                           # Einstiegspunkt (startet simulation.py)
```

---

## **📜 Anforderungen**

---

### **🎯 Grundlegendes**


| **Anforderung**         | **Details**                                               | **Status** | **Notizen**                    |
| ----------------------- | --------------------------------------------------------- | ---------- | ------------------------------ |
| **Titel**               | *Assault on Grayskull* (EN) / *Sturm auf Grayskull* (DE). | ✅          | Zweideutigkeit gewollt.        |
| **Sprachunterstützung** | Englisch (Standard) + Deutsch (optional).                 | ✅          | JSON-Daten unterstützen beide. |
| **Spielmodi**           | Single Match, Best of X Factions.                         | ✅          | &nbsp;                         |


---

# **📜  0. Spielerlebnis**


## **🎮 Match-Ablauf & Programmstart**

### **📌 Startsequenz**

1. **Spielstart**:
  - Spieler startet das Spiel über `main.py`.
  - **Hintergrund**: Initialisierung der Spiel-Engine (Pygame, Board, Entities)über `init-test.py`.
  - **Launch-Phase**:
    - **Automatisierte Tests** werden während des Starts durchgeführt (z. B. Board-Initialisierung, Entity-Loading).
    - **Ladebildschirm**: Optional (aktuell nicht nötig, da Ladezeit kurz).
2. **Spielerauswahl**:
  - **Anzahl der Spieler**: Immer **2 Spieler** (Hotseat oder gegen KI).
  - **Spielmodus**:
    - **Mensch vs. Mensch** (Hotseat).
    - **Mensch vs. Computer** (KI-Gegner).
    - **Computer vs. Computer** (für Simulationen und Balancing-Daten).
  - **Zweck von Computer vs. Computer**:
    - Ermöglicht **automatisierte Matches** zur Datenerfassung für **Balancing**.
    - Wichtig für **Winrate-Analysen** pro Faction/Figur.
3. **Modus-Auswahl**:
  - **Single Match**: Ein einzelnes Match entscheidet über Sieg/Verlust.
  - **Best of X Factions**:
    - **Win Condition**: Spieler muss mit **X verschiedenen Factions** gewinnen (X = 1, 2, 3, oder 4).
    - **Beispiel**:
      - **X = 1**: Single Match (1 Faction reicht).
      - **X = 2**: Spieler muss mit **2 verschiedenen Factions** gewinnen.
      - **X = 4**: Spieler muss mit **allen 4 Factions** gewinnen (Maximalvariante).
  - **Faction-Wahl**:
    - Beide Spieler wählen **jeweils eine Faction** aus den 4 verfügbaren Factions:
      - **Adam** (Good)
      - **Skeletor** (Evil)
      - **Hordak** (Evil, Horde)
      - **Zodak** (Neutral)
    - **Gleiche Faction erlaubt?**
      - **Ja, standardmäßig erlaubt** (wichtig für Simulationen!).
      - Optional: Einstellung, um **gleiche Factions zu verbieten** (z. B. für Balancing-Tests).
4. **Faction-Auswahl**:
  - Nach der Modus-Auswahl wählen beide Spieler ihre Faction.
  - **Faction-Themes**:
    - **Musik**: Jede Faction hat ein **eigenes Musikthema** (MP3-Datei).
    - **Hintergrundbild**: Optional anpassbar pro Faction.
    - **Farbschema**: Nutzt `FACTION_COLORS` aus `global_constants.py` (z. B. Blau für Adam, Rot für Skeletor).
5. **Match-Start**:
  - Nach der Faction-Auswahl beginnt das **erste Match** (Runden 0–6).
  - **Siegbedingung pro Match**: Wer nach **7 Runden** (Runde 0–6) mehr Idle kontrolliert, gewinnt das Match.
6. **Spielende**:
  - Nach jedem Match wird geprüft, ob die **Siegbedingung für das gesamte Spiel** erfüllt ist:
    - **Single Match (X=1)**: Sieg nach **1 Match**.
    - **Best of X Factions (X=2,3,4)**: Spiel endet, wenn ein Spieler mit **X verschiedenen Factions** gewonnen hat.
  - **Faction-Sperre**:
    - Wenn ein Spieler mit einer Faction gewonnen hat, **kann diese Faction nicht nochmal gewählt werden** (gilt für beide Spieler).
    - **Ausnahme**: Bei **Computer vs. Computer** (Simulationen) kann diese Regel deaktiviert werden.

---

## **📊 Match-Export & Datenanalyse**

### **📌 Export-Datei pro Match**

- **Zweck**: Erfassung von **Balancing-Daten** (Winrates pro Faction/Figur).
- **Dateiformat**: **JSON oder CSV** (noch zu definieren).
- **Speicherort**: `data/matches/` (neuer Ordner).

### **📌 Struktur der Export-Datei**

```json
{
  "metadata": {
    "timestamp": "2026-05-29T12:00:00Z",
    "match_id": "unique_id_12345",
    "game_mode": "Best of 4 Factions",
    "players": [
      {
        "type": "human",
        "faction": "Adam",
        "difficulty": null  // Nur für KI
      },
      {
        "type": "ai",
        "faction": "Skeletor",
        "difficulty": "random"  // oder "refined" (später)
      }
    ],
    "duration": "00:05:23"  // Spielzeit
  },
  "results": {
    "winner": "player1",
    "win_condition": "2 Factions",
    "factions_used": ["Adam", "Zodak"],
    "battles": [
      {
        "battle_id": 1,
        "player1_faction": "Adam",
        "player2_faction": "Skeletor",
        "winner": "player1",
        "rounds": 7,
        "idle_control": {
          "3011": "player1",
          "3012": "player1",
          "3013": "player2"
        },
        "figures_played": {
          "player1": ["1110", "1111", "1112"],  // IDs der gespielten Figuren
          "player2": ["2110", "2111", "2112"]
        },
        "might_history": [
          {"round": 0, "player1_might": [10, 5, 0], "player2_might": [8, 6, 0]},
          {"round": 1, "player1_might": [12, 7, 0], "player2_might": [9, 4, 0]},
          // ... bis Runde 6
        ]
      },
      {
        "battle_id": 2,
        "player1_faction": "Zodak",
        "player2_faction": "Hordak",
        "winner": "player1",
        // ... weitere Battle-Daten
      }
    ],
    "figure_stats": {
      "1110": {"wins": 5, "losses": 2, "winrate": 0.714},
      "1111": {"wins": 3, "losses": 1, "winrate": 0.750},
      // ... für alle gespielten Figuren
    },
    "faction_stats": {
      "Adam": {"wins": 2, "losses": 0, "winrate": 1.0},
      "Skeletor": {"wins": 0, "losses": 2, "winrate": 0.0},
      // ... für alle Factions
    }
  }
}
```

### **📌 Anforderungen an den Export**

- **Header**: Metadaten (Timestamp, Spieler, Modus, Schwierigkeit).
- **Match-Daten**:
  - **Battles**: Liste aller gespielten Matches (inkl. Runden, Idle-Kontrolle, gespielte Figuren).
  - **Figure Stats**: Winrate pro Figur (für Balancing).
  - **Faction Stats**: Winrate pro Faction (für Balancing).
- **Automatisierung**:
  - Export **automatisch nach jedem Match** (oder nach Spielende).
  - **Dateiname**: `match_{timestamp}_{match_id}.json` (z. B. `match_20260529_120000_12345.json`).

---

## **🎨 Spielerlebnis & UI**

### **📌 Menü & Einstellungen**


| **Anforderung**       | **Details**                                                           | **Status** | **Notizen**                   |
| --------------------- | --------------------------------------------------------------------- | ---------- | ----------------------------- |
| **Sprachauswahl**     | Deutsch/Englisch (Standard: Englisch).                                | ✅          | In `settings.ini` speichern.  |
| **Musik-Einstellung** | An/Aus + Lautstärke (Schieberegler).                                  | ✅          | In `settings.ini` speichern.  |
| **Hintergrundmusik**  | Titelmusik (Startbildschirm) + Faction-Themes (nach Faction-Auswahl). | ⏳          | MP3-Dateien in `artwork/`.    |
| **Hintergrundbild**   | Statisches Bild (keine Animation).                                    | ✅          | JPG in `artwork/`.            |
| **Faction-Themes**    | **Musik + Farbschema** ändern sich je nach gewählter Faction.         | ⏳          | Nutzt `FACTION_COLORS`.       |
| **Settings-Datei**    | `settings.ini` (speichert Sprache, Musik-Einstellungen, etc.).        | ✅          | Wird beim Spielstart geladen. |


### **📌 Faction-Themes**

- **Musik**:
  - **Titelmusik**: Wird beim Startbildschirm abgespielt.
  - **Faction-Themes**:
    - **Adam**: `artwork/music/adam_theme.mp3`
    - **Skeletor**: `artwork/music/skeletor_theme.mp3`
    - **Hordak**: `artwork/music/hordak_theme.mp3`
    - **Zodak**: `artwork/music/zodak_theme.mp3`
  - **Wechsel**: Musik wechselt **sofort nach Faction-Auswahl**.
- **Farbschema**:
  - Definiert in `global_constants.py` als `FACTION_COLORS`:
    ```python
    FACTION_COLORS = {
        "Adam": (0, 100, 200),      # Blau
        "Skeletor": (200, 0, 0),   # Rot
        "Hordak": (150, 0, 150),   # Lila
        "Zodak": (100, 100, 100)   # Grau
    }
    ```
  - Wird für **UI-Highlighting** (z. B. Rahmen, Text) genutzt.

---

## **🤖 KI-Gegner (für Simulationen)**


| **Anforderung**            | **Details**                                                            | **Status** | **Notizen**                    |
| -------------------------- | ---------------------------------------------------------------------- | ---------- | ------------------------------ |
| **KI-Schwierigkeitsgrade** | `random` (zufällig), `maxed` (high) oder `refined` (optimiert, später).| ⏳          | `random` für erste Tests.      |
| **KI-Entscheidungen**      | **Zufällig**: Faction-Wahl, Figurenauswahl, Effekte, Züge.             | ✅          | Keine Strategie in Phase 1.    |
| **Simulationen**           | **Computer vs. Computer**: Automatisierte Matches für Balancing-Daten. | ⏳          | Export der Ergebnisse in JSON. |


---

## **📌 Zusammenfassung der Spiel-Anforderungen**

### **🎮 Spiel-Ablauf**

1. **Spielerauswahl**: 2 Spieler (Mensch/Mensch, Mensch/KI, KI/KI).
2. **Modus-Auswahl**: Single Match oder Best of X Factions (X = 1–4).
3. **Faction-Auswahl**: 4 Factions (Adam, Skeletor, Hordak, Zodak), gleiche Faction **standardmäßig erlaubt**.
4. **Match-Start**: Runden 0–6, Siegbedingung pro Match.
5. **Spielende**: Prüfe Siegbedingung für das gesamte Spiel (Single Match oder Best of X).

### **📊 Daten-Export**

- **Automatischer Export** nach jedem Match/Spiel.
- **Inhalt**: Metadaten, Match-Daten, Figure Stats, Faction Stats.
- **Zweck**: Balancing-Analyse (Winrates pro Faction/Figur).

### **🎨 Spielerlebnis**

- **Sprachauswahl** (DE/EN) + **Musik-Einstellungen** (An/Aus, Lautstärke).
- **Faction-Themes**: Musik + Farbschema wechseln je nach gewählter Faction.
- **Settings-Datei**: `settings.ini` für Persistenz.

### **🤖 KI & Simulationen**

- **KI-Schwierigkeit**: `random` (Standard) oder `refined` (später).
- **Computer vs. Computer**: Für automatisierte Balancing-Tests.

---

## **📅 Nächste Schritte**

1. **Match-Ablauf implementieren**:
  - Spielerauswahl (Mensch/KI).
  - Modus-Auswahl (Single Match / Best of X).
  - Faction-Auswahl (mit Faction-Themes).
2. **Export-Funktionalität**:
  - JSON-Export für Matches (Metadaten + Statistiken).
  - Automatische Generierung nach Spielende.
3. **UI-Anpassungen**:
  - Menü für Sprache/Musik.
  - Faction-Themes (Musik + Farbschema).
4. **KI-Implementierung**:
  - Level easy `random`-Modus für erste Tests.
  - Level normal `maxed`-Modus später.
  - Level hard `refined`-Modus später.

---

### **🎮 Kernmechaniken**

---

#### **🔹 1. Might-Berechnung**

**Definition:**  
Might = `base_might` + Summe aller Buff-Values (nach strikter Prioritätenreihenfolge).


| **Priorität** | **Buff-Typ** | **Beschreibung**                                                            | **Beispiel**                              |
| ------------- | ------------ | --------------------------------------------------------------------------- | ----------------------------------------- |
| 1             | `base_might` | Grundstärke der Entity.                                                     | Figur: `10`, Location: `5`                |
| 2             | `self`       | Buffs der Entity selbst (wirken nur bei Alt-State oder Figur auf Location). | `{"value": +2, "target": "Adam"}`         |
| 3             | `neighbor`   | Buffs von angrenzenden Entities (Figuren, Locations, Effekte).              | `{"value": +1, "target_type": "faction"}` |
| 4             | `opponent`   | Buffs von gegenüberliegender Entity.                                        | `{"value": -1, "target": "Evil"}`         |
| 5             | `faction`    | Buffs für alle Entities der gleichen Faction.                               | `{"value": +3, "target": "Good"}`         |
| 6             | `targeted`   | Buffs für spezifische Entities (per ID oder Name).                          | `{"value": +5, "target": "1111"}`         |


**Might-Split:**

- Jede Entity hat ein `might_split: List[float]` (Default: `[0.5, 0.5]`).
- **Summe kann > 1.0 sein** (z. B. `[1.0, 1.0]` für volle Idle-Kontrolle).
- **Anwendung:** Might wird nach `might_split` auf **angrenzende Idle-Felder** verteilt.
  - Beispiel: Figur mit `might: 20` und `might_split: [0.7, 0.3]` → **Idle 3011: +14**, **Idle 3012: +6**.

**Mighty-Status:**

- Ab `Might >= 20` gilt eine Entity als **"Mighty"** und erhält **Immunitäten** (z. B. gegen negative Buffs).

---

#### **🔹 2. Alt-State**

**Definition:**  
Jede Entity hat einen **alternativen Zustand** (`alt = True/False`), der **andere Buff-Values** aktiviert.


| **Entity-Typ** | **Aktivierungsbedingung**                       | **Kosten**                                        | **Self-Buff wirkt**      |
| -------------- | ----------------------------------------------- | ------------------------------------------------- | ------------------------ |
| **Figur**      | `self_alt_activation: true` + `activation_cost` | `activation_cost` (einmalig)                      | Nur wenn `alt = True`.   |
| **Effekt**     | Kauf (`cost`) + Aktivierung (`activation_cost`) | `cost` (einmalig) + `activation_cost` (pro Runde) | Nur wenn `alt = True`.   |
| **Location**   | **Automatisch**, wenn Figur darauf steht.       | **Keine Kosten**                                  | Ja (wenn Figur präsent). |


---

#### **🔹 3. Buff-System**

**Buff-Klasse (`core/entities/buff.py`):**

```python
@dataclass
class Buff:
    value: int                  # Buff-Value (positiv/negativ)
    target: Optional[str] = None  # Ziel: "self", "Good", "Evil", ID, etc.
    target_type: Optional[str] = None  # Typ: "self", "faction", "pool", "tag", "id"
```


| **Buff-Typ**      | **Aktivierungsbedingung**                                                          | **Beispiel**                                                |
| ----------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| **Self-Buff**     | Immer aktiv (Figur/Effekt: nur bei `alt = True`; Location: nur bei Figur-Präsenz). | `{"value": +2, "target": "1111", "target_type": "id"}`      |
| **Neighbor-Buff** | Aktiv, wenn die Entity **angrenzend** zu einer anderen Entity ist.                 | `{"value": +1, "target": "Good", "target_type": "faction"}` |
| **Opponent-Buff** | Aktiv, wenn die Entity **gegenüber** einer anderen Entity steht.                   | `{"value": -1, "target": "Evil", "target_type": "faction"}` |
| **Faction-Buff**  | Aktiv, wenn die Entity zur **Faction/Tag** des Buffs gehört.                       | `{"value": +3, "target": "Good", "target_type": "faction"}` |
| **Targeted-Buff** | Aktiv, wenn die Entity **explizit das Ziel** des Buffs ist (ID/Name).              | `{"value": +5, "target": "1111", "target_type": "id"}`      |


---

#### **🔹 4. AP-System (Assault Points)**

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

- Entities mit `AP_credit: X` können **X AP überziehen** (z. B. `AP: -1`, aber `credit: 2` → kann noch 1 AP ausgeben).

---

---

### **🏷️ Spiel-Entitäten**


| **Entity-Typ** | **Attribute**                                                                      | **Spezifika**                                                                              |
| -------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **Figur**      | `base_might`, `might_split`, `faction`, `AP_credit`, `self_alt_activation`, `cost` | Kann `placing: true` haben (Positionen tauschen). Alt-State aktivierbar.                   |
| **Location**   | `base_might`, `might_split`, `buffs` (Self-Buffs wirken nur bei Figur-Präsenz)     | Keine Kosten, keine Aktivierung. Self-Buffs wirken automatisch, wenn Figur darauf steht.   |
| **Effekt**     | `base_might`, `might_split`, `cost`, `activation_cost`, `duration` (dauerhaft?)    | `cost`: Kaufkosten. `activation_cost`: Kosten pro Aktivierung (pro Runde, wenn dauerhaft). |
| **Vehicle**    | `base_might`, `might_split`, `capacity` (Anzahl Figuren)                           | Kein Alt-State, keine Aktivierungskosten.                                                  |


**Gemeinsame Attribute für alle Entities:**

- `id`, `name`, `type`, `base_might`, `buffs`, `tags`, `might_split`, `alt`, `alt_entity`, `mighty_threshold`.

---

---

## **🔄 Spielablauf & Phasen**

### **Rundenablauf (9 Phasen pro Runde)**


| **Phase** | **Name**           | **Aktion**                                                                     | **Might-Berechnung** | **Idle-Kontrolle** | **AP-Relevanz**                                 |
| --------- | ------------------ | ------------------------------------------------------------------------------ | -------------------- | ------------------ | ----------------------------------------------- |
| **0**     | Initialisierung    | Übertrage Endstand aus Vorrunde (Might-Werte, Idle-Kontrolle, AP-Restbestand). | ❌                    | ❌                  | ✅ **AP + Rundennummer** (z. B. Runde 4 → +4 AP) |
| **1**     | Figur wählen       | Wähle Figur aus Preview-Bereich (Kosten: `cost`).                              | ❌                    | ❌                  | ✅ `cost` wird abgezogen.                        |
| **2**     | Marsch             | Alle Figuren bewegen sich **1 Feld vor**. Neue Figur wird platziert.           | ✅ **Ja**             | ❌                  | ❌                                               |
| **3**     | Might-Berechnung   | Berechne Might für **alle Entities** (nach Marsch).                            | ✅ **Ja**             | ✅ **Ja**           | ❌                                               |
| **4**     | Positionskorrektur | Figuren mit `placing: true` können Positionen tauschen.                        | ✅ **Ja**             | ❌                  | ❌                                               |
| **5**     | Might-Berechnung   | **Neuberechnung** nach Positionstausch.                                        | ✅ **Ja**             | ✅ **Ja**           | ❌                                               |
| **6**     | Effekte kaufen     | Kaufe Effekte mit `cost` (oder erhalte automatische Belohnungen).              | ❌                    | ❌                  | ✅ `cost` wird abgezogen.                        |
| **7**     | Effekte auslösen   | Aktiviere Effekte mit `activation_cost`.                                       | ✅ **Ja**             | ✅ **Ja**           | ✅ `activation_cost` wird abgezogen.             |
| **8**     | Might-Berechnung   | **Finale Berechnung** nach Effektauslösung.                                    | ✅ **Ja**             | ✅ **Ja**           | ❌                                               |
| **9**     | Auswertung         | **Wer kontrolliert welche Idle?** (Siegbedingung: Alle 3 Idle = Sieg).         | ❌                    | ✅ **Ja**           | ❌                                               |


---

### **Idle-Kontrolle**

- **Idle-Felder**: `3011`, `3012`, `3013`.
- **Angrenzende Felder**:
  - **3011**: Spieler: `1111`, `1112`, `1213` | Gegner: `2111`, `2112`, `2213`.
  - **3012**: Spieler: `1213`, `1114`, `1215` | Gegner: `2213`, `2114`, `2215`.
  - **3013**: Spieler: `1215`, `1116`, `1117` | Gegner: `2215`, `2116`, `2117`.

**Might-Verteilung:**

- Der **gesamte Might** einer Entity wird nach `might_split` auf die **angrenzenden Idle-Felder** verteilt.
- **Threshold-Regel**:
  - Wenn ein Spieler an einem Idol `**Might >= 20**` erreicht, behält er dieses Idol **dauerhaft** (auch wenn der Gegner später mehr Might hat).
  - **Falls kein Threshold gerissen wurde**: Der Spieler mit der **höheren Might** am Rundenende kontrolliert das Idol.

---

## **🏆 Siegbedingungen**

- **Idle-Kontrolle**: Nach jeder Runde wird geprüft, wer welche Idle kontrolliert.
- **Match-Sieg**: Ein Spieler gewinnt, wenn er **alle 3 Idle in einer Runde** kontrolliert.
- **Spiel-Sieg**: Ein Spieler mit so vielen Factions gewinnt, wie vereinbart wurde (min 1, max 4)

---

---

## **📊 Implementierungsstand**

---

### **✅ Finalisierte Module/Klassen**


| **Modul/Klasse**  | **Status** | **Beschreibung**                                               | **Datei**                                          |
| ----------------- | ---------- | -------------------------------------------------------------- | -------------------------------------------------- |
| `BaseEntity`      | ✅          | Basis-Klasse mit allen Attributen (keine Might-Logik).         | `core/entities/base_entity.py`                     |
| `Buff`            | ✅          | Buff-Klasse (value, target, target_type) + Serialisierung.     | `core/entities/buff.py`                            |
| `Figure`          | ✅          | Erbt von `BaseEntity` + `self_alt_activation`.                 | `core/entities/figure.py`                          |
| `Location`        | ✅          | Erbt von `BaseEntity` (Self-Buffs nur bei Figur-Präsenz).      | `core/entities/location.py`                        |
| `Effect`          | ✅          | Erbt von `BaseEntity` + `duration`, `cost`, `activation_cost`. | `core/entities/effect.py`                          |
| `Vehicle`         | ✅          | Erbt von `BaseEntity` + `capacity`.                            | `core/entities/vehicle.py`                         |
| `HexID`           | ✅          | Hexfeld-ID mit Validierung und Nachbarn-Berechnung.            | `core/game/hex_id.py`                              |
| `Board`           | ✅          | Hexfeld-Verwaltung, Nachbarn, Idle-Kontrolle.                  | `core/game/board.py`                               |
| `GlobalConstants` | ✅          | Farben, Fonts, Hexfeld-Größen, Dateipfade.                     | `core/utils/global_constants.py`                   |
| `GameController`  | ✅          | Eingabe-Handling (Tasten, Zahleneingabe).                      | `interfaces/game_controller.py`                    |
| `Screen`          | ✅          | Pygame-Screen mit Hintergrund und Text-Rendering.              | `interfaces/renderer/pygame/screen.py`             |
| `Console`         | ✅          | Textkonsole für Log-Meldungen.                                 | `interfaces/renderer/pygame/components/console.py` |
| `AudioManager`    | ✅          | MP3-Wiedergabe für Hintergrundmusik.                           | `interfaces/renderer/pygame/audio.py`              |
| `Simulation`      | ✅          | Testumgebung mit 8 Tests (Tasten 1–8).                         | `simulation.py`                                    |
| `Main`            | ✅          | Einstiegspunkt (startet Simulation).                           | `main.py`                                          |


---

### **⏳ Offene Module/Klassen (Priorisiert)**


| **Modul/Klasse**      | **Priorität** | **Beschreibung**                                                                     | **Abhängigkeiten**                      | **Datei**                           |
| --------------------- | ------------- | ------------------------------------------------------------------------------------ | --------------------------------------- | ----------------------------------- |
| `**MightCalculator**` | 🔴 Hoch       | **Zentrale Might-Berechnung** (nutzt `BaseEntity`-Attribute, `Board`, `Buff`).       | `BaseEntity`, `Board`, `Buff`           | `core/managers/might_calculator.py` |
| `**APManager**`       | 🔴 Hoch       | AP-Konto (Grundbetrag, Übertrag, Überziehung mit `credit`).                          | `BaseEntity`                            | `core/managers/ap_manager.py`       |
| `**RoundManager**`    | 🔴 Hoch       | Steuerung der **9 Phasen pro Runde** (Initialisierung, Marsch, Effekte, Auswertung). | `Board`, `MightCalculator`, `APManager` | `core/managers/round_manager.py`    |
| `**IdleControl**`     | 🔴 Hoch       | Idle-Kontrolle (Might-Verteilung, Threshold-Regel).                                  | `Board`, `MightCalculator`              | `core/managers/idle_control.py`     |
| `**EntityLoader**`    | 🟡 Mittel     | Lädt Entities aus JSON-Dateien (nutzt `BaseEntity.from_dict()`).                     | `BaseEntity`                            | `core/entities/entity_loader.py`    |


---

### **📋 Offene JSON-Datenbanken**


| **Datei**          | **Status** | **Beschreibung**                                              |
| ------------------ | ---------- | ------------------------------------------------------------- |
| `figurenwerk.json` | ✅          | Figuren (inkl. Dummy `0000`).                                 |
| `eterniaorte.json` | ✅          | Locations (inkl. Dummy `0000`).                               |
| `effekte.json`     | ✅          | Effekte (inkl. Dummy `0000`).                                 |
| `fahrzeuge.json`   | ⏳          | **Fehlt noch**: Vehicles (inkl. Dummy `0000` mit `capacity`). |
| `factions.json`    | ✅          | Faction-Pools (Liste der Figuren-IDs pro Faction).            |


---

### **🎯 Nächste Schritte (Priorisiert)**

1. `**fahrzeuge.json` erweitern (mit Dummy-Vehicle `0000` erstellt).
2. `**MightCalculator` implementieren** (zentrale Might-Berechnung).
3. `**APManager` implementieren** (AP-Konto, Kostenabzug).
4. `**RoundManager` implementieren** (Phasen 0–9).
5. `**IdleControl` implementieren** (Might-Verteilung, Threshold-Regel).

---

### **💡 Legende**

- ✅ **Finalisiert**: Implementiert und getestet.
- ⏳ **Offen**: Noch nicht implementiert.
- 🔴 **Hoch**: Kritisch für lauffähigen Prototypen.
- 🟡 **Mittel**: Wichtig, aber nicht blockierend.
- 🟢 **Niedrig**: Kann später folgen.