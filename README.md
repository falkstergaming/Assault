# 📜 **Anforderungen & Implementierungsstand - Assault on Grayskull / Sturm auf Grayskull**

*Letzte Aktualisierung: 29.05.2026*  
*Status: ✅ Finalisiert für Implementierung*

---

## **📁 Datei-Ablagestruktur**

```
Assault/
│
├── core/
│   ├── __init__.py
│   │
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── base_entity.py      # Basis-Klasse (Attribute: id, base_might, buffs, alt, might_split, etc.)
│   │   ├── buff.py             # Buff-Klasse (value, target, target_type) + Serialisierung
│   │   ├── figure.py           # Erbt von BaseEntity + self_alt_activation
│   │   ├── location.py         # Erbt von BaseEntity (Self-Buffs nur bei Figur-Präsenz)
│   │   ├── effect.py           # Erbt von BaseEntity + duration, cost, activation_cost
│   │   └── vehicle.py          # Erbt von BaseEntity + capacity
│   │
│   ├── game/
│   │   ├── __init__.py
│   │   ├── board.py            # Hexfeld-Verwaltung, Nachbarn, Idle-Kontrolle
│   │   └── hex_id.py           # HexID-Klasse (Validierung, Nachbarn)
│   │
│   ├── managers/
│   │   ├── __init__.py
│   │   ├── might_calculator.py # **Zentrale Might-Berechnung** (nutzt BaseEntity-Attribute)
│   │   ├── ap_manager.py       # AP-Konto (Grundbetrag, Übertrag, Überziehung mit credit)
│   │   └── round_manager.py    # Steuerung der 9 Phasen pro Runde
│   │
│   └── utils/
│       ├── __init__.py
│       └── global_constants.py # Farben, Fonts, Hexfeld-Größen, Dateipfade
│
├── data/
│   ├── figurenwerk.json       # Figuren (inkl. Dummy 0000)
│   ├── eterniaorte.json       # Locations (inkl. Dummy 0000)
│   ├── effects.json           # Effekte (inkl. Dummy 0000)
│   ├── vehicles.json          # Vehicles (inkl. Dummy 0000)
│   └── factions.json          # Faction-Pools (Liste der Figuren-IDs pro Faction)
│
├── interfaces/
│   ├── game_controller.py     # Eingabe-Handling (Tasten, Zahleneingabe)
│   │
│   └── renderer/
│       └── pygame/
│           ├── __init__.py
│           ├── audio.py       # AudioManager (MP3-Wiedergabe)
│           ├── screen.py       # Screen-Klasse (Hintergrund, Text-Rendering)
│           ├── artwork/        # JPG/MP3-Dateien für UI
│           │   ├── background.jpg
│           │   └── music.mp3
│           │
│           └── components/
│               └── console.py  # Textkonsole für Log-Meldungen
│
├── main.py                    # Einstiegspunkt (startet Simulation)
└── simulation.py              # Testumgebung (720p-Fenster, Tasten 1–8 für Tests)

└── README.md                  # Projektdokumentation (Anforderungen, Architektur)
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
- **Sieg**: Ein Spieler gewinnt, wenn er **alle 3 Idle in einer Runde** kontrolliert.

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