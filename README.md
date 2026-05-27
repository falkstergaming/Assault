# Assault
Coding Assault
# 📋 **Anforderungs-Tracking**

*Status: ✅ Finalisiert | ⏳ Offen | ❌ Nicht relevant*  
*Letzte Aktualisierung: 27.05.2026*

---

## **🎯 Grundlegendes**


| **Anforderung**     | **Beschreibung**                               | **Status** | **Notizen** |
| ------------------- | ---------------------------------------------- | ---------- | ----------- |
| Titel (EN/DE)       | *Assault on Grayskull* / *Sturm auf Grayskull* | ✅          | -           |
| Sprachunterstützung | Englisch (Standard) + Deutsch (optional)       | ✅          | -           |
| Spielmodi           | Single Match, Best of X Factions               | ✅          | -           |


---

## **🎮 Kernmechaniken**

### **📌 Might-Berechnung**


| **Anforderung**   | **Beschreibung**                                                                                                         | **Status** | **Notizen**               |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------ | ---------- | ------------------------- |
| **Definition**    | Might = `Base Might` + Summe aller Buff-Values (Prioritäten: Self → Neighbor → Opponent → Faction → Targeted → Location) | ✅          | Impl. in `base_entity.py` |
| **Grenzen**       | Minimum: `0`, Maximum: kein festes Limit                                                                                 | ✅          | -                         |
| **Mighty-Status** | Ab `Might > 20`: Immunitäten (z. B. gegen negative Buffs)                                                                | ✅          | -                         |
| **Might-Split**   | Individuelle Aufteilung pro Entity (Default: `[0.5, 0.5]`), Summe kann **> 1.0** sein                                    | ✅          | -                         |


### **📌 Alt-State**


| **Anforderung**   | **Beschreibung**                                                         | **Status** | **Notizen**                  |
| ----------------- | ------------------------------------------------------------------------ | ---------- | ---------------------------- |
| **Aktivierung**   | Kostenlos, restricted (Runden-Count, Hold-Idle-Count, Effekte 5xxx/9xxx) | ✅          | -                            |
| **Deaktivierung** | Manuell durch Spieler oder Gegner-Effekte/Spezial-Locations              | ✅          | -                            |
| **Scope**         | **Nur für 4 Heroes** (Adam, Skeletor, Hordak, Zodak)                     | ✅          | `alt_entity` nur für diese 4 |


### **📌 Buffs & Immunitäten**


| **Anforderung**            | **Beschreibung**                                                                                  | **Status** | **Notizen** |
| -------------------------- | ------------------------------------------------------------------------------------------------- | ---------- | ----------- |
| **Buff-Typen**             | `self`, `neighbor`, `opponent`, `faction`, `targeted`                                             | ✅          | -           |
| **Buff-Struktur**          | Jeder Buff: `value` (int), `target` (str/None), `target_type` (str/None)                          | ✅          | -           |
| **Target-Einschränkungen** | `target_type`: `"self"`, `"faction"`, `"pool"`, `"tag"`, `"id"`                                   | ✅          | -           |
| **Immunitäten**            | `buff_types` (Liste), `buff_targets` (Liste), `buff_values` (`"negative"`, `"positive"`, `"all"`) | ✅          | -           |


---

## **💰 Assault Points (AP)**


| **Anforderung**           | **Beschreibung**                                                      | **Status** | **Notizen**              |
| ------------------------- | --------------------------------------------------------------------- | ---------- | ------------------------ |
| **Konto-Modell**          | Pro Match (nicht pro Runde), Anzeige: `"AP: X"`                       | ✅          | UI in `screen.py`        |
| **Grundbetrag pro Runde** | Runde 0: 0 AP, Runde 1–6: +1–6 AP (kumulativ)                         | ⏳          | Fehlt in `ap_manager.py` |
| **Übertrag**              | Nicht verbrauchte AP bleiben auf dem Konto                            | ⏳          | Fehlt in `ap_manager.py` |
| **Kredit-System**         | Factions/Figuren mit `credit: 1-2` können AP überziehen               | ⏳          | Fehlt in `ap_manager.py` |
| **AP-Quellen**            | Idle-Kontrolle (+1 AP/Runde), Locations (+X AP), Effekte (`bonus_ap`) | ⏳          | Fehlt in `ap_manager.py` |
| **AP-Nutzung**            | Effekte kaufen (`cost`), Effekte aktivieren (`activation_cost`)       | ⏳          | Fehlt in `ap_manager.py` |


