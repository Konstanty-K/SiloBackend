from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

app = FastAPI(title="SiloMonitor REST API", version="0.1.0")

# --- KONFIGURACJA CORS ---
# Kluczowe dla Androida! Bez tego telefon odrzuci połączenie z laptopem.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Na potrzeby testów pozwalamy na wszystko
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


class SiloStatus(BaseModel):
    id: str
    name: str
    average_temp: float
    matrix_data: List[List[Optional[float]]]


class McuStatus(BaseModel):
    id: str
    name: str
    ext_temp: float
    ext_hum: int
    silos: List[SiloStatus]


# --- FAŁSZYWA BAZA DANYCH (MOCKUP NA START) ---
FAKE_TOKEN = "kk_rnd_secure_token_placeholder_for_phase_2"

# Nasza "baza danych" w pamięci RAM serwera
db_mcus: List[McuStatus] = []


# --- ENDPOINTY (Trasy API) ---

@app.get("/")
def read_root():
    return {"status": "SiloMonitor API v0.1.0 is ONLINE", "time": datetime.now()}


@app.post("/api/v1/auth/login", response_model=TokenResponse)
def login(request: LoginRequest):
    print(f"DEBUG: Próba logowania: {request.username}")
    if request.username == "Admin" and request.password == "1234":
        return TokenResponse(access_token=FAKE_TOKEN, operator_id="OP_001", expires_at=datetime.now())
    else:
        raise HTTPException(status_code=401, detail="Nieprawidłowy identyfikator")


# NOWOŚĆ: Endpoint dla aplikacji Android (Pobieranie stanu)
@app.get("/api/v1/mcus", response_model=List[McuStatus])
def get_all_mcus():
    print(f"DEBUG: Telefon pobiera listę urządzeń. Ilość w bazie: {len(db_mcus)}")
    return db_mcus


# NOWOŚĆ: Endpoint dla fizycznych maszyn / Postmana (Wysyłanie pomiarów)
@app.post("/api/v1/mcus")
def update_mcu_status(mcu: McuStatus):
    print(f"DEBUG: Odebrano nowe dane od urządzenia: {mcu.id}")
    # Szukamy czy MCU już istnieje w bazie
    for i, existing_mcu in enumerate(db_mcus):
        if existing_mcu.id == mcu.id:
            db_mcus[i] = mcu  # Aktualizacja
            return {"status": "success", "message": "Zaktualizowano MCU"}

    # Jeśli nie ma, dodajemy nowe
    db_mcus.append(mcu)
    return {"status": "success", "message": "Dodano nowe MCU"}

# --- START SERWERA ---
# Aby uruchomić, wpisz w terminalu:
# uvicorn main:app --reload --host 0.0.0.0 --port 8000
# UWAGA: '--host 0.0.0.0' jest konieczne, aby telefon widział serwer w Wi-Fi!