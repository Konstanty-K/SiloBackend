# SiloBackend - REST API dla systemu SiloMonitor

SiloBackend to serwerowa część systemu SiloMonitor, zapewniająca centralny punkt gromadzenia i udostępniania danych telemetrycznych z monitorowanych silosów zbożowych. [cite_start]Zbudowany w języku Python z wykorzystaniem frameworka FastAPI, serwer obsługuje asynchroniczną wymianę danych z aplikacją mobilną.

## 🚀 Architektura i Główne Cechy

* **FastAPI:** Wysokowydajny framework do budowy API w języku Python, zapewniający asynchroniczność (AsyncIO) i automatyczne generowanie dokumentacji (Swagger UI).
* **Architektura Delta Sync:** API wspiera optymalizację przesyłu danych poprzez filtrowanie zapytań (np. po parametrze `location_id`). [cite_start]Aplikacja mobilna pobiera tylko niezbędny pakiet danych, co oszczędza pasmo.
* [cite_start]**Zarządzanie Hierarchiczne:** System odwzorowuje rzeczywistą strukturę sprzętową: MCU (Microcontroller Unit) -> Silosy (kombinacja ID i portu) -> Macierz Pomirowa (sondy × poziomy).
* **Wsparcie dla Architektury Offline-First (Mobile):** API zostało zaprojektowane tak, aby współpracować z aplikacją kliencką w trybie offline-first. [cite_start]Serwer dostarcza pełne ładunki danych w formacie JSON, które są następnie synchronizowane z lokalną bazą SQLite na urządzeniu mobilnym.

## 📊 Struktura Danych i Kontrakty (JSON)

Głównym formatem wymiany danych jest JSON. [cite_start]Struktura opiera się na hierarchii stacji pomiarowych (MCU) i podłączonych do nich silosów.

### Model Danych - `MCU` (Stacja Główna)

| Pole | Typ | Opis |
| :--- | :--- | :--- |
| `id` | `String` | [cite_start]Unikalny identyfikator mikrokontrolera (np. `MCU_PROD_123`). |
| `location_id` | `String` | Identyfikator logiczny lokalizacji (np. `LOC_001` dla Poznania). |
| `ext_temp` | `Float` | [cite_start]Zewnętrzna temperatura otoczenia (w °C). |
| `ext_hum` | `Int` / `Float` | [cite_start]Względna wilgotność zewnętrzna (w %). |
| `timestamp` | `Long` | [cite_start]Czas pomiaru w formacie Epoch Milliseconds. |
| `silos` | `Array[Object]` | [cite_start]Lista obiektów reprezentujących podłączone silosy. |

### Model Danych - `Silo` (Zbiór Sond)

| Pole | Typ | Opis |
| :--- | :--- | :--- |
| `id` | `String` | [cite_start]Unikalny ID silosu (Klucz Złożony: Hardware ID + Numer Portu, np. `S_01_POZ`). |
| `average_temp` | `Float` | [cite_start]Wyliczona średnia temperatura z całej macierzy. |
| `matrix_data` | `Array[Array[Float]]` | Dwuwymiarowa macierz odczytów. [cite_start]Każdy wiersz to pojedyncza sonda sznurkowa, każda kolumna to poziom głębokości. |

## 📡 Endpoints API

### 1. Pobieranie danych stacji (Synchronizacja)

Służy do pobierania historycznych danych telemetrycznych.

* **Endpoint:** `/api/mcus`
* **Metoda:** `GET`
* **Parametry Zapytania (Query Params):**
    * [cite_start]`location_id` (Opcjonalny) - Filtrowanie wyników dla konkretnej lokalizacji (np. `?location_id=LOC_001`).

#### Przykładowa Odpowiedź (200 OK)
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
🔐 Rejestracja Urządzeń (QR Skaner)Aplikacja mobilna wykorzystuje moduł wizyjny (ML Kit) do wstrzykiwania zminimalizowanych ładunków konfiguracyjnych z fizycznych urządzeń, pomijając pełną synchronizację początkową.  Format danych QR (Hardware ID Tag) oczekiwany przez aplikację, który wyzwala późniejsze zapytania do API:JSON{
  "mcu_id": "MCU_PROD_123",
  "active_ports": [1, 2, 3]
}
🛠️ Uruchomienie Serwera Lokalnie (Development)Wymagania: Python 3.9+Sklonuj repozytorium.Zainstaluj wymagane pakiety:Bashpip install fastapi uvicorn
Uruchom serwer developerski:Bashuvicorn main:app --reload
Dokumentacja API (Swagger UI) będzie dostępna pod adresem: http://127.0.0.1:8000/docsProjekt zrealizowany jako część inżynierskiego systemu monitoringu silosów zbożowych.   
Ten dokument podsumowuje kontrakty pomiędzy serwerem a aplikacją mobilną, opierając się na architekturze zdefiniowanej w poprzednich krokach. Zwróciłem szczególną uwagę na udokumentowanie punktów końcowych oraz struktury JSON, które są kluczowe dla poprawnej komunikacji z aplikacją kliencką napisaną w Kotlinie.