---

## **🏷️ Spiel-Entitäten**


| **Entity-Typ**      | **Anforderung**                                                                          | **Status** | **Notizen**           |
| ------------------- | ---------------------------------------------------------------------------------------- | ---------- | --------------------- |
| **Figur**           | `base_might`, `might_split`, `immunity`, `mobility`, `scout_vision`, `special_abilities` | ✅          | `figure.py`           |
| **Location**        | Wie Figur, aber `base_might: 0`, `mobility.range: 0`, `scout_vision: 0`                  | ✅          | `location.py`         |
| **Effekt**          | Wie Figur, aber `active: bool`, `cost`, `activation_cost`, `bonus_ap`                    | ✅          | `effect.py`           |
| **Transportmittel** | Wie Figur, aber `type: "vehicle"`                                                        | ⏳          | Fehlt in `vehicle.py` |
| **Faction**         | `pool` (Liste der Figuren-IDs), **kein `credit**` (über Figuren gelöst)                  | ✅          | `factions.json`       |


---

## **🔄 Spielablauf & Phasen**


| **Phase**          | **Anforderung**                                                                                                                                                                | **Status** | **Notizen**                 |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------- | --------------------------- |
| **1–9 pro Runde**  | 1. Figur wählen, 2. Marsch, 3. Might-Berechnung, 4. Positionskorrektur, 5. Might-Berechnung, 6. Effekte kaufen, 7. Effekte anwenden, 8. Finale Might-Berechnung, 9. Auswertung | ⏳          | Fehlt in `round_manager.py` |
| **Idle-Kontrolle** | Nach Phase 3, 5, 8: Vergleich der Might aller angrenzenden Figuren (max. 3 pro Seite)                                                                                          | ⏳          | Teilweise in `board.py`     |
| **Belohnungen**    | +1 AP/Runde für gehaltenes Idol, +2 AP als Comeback-Bonus                                                                                                                      | ⏳          | Fehlt in `round_manager.py` |


---

## **🏆 Siegbedingungen**


| **Anforderung**    | **Beschreibung**                                             | **Status** | **Notizen**                 |
| ------------------ | ------------------------------------------------------------ | ---------- | --------------------------- |
| **Idle-Kontrolle** | Nach jeder Runde: Wer hat mehr Might auf einem Idol?         | ⏳          | Teilweise in `board.py`     |
| **Sieg**           | Gewonnen, wenn alle Idles in einer Runde kontrolliert werden | ⏳          | Fehlt in `round_manager.py` |


---

## **🎨 Optik & UI/UX**


| **Anforderung**        | **Beschreibung**                                                                          | **Status** | **Notizen**          |
| ---------------------- | ----------------------------------------------------------------------------------------- | ---------- | -------------------- |
| **Immer sichtbar**     | Modus, Battle Count, Rundenanzeige, AP-Konto, Idols-Status, aktuelle Phase, Mighty-Status | ⏳          | Fehlt in `screen.py` |
| **Spielfeld**          | Verdeckte Locations (grau/nebelartig), enthüllt durch `scout_vision`                      | ⏳          | Fehlt in `screen.py` |
| **Effekte in der Bar** | Aktiv: hervorgehoben, deaktiviert: ausgegraut, verbraucht: durchgestrichen                | ⏳          | Fehlt in `screen.py` |
| **Farben**             | Aus `global_constants.py` (z. B. `COLORS["background"]`, `COLORS["text"]`)                | ✅          | `screen.py`          |
| **Hintergrundbild**    | JPG aus `interfaces/renderer/pygame/artwork/`                                             | ✅          | `screen.py`          |
| **Audio**              | MP3 aus `interfaces/renderer/pygame/artwork/`                                             | ✅          | `audio.py`           |
| **Zahleneingabe**      | Eingabe von Zahlen (z. B. für AP-Management) über `GameController`                        | ✅          | `game_controller.py` |


---

## **📊 Technische Anforderungen**


