from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

'''Do testowania SiloMonitor v1.2, + Postman'''
app = FastAPI(title="SiloMonitor REST API", version="0.1.3")

# --- KONFIGURACJA CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- MODELE DANYCH (Pydantic) ---

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    operator_id: str
    expires_at: datetime


# --- MODELE DANYCH (SUROWE IoT - Bez aliasów) ---

class SiloStatus(BaseModel):
    id: str  # Np. "S_01", to id sprzętowe, NIE alias rolnika
    average_temp: float
    # Macierz: Zewnętrzna lista = Sondy (Kolumny), Wewnętrzna = Poziomy (Wiersze)
    matrix_data: List[List[Optional[float]]]


class McuStatus(BaseModel):
    id: str  # Hardware ID (np. MAC adres)
    location_id: str
    ext_temp: float
    ext_hum: int
    timestamp: int
    silos: List[SiloStatus]


# --- BAZA DANYCH W PAMIĘCI RAM ---
FAKE_TOKEN = "kk_rnd_secure_token_placeholder_for_phase_2"
db_mcus: List[McuStatus] = []


# --- ENDPOINTY (Trasy API) ---

@app.get("/")
def read_root():
    return {"status": "SiloMonitor API is ONLINE", "time": datetime.now()}


@app.post("/api/v1/auth/login", response_model=TokenResponse)
def login(request: LoginRequest):
    print(f"DEBUG: Próba logowania: {request.username}")
    if request.username == "Admin" and request.password == "1234":
        return TokenResponse(access_token=FAKE_TOKEN, operator_id="OP_001", expires_at=datetime.now())
    else:
        raise HTTPException(status_code=401, detail="Nieprawidłowy identyfikator")


# UWAGA: Usunięto niepotrzebny stary endpoint get_all_mcus.
# Zostawiamy jeden, sprytny, który zwraca wszystko, gdy nie podasz ID, a filtruje, gdy je podasz.

@app.get("/api/v1/mcus", response_model=List[McuStatus])
def get_mcus(location_id: Optional[str] = None):
    """Zwraca historię pomiarów opcjonalnie przefiltrowaną po lokalizacji."""
    if location_id is None:
        print(f"DEBUG: Telefon pobiera całą historię. Elementów: {len(db_mcus)}")
        return db_mcus

    print(f"DEBUG: Telefon pobiera historię dla lokalizacji: {location_id}")
    # Używamy list comprehension do przefiltrowania "bazy danych"
    filtered_mcus = [mcu for mcu in db_mcus if mcu.location_id == location_id]
    return filtered_mcus


@app.post("/api/v1/mcus")
def update_mcu_status(mcu: McuStatus):
    """Urządzenie IoT wysyła nowy punkt pomiarowy do Time-Series DB."""
    print(f"DEBUG: Odebrano pomiar od {mcu.id} (Lokalizacja: {mcu.location_id}) z czasu: {mcu.timestamp}")
    db_mcus.append(mcu)
    return {"status": "success", "message": f"Zapisano punkt historyczny dla {mcu.id}"}


import time


@app.on_event("startup")
def seed_historical_data():
    """Automatycznie wstrzykuje 5 godzin historii przy starcie serwera, żeby PROD nie był pusty."""
    if not db_mcus:
        # Aktualny czas w milisekundach
        now_ms = int(time.time() * 1000)

        # Generujemy 5 paczek cofając się o godzinę (3600000 ms) w przeszłość
        for i in range(5, 0, -1):
            historical_time = now_ms - (i * 3600000)

            # Temperatura rośnie z czasem, żebyśmy widzieli różnicę na matrycy
            base_temp = 15.0 + (5 - i)

            db_mcus.append(McuStatus(
                id="MCU_PROD_123",
                location_id="LOC_001",  # Poznań
                ext_temp=20.0 + (5 - i),
                ext_hum=50,
                timestamp=historical_time,
                silos=[
                    SiloStatus(
                        id="S_01",
                        average_temp=base_temp,
                        matrix_data=[
                            [base_temp, base_temp + 1],
                            [base_temp - 1, base_temp]
                        ]
                    )
                ]
            ))
        print("DEBUG: Zasilano RAM 5-godzinną historią startową dla PROD!")


# --- START SERWERA ---
# Aby uruchomić, wpisz w terminalu:
# uvicorn main:app --reload --host 0.0.0.0 --port 8000