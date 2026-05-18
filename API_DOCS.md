# SiloMonitor - REST API Documentation

Ten dokument opisuje strukturę i kontrakty danych dla komunikacji z serwerem bazowym (Python/FastAPI) wykorzystywanym w aplikacji SiloMonitor. Architektura opiera się na transferze danych telemetrycznych w formacie JSON.

## Architektura Danych

System opiera się na hierarchicznej strukturze urządzeń:
1. **MCU (Microcontroller Unit):** Główna stacja zbierająca dane dla danej lokalizacji. Posiada sensory środowiskowe (zewnętrzna temperatura i wilgotność).
2. **Silo (Zbiór Sond):** Fizyczny silos podłączony do MCU, identyfikowany przez unikalny ID będący kombinacją ID sprzętowego i numeru portu (np. `S_01`).
3. **Matrix Data:** Dwuwymiarowa tablica odczytów temperatur (Sondy × Poziomy wew. silosu).

---

## Endpoints

### 1. Pobieranie danych stacji (Synchronizacja UI)

Endpoint służy do synchronizacji aplikacji mobilnej z bazą danych na serwerze. Obsługuje filtrowanie po `location_id`, aby optymalizować użycie łącza (architektura Delta Sync).

* **URL:** `/api/mcus` *(ścieżka przykładowa)*
* **Metoda:** `GET`
* **URL Params:**
  * `location_id=[string]` (Opcjonalny) - Identyfikator lokalizacji, np. `LOC_001`.

#### Przykładowa Odpowiedź (Success - 200 OK)

```json
[
  {
    "id": "MCU_PROD_123",
    "location_id": "LOC_001",
    "ext_temp": 24.5,
    "ext_hum": 55,
    "timestamp": 1727056000000,
    "silos": [
      {
        "id": "S_01",
        "average_temp": 18.5,
        "matrix_data": [
          [15.0, 16.5, 18.0],
          [15.5, 17.0, 19.5],
          [14.0, 15.0, 16.0]
        ]
      }
    ]
  }
]