| **Anforderung**           | **Beschreibung**                                                                                    | **Status** | **Notizen**     |
| ------------------------- | --------------------------------------------------------------------------------------------------- | ---------- | --------------- |
| **Datenbanken**           | JSON-Dateien: `figurenwerk.json`, `eterniaorte.json`, `effects.json`, `factions.json`               | ✅          | Fertig          |
| **Einheitliche Struktur** | Alle Entities haben: `id`, `name`, `type`, `base_might`, `buffs`, `immunity`, `might_split`, `tags` | ✅          | Fertig          |
| **Code-Standards**        | Globale Konstanten in `global_constants.py`, Docstrings für alle Funktionen                         | ✅          | Fertig          |
| **Simulationsumgebung**   | 720p-Fenster mit Konsolenausgabe (für Tests der Kernlogik)                                          | ✅          | `simulation.py` |


---

## **🔧 Offene technische Aufgaben**


| **Aufgabe**          | **Beschreibung**                                                                 | **Priorität** | **Status** |
| -------------------- | -------------------------------------------------------------------------------- | ------------- | ---------- |
| **Might-Calculator** | Berechnet Might für alle Entities (Prioritäten, Buffs, Immunitäten, Might-Split) | 🔴 Hoch       | ⏳          |
| **AP-Manager**       | AP-Konto (Grundbetrag, Bonus-AP, Kredit)                                         | 🔴 Hoch       | ⏳          |
| **Round-Manager**    | 9 Phasen pro Runde (Figur wählen, Marsch, Effekte kaufen, etc.)                  | 🔴 Hoch       | ⏳          |
| **State Machines**   | Zustandsverwaltung für Runden und Spielablauf                                    | 🟡 Mittel     | ⏳          |
| **UI-Erweiterung**   | Buttons, Highlighting, Mouseover-Tooltips                                        | 🟡 Mittel     | ⏳          |
| **Vehicle-Klasse**   | Transportmittel-Implementierung                                                  | 🟢 Niedrig    | ⏳          |


---

## **📅 Letzte Prüfung**

- **Datum:** 27.05.2026
- **Geprüft von:** Christian Heb
- **Nächste Prüfung:** Offene Punkte priorisieren (🔴 Hoch)

---

### **💡 Legende**

- ✅ **Finalisiert**: Implementiert und getestet.
- ⏳ **Offen**: Noch nicht implementiert.
- 🔴 **Hoch**: Kritisch für lauffähigen Prototypen.
- 🟡 **Mittel**: Wichtig, aber nicht blockierend.
- 🟢 **Niedrig**: Kann später folgen.

# Projektdokumentation
# 📋 **Anforderungs-Tracking**

*Status: ✅ Finalisiert | ⏳ Offen | ❌ Nicht relevant*  
*Letzte Aktualisierung: 27.05.2026*

---

## **🎯 Grundlegendes**


| **Anforderung**     | **Beschreibung**                               | **Status** | **Notizen** |
| ------------------- | ---------------------------------------------- | ---------- | ----------- |
| Titel (EN/DE)       | *Assault on Grayskull* / *Sturm auf Grayskull* | ✅          | -           |
| Sprachunterstützung | Englisch (Standard) + Deutsch (optional)       | ✅          | -           |
| Spielmodi           | Single Match, Best of X Factions               | ✅          | -           |


---

## **🎮 Kernmechaniken**

### **📌 Might-Berechnung**


| **Anforderung**   | **Beschreibung**                                                                                                         | **Status** | **Notizen**               |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------ | ---------- | ------------------------- |
| **Definition**    | Might = `Base Might` + Summe aller Buff-Values (Prioritäten: Self → Neighbor → Opponent → Faction → Targeted → Location) | ✅          | Impl. in `base_entity.py` |
| **Grenzen**       | Minimum: `0`, Maximum: kein festes Limit                                                                                 | ✅          | -                         |
| **Mighty-Status** | Ab `Might > 20`: Immunitäten (z. B. gegen negative Buffs)                                                                | ✅          | -                         |
| **Might-Split**   | Individuelle Aufteilung pro Entity (Default: `[0.5, 0.5]`), Summe kann **> 1.0** sein                                    | ✅          | -                         |


### **📌 Alt-State**


| **Anforderung**   | **Beschreibung**                                                         | **Status** | **Notizen**                  |
| ----------------- | ------------------------------------------------------------------------ | ---------- | ---------------------------- |
| **Aktivierung**   | Kostenlos, restricted (Runden-Count, Hold-Idle-Count, Effekte 5xxx/9xxx) | ✅          | -                            |
| **Deaktivierung** | Manuell durch Spieler oder Gegner-Effekte/Spezial-Locations              | ✅          | -                            |
| **Scope**         | **Nur für 4 Heroes** (Adam, Skeletor, Hordak, Zodak)                     | ✅          | `alt_entity` nur für diese 4 |


