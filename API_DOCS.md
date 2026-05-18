Dokumentacja REST APIOto profesjonalnie sformatowany plik .md, który podsumowuje strukturę Twojego Pythona. Skopiuj ten blok i zapisz jako API_DOCS.md w swoim repozytorium.Markdown# SiloMonitor - REST API Documentation

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
Struktura JSON (Schemat Typów)PoleTypOpisidStringUnikalny identyfikator mikrokontrolera (Klucz główny).location_idStringIdentyfikator logiczny lokalizacji (np. Poznań = LOC_001).ext_tempFloatZewnętrzna temperatura otoczenia (w °C).ext_humInt / FloatWzględna wilgotność zewnętrzna (w %).timestampLongCzas pomiaru w formacie Epoch Milliseconds.silosArray[Object]Lista obiektów reprezentujących podłączone silosy.Struktura obiektu Silo:PoleTypOpisidStringUnikalny ID silosu (np. S_01_POZ). Powinien składać się z numeru urządzenia i portu.average_tempFloatWyliczona średnia temperatura z całej macierzy.matrix_dataArray[Array[Float]]Macierz odczytów. Każda wiersz to pojedyncza sonda sznurkowa, każda kolumna to poziom głębokości.Moduł Rejestracji Urządzeń (QR Skaner)Podczas dodawania nowego urządzenia za pomocą systemu wizyjnego (QR Code z fizycznej skrzynki urządzenia), generowany jest zminimalizowany ładunek (Payload) służący do wstrzyknięcia kluczy złożonych do bazy lokalnej SQLite przed pełną synchronizacją.Format danych z kodu QR (Hardware ID Tag)JSON{
  "mcu_id": "MCU_PROD_123",
  "active_ports": [1, 2, 3]
}
Opis logiki: Kod QR nie zawiera historii pomiarów (oszczędność pamięci na mikrokontrolerze). Moduł wizyjny odczytuje aktywne porty i skleja je z mcu_id, po czym aplikacja mobilna asynchronicznie dociąga historyczną tablicę matrix_data z serwera REST.