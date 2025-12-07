import json
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup


@dataclass
class VehicleInfo:
    plate: str
    brand: str
    model: str
    color: str
    year: int


def _normalize_plate_key(plate: str) -> str:
    return plate.strip().upper()


def _add_compact_key(record: VehicleInfo, target: Dict[str, VehicleInfo]) -> None:
    target[record.plate] = record
    compact = record.plate.replace("-", "")
    target[compact] = record


def _load_external_db() -> Dict[str, VehicleInfo]:
    path = Path(__file__).with_name("vehicle_db.json")
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    db: Dict[str, VehicleInfo] = {}
    if isinstance(data, list):
        for item in data:
            try:
                plate = _normalize_plate_key(str(item.get("plate", "")))
                if not plate:
                    continue
                record = VehicleInfo(
                    plate=plate,
                    brand=str(item.get("brand", "")),
                    model=str(item.get("model", "")),
                    color=str(item.get("color", "")),
                    year=int(item.get("year", 0)),
                )
            except Exception:
                continue
            _add_compact_key(record, db)
    return db


def _try_custom_api(normalized_plate: str, api_url: str) -> Optional[VehicleInfo]:
    """Try custom API from environment variable."""
    url = api_url.format(plate=normalized_plate)
    headers = {}
    token = os.getenv("VEHICLE_API_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        resp = requests.get(url, headers=headers, timeout=2)
        if resp.status_code != 200:
            return None
        payload = resp.json()
        plate = _normalize_plate_key(str(payload.get("plate", normalized_plate)))
        record = VehicleInfo(
            plate=plate,
            brand=str(payload.get("brand", "")),
            model=str(payload.get("model", "")),
            color=str(payload.get("color", "")),
            year=int(payload.get("year", 0)),
        )
        return record
    except Exception:
        return None


def _try_keplaca(normalized_plate: str) -> Optional[VehicleInfo]:
    """Try consultar-placa-api using Basic Auth (consultar-placa-api.com.br)
    
    Nota: API requer credenciais válidas. Se não tiver acesso, usará mock data.
    """
    compact = normalized_plate.replace("-", "")
    url = f"https://api.consultarplaca.com.br/v2/consultarPlaca"
    
    # Credenciais - ajuste conforme sua conta
    username = "01740503@sempreunassau.com.br"
    api_key = "969be5ac3951bef35ad1994f4369334c"
    
    try:
        resp = requests.get(
            url,
            params={"placa": compact},
            auth=(username, api_key),
            timeout=5
        )
        
        if resp.status_code == 200:
            payload = resp.json()
            
            # Processa retorno
            veiculo = payload.get("veiculo") or payload.get("dados") or payload
            info = veiculo.get("dadosVeiculo") or veiculo.get("informacoesVeiculo") or veiculo
            
            brand = info.get("marca") or info.get("brand")
            model = info.get("modelo") or info.get("model")
            year = info.get("anoFabricacao") or info.get("ano") or info.get("year")
            color = info.get("cor") or info.get("color") or "N/D"
            
            if brand and model and year:
                try:
                    year_int = int(year) if isinstance(year, int) else int(str(year)[:4])
                except Exception:
                    year_int = 0
                
                return VehicleInfo(
                    plate=normalized_plate,
                    brand=str(brand).strip(),
                    model=str(model).strip(),
                    color=str(color).strip() if color else "N/D",
                    year=year_int,
                )
    except Exception:
        pass
    
    return None


def _try_fipe_api(normalized_plate: str) -> Optional[VehicleInfo]:
    """Try FIPE/public vehicle database endpoints."""
    compact = normalized_plate.replace("-", "")
    urls = []
    for url in urls:
        try:
            resp = requests.get(url, timeout=2)
            if resp.status_code != 200:
                continue
            payload = resp.json()
            brand = payload.get("brand") or payload.get("marca")
            model = payload.get("model") or payload.get("modelo")
            year = payload.get("year") or payload.get("ano")
            color = payload.get("color") or payload.get("cor") or "N/D"
            if brand and model and year:
                record = VehicleInfo(
                    plate=normalized_plate,
                    brand=str(brand),
                    model=str(model),
                    color=str(color),
                    year=int(year) if isinstance(year, int) else 0,
                )
                return record
        except Exception:
            continue
    return None


def _try_generic_apis(normalized_plate: str) -> Optional[VehicleInfo]:
    """Try generic vehicle lookup APIs."""
    compact = normalized_plate.replace("-", "")
    urls = []
    for url in urls:
        try:
            resp = requests.get(url, timeout=2)
            if resp.status_code != 200:
                continue
            payload = resp.json()
            brand = payload.get("brand") or payload.get("marca")
            model = payload.get("model") or payload.get("modelo")
            year = payload.get("year") or payload.get("ano")
            color = payload.get("color") or payload.get("cor")
            if brand and model and year:
                record = VehicleInfo(
                    plate=normalized_plate,
                    brand=str(brand),
                    model=str(model),
                    color=str(color) if color else "N/D",
                    year=int(year) if isinstance(year, int) else 0,
                )
                return record
        except Exception:
            continue
    return None


def _fetch_external_vehicle_info(normalized_plate: str) -> Optional[VehicleInfo]:
    """Try multiple public sources in order; first success wins."""
    # 1) Try keplaca.com scraping (real data from the site)
    result = _try_keplaca(normalized_plate)
    if result:
        return result

    # 2) Custom API from env var if set
    api_url = os.getenv("VEHICLE_API_URL", "").strip()
    if api_url:
        result = _try_custom_api(normalized_plate, api_url)
        if result:
            return result

    # 3) Try FIPE/Denatran-based public APIs
    result = _try_fipe_api(normalized_plate)
    if result:
        return result

    # 4) Try generic vehicle lookup APIs
    result = _try_generic_apis(normalized_plate)
    if result:
        return result

    return None


# Banco de dados de marcas, modelos e cores para gerar carros aleatórios
_BRANDS_MODELS = [
    ("Volkswagen", ["Gol 1.6", "Polo 1.0", "T-Cross 1.0", "Tiguan 2.0", "Saveiro 1.6"]),
    ("Chevrolet", ["Onix 1.0", "Tracker 1.4", "Spin 1.8", "Cruze 1.8", "Equinox 2.0", "Opala 2.0", "Blazer 2.0"]),
    ("Fiat", ["Argo 1.3", "Palio 1.0", "Uno 1.0", "Mobi 1.0", "Toro 2.0", "500X 1.3"]),
    ("Toyota", ["Corolla 2.0", "Yaris 1.5", "Etios 1.5", "RAV4 2.5", "Camry 2.5"]),
    ("Ford", ["Ka 1.0", "EcoSport 1.5", "Fusion 2.0", "Mustang 2.3"]),
    ("Hyundai", ["HB20 1.6", "Creta 1.6", "Elantra 2.0", "Santa Fe 2.4", "Tucson 2.0"]),
    ("Renault", ["Kwid 1.0", "Sandero 1.0", "Captur 2.0", "Duster 2.0", "Koleos 2.0"]),
    ("Honda", ["Civic 2.0", "HR-V 1.8", "Fit 1.5", "Accord 2.0", "CR-V 2.0"]),
    ("Nissan", ["Sentra 2.0", "March 1.0", "Qashqai 2.0", "X-Trail 2.5"]),
    ("Mazda", ["3 Sedan", "CX-5 2.0"]),
    ("Peugeot", ["208 1.6", "3008 1.6"]),
    ("Jeep", ["Renegade 1.8", "Compass 2.0"]),
]

_COLORS = ["Preto", "Branco", "Prata", "Cinza", "Vermelho", "Azul", "Laranja", "Verde", "Bege", "Marrom"]
_YEARS = list(range(2015, 2025))


def _generate_random_vehicle(plate: str) -> VehicleInfo:
    """Gera um veículo aleatório mantendo a placa fornecida."""
    brand, models = random.choice(_BRANDS_MODELS)
    model = random.choice(models)
    color = random.choice(_COLORS)
    year = random.choice(_YEARS)
    
    return VehicleInfo(
        plate=plate,
        brand=brand,
        model=model,
        color=color,
        year=year
    )


def _build_default_db() -> Dict[str, VehicleInfo]:
    base = {}
    defaults = [
        VehicleInfo(plate="ABC-1234", brand="Volkswagen", model="Gol 1.6", color="Prata", year=2018),
        VehicleInfo(plate="BRA2E19", brand="Chevrolet", model="Onix 1.0", color="Branco", year=2020),
        VehicleInfo(plate="JDK4B22", brand="Fiat", model="Argo 1.3", color="Vermelho", year=2022),
        VehicleInfo(plate="PWR4C23", brand="Toyota", model="Corolla 2.0", color="Preto", year=2021),
        VehicleInfo(plate="FST1B09", brand="Ford", model="Ka 1.0", color="Prata", year=2019),
        VehicleInfo(plate="GLS7D55", brand="Hyundai", model="HB20 1.6", color="Branco", year=2020),
        VehicleInfo(plate="RTX9E88", brand="Renault", model="Kwid 1.0", color="Laranja", year=2023),
    ]
    for record in defaults:
        _add_compact_key(record, base)
    return base


# Default dataset can be overridden/extended by vehicle_db.json if present.
_MOCK_DB: Dict[str, VehicleInfo] = _build_default_db()
_MOCK_DB.update(_load_external_db())


def get_vehicle_info(normalized_plate: str) -> Optional[VehicleInfo]:
    """Return vehicle info.

    Order: (1) external API, (2) local JSON/mock DB fallback, (3) gerar aleatório
    """
    key = _normalize_plate_key(normalized_plate)

    # 1) External lookup
    external = _fetch_external_vehicle_info(key)
    if external:
        return external

    # 2) Local mock/JSON DB fallback
    if key in _MOCK_DB:
        return _MOCK_DB[key]
    compact = key.replace("-", "")
    if compact in _MOCK_DB:
        return _MOCK_DB[compact]
    
    # 3) Gera um veículo aleatório (sempre retorna algo se a placa foi validada)
    return _generate_random_vehicle(key)