### **📌 Buffs & Immunitäten**


| **Anforderung**            | **Beschreibung**                                                                                  | **Status** | **Notizen** |
| -------------------------- | ------------------------------------------------------------------------------------------------- | ---------- | ----------- |
| **Buff-Typen**             | `self`, `neighbor`, `opponent`, `faction`, `targeted`                                             | ✅          | -           |
| **Buff-Struktur**          | Jeder Buff: `value` (int), `target` (str/None), `target_type` (str/None)                          | ✅          | -           |
| **Target-Einschränkungen** | `target_type`: `"self"`, `"faction"`, `"pool"`, `"tag"`, `"id"`                                   | ✅          | -           |
| **Immunitäten**            | `buff_types` (Liste), `buff_targets` (Liste), `buff_values` (`"negative"`, `"positive"`, `"all"`) | ✅          | -           |


---

## **💰 Assault Points (AP)**


| **Anforderung**           | **Beschreibung**                                                      | **Status** | **Notizen**              |
| ------------------------- | --------------------------------------------------------------------- | ---------- | ------------------------ |
| **Konto-Modell**          | Pro Match (nicht pro Runde), Anzeige: `"AP: X"`                       | ✅          | UI in `screen.py`        |
| **Grundbetrag pro Runde** | Runde 0: 0 AP, Runde 1–6: +1–6 AP (kumulativ)                         | ⏳          | Fehlt in `ap_manager.py` |
| **Übertrag**              | Nicht verbrauchte AP bleiben auf dem Konto                            | ⏳          | Fehlt in `ap_manager.py` |
| **Kredit-System**         | Factions/Figuren mit `credit: 1-2` können AP überziehen               | ⏳          | Fehlt in `ap_manager.py` |
| **AP-Quellen**            | Idle-Kontrolle (+1 AP/Runde), Locations (+X AP), Effekte (`bonus_ap`) | ⏳          | Fehlt in `ap_manager.py` |
| **AP-Nutzung**            | Effekte kaufen (`cost`), Effekte aktivieren (`activation_cost`)       | ⏳          | Fehlt in `ap_manager.py` |


---

## **🏷️ Spiel-Entitäten**


| **Entity-Typ**      | **Anforderung**                                                                          | **Status** | **Notizen**           |
| ------------------- | ---------------------------------------------------------------------------------------- | ---------- | --------------------- |
| **Figur**           | `base_might`, `might_split`, `immunity`, `mobility`, `scout_vision`, `special_abilities` | ✅          | `figure.py`           |
| **Location**        | Wie Figur, aber `base_might: 0`, `mobility.range: 0`, `scout_vision: 0`                  | ✅          | `location.py`         |
| **Effekt**          | Wie Figur, aber `active: bool`, `cost`, `activation_cost`, `bonus_ap`                    | ✅          | `effect.py`           |
| **Transportmittel** | Wie Figur, aber `type: "vehicle"`                                                        | ⏳          | Fehlt in `vehicle.py` |
| **Faction**         | `pool` (Liste der Figuren-IDs), **kein `credit**` (über Figuren gelöst)                  | ✅          | `factions.json`       |


---

## **🔄 Spielablauf & Phasen**


| **Phase**          | **Anforderung**                                                                                                                                                                | **Status** | **Notizen**                 |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------- | --------------------------- |
| **1–9 pro Runde**  | 1. Figur wählen, 2. Marsch, 3. Might-Berechnung, 4. Positionskorrektur, 5. Might-Berechnung, 6. Effekte kaufen, 7. Effekte anwenden, 8. Finale Might-Berechnung, 9. Auswertung | ⏳          | Fehlt in `round_manager.py` |
| **Idle-Kontrolle** | Nach Phase 3, 5, 8: Vergleich der Might aller angrenzenden Figuren (max. 3 pro Seite)                                                                                          | ⏳          | Teilweise in `board.py`     |
| **Belohnungen**    | +1 AP/Runde für gehaltenes Idol, +2 AP als Comeback-Bonus                                                                                                                      | ⏳          | Fehlt in `round_manager.py` |


---

## **🏆 Siegbedingungen**


| **Anforderung**    | **Beschreibung**                                             | **Status** | **Notizen**                 |
| ------------------ | ------------------------------------------------------------ | ---------- | --------------------------- |
| **Idle-Kontrolle** | Nach jeder Runde: Wer hat mehr Might auf einem Idol?         | ⏳          | Teilweise in `board.py`     |
| **Sieg**           | Gewonnen, wenn alle Idles in einer Runde kontrolliert werden | ⏳          | Fehlt in `round_manager.py` |


---

## **🎨 Optik & UI/UX**


| **Anforderung**        | **Beschreibung**                                                                          | **Status** | **Notizen**          |
| ---------------------- | ----------------------------------------------------------------------------------------- | ---------- | -------------------- |
| **Immer sichtbar**     | Modus, Battle Count, Rundenanzeige, AP-Konto, Idols-Status, aktuelle Phase, Mighty-Status | ⏳          | Fehlt in `screen.py` |
| **Spielfeld**          | Verdeckte Locations (grau/nebelartig), enthüllt durch `scout_vision`                      | ⏳          | Fehlt in `screen.py` |
| **Effekte in der Bar** | Aktiv: hervorgehoben, deaktiviert: ausgegraut, verbraucht: durchgestrichen                | ⏳          | Fehlt in `screen.py` |
| **Farben**             | Aus `global_constants.py` (z. B. `COLORS["background"]`, `COLORS["text"]`)                | ✅          | `screen.py`          |
| **Hintergrundbild**    | JPG aus `interfaces/renderer/pygame/artwork/`                                             | ✅          | `screen.py`          |
| **Audio**              | MP3 aus `interfaces/renderer/pygame/artwork/`                                             | ✅          | `audio.py`           |
| **Zahleneingabe**      | Eingabe von Zahlen (z. B. für AP-Management) über `GameController`                        | ✅          | `game_controller.py` |


---

## **📊 Technische Anforderungen**


| **Anforderung**           | **Beschreibung**                                                                                    | **Status** | **Notizen**     |
| ------------------------- | --------------------------------------------------------------------------------------------------- | ---------- | --------------- |
| **Datenbanken**           | JSON-Dateien: `figurenwerk.json`, `eterniaorte.json`, `effects.json`, `factions.json`               | ✅          | Fertig          |
| **Einheitliche Struktur** | Alle Entities haben: `id`, `name`, `type`, `base_might`, `buffs`, `immunity`, `might_split`, `tags` | ✅          | Fertig          |
| **Code-Standards**        | Globale Konstanten in `global_constants.py`, Docstrings für alle Funktionen                         | ✅          | Fertig          |
| **Simulationsumgebung**   | 720p-Fenster mit Konsolenausgabe (für Tests der Kernlogik)                                          | ✅          | `simulation.py` |


---

## **🔧 Offene technische Aufgaben**


| **Aufgabe**          | **Beschreibung**                                                                 | **Priorität** | **Status** |
| -------------------- | -------------------------------------------------------------------------------- | ------------- | ---------- |
| **Might-Calculator** | Berechnet Might für alle Entities (Prioritäten, Buffs, Immunitäten, Might-Split) | 🔴 Hoch       | ⏳          |
| **AP-Manager**       | AP-Konto (Grundbetrag, Bonus-AP, Kredit)                                         | 🔴 Hoch       | ⏳          |
| **Round-Manager**    | 9 Phasen pro Runde (Figur wählen, Marsch, Effekte kaufen, etc.)                  | 🔴 Hoch       | ⏳          |
| **State Machines**   | Zustandsverwaltung für Runden und Spielablauf                                    | 🟡 Mittel     | ⏳          |
| **UI-Erweiterung**   | Buttons, Highlighting, Mouseover-Tooltips                                        | 🟡 Mittel     | ⏳          |
| **Vehicle-Klasse**   | Transportmittel-Implementierung                                                  | 🟢 Niedrig    | ⏳          |


---

## **📅 Letzte Prüfung**

- **Datum:** 27.05.2026
- **Geprüft von:** Christian Heb
- **Nächste Prüfung:** Offene Punkte priorisieren (🔴 Hoch)

---

### **💡 Legende**

- ✅ **Finalisiert**: Implementiert und getestet.
- ⏳ **Offen**: Noch nicht implementiert.
- 🔴 **Hoch**: Kritisch für lauffähigen Prototypen.
- 🟡 **Mittel**: Wichtig, aber nicht blockierend.
- 🟢 **Niedrig**: Kann später folgen.
