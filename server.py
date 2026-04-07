"""
Serveur MCP Météo & Heure Système
==================================
Un serveur Model Context Protocol simple qui expose 3 outils :
  - get_current_weather : météo actuelle d'une ville
  - get_forecast        : prévisions 5 jours / 3h d'une ville
  - get_system_time     : date et heure système du PC
"""

import os
import datetime
import platform

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# ── Configuration ────────────────────────────────────────────────────────────

load_dotenv()

API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5"
DEFAULT_UNITS = "metric"  # metric = °C, imperial = °F, standard = K
DEFAULT_LANG = "fr"

mcp = FastMCP(
    name="Météo & Heure Système",
    json_response=True,
)

# ── Helpers ──────────────────────────────────────────────────────────────────


def _check_api_key() -> None:
    """Vérifie que la clé API est configurée."""
    if not API_KEY:
        raise ValueError(
            "La clé OPENWEATHERMAP_API_KEY n'est pas définie. "
            "Crée un fichier .env avec ta clé (voir .env.example)."
        )


def _wind_direction(degrees: float) -> str:
    """Convertit des degrés en direction cardinale."""
    directions = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO",
    ]
    idx = round(degrees / 22.5) % 16
    return directions[idx]


def _format_current(data: dict) -> dict:
    """Met en forme la réponse météo actuelle."""
    main = data["main"]
    weather = data["weather"][0]
    wind = data.get("wind", {})
    sys_info = data.get("sys", {})

    return {
        "ville": data.get("name", "Inconnue"),
        "pays": sys_info.get("country", "??"),
        "condition": weather.get("description", "").capitalize(),
        "icone": f"https://openweathermap.org/img/wn/{weather.get('icon', '01d')}@2x.png",
        "temperature": {
            "actuelle": f"{main['temp']:.1f}°C",
            "ressentie": f"{main['feels_like']:.1f}°C",
            "min": f"{main['temp_min']:.1f}°C",
            "max": f"{main['temp_max']:.1f}°C",
        },
        "humidite": f"{main['humidity']}%",
        "pression": f"{main['pressure']} hPa",
        "vent": {
            "vitesse": f"{wind.get('speed', 0):.1f} m/s",
            "direction": _wind_direction(wind.get("deg", 0)),
            "rafales": f"{wind.get('gust', 0):.1f} m/s" if "gust" in wind else None,
        },
        "visibilite": f"{data.get('visibility', 0) / 1000:.1f} km",
        "horodatage_utc": datetime.datetime.fromtimestamp(
            data["dt"], tz=datetime.timezone.utc
        ).isoformat(),
    }


def _format_forecast_entry(entry: dict) -> dict:
    """Met en forme un créneau de prévision."""
    main = entry["main"]
    weather = entry["weather"][0]
    wind = entry.get("wind", {})

    return {
        "date_heure": entry.get("dt_txt", ""),
        "condition": weather.get("description", "").capitalize(),
        "icone": f"https://openweathermap.org/img/wn/{weather.get('icon', '01d')}@2x.png",
        "temperature": f"{main['temp']:.1f}°C",
        "ressentie": f"{main['feels_like']:.1f}°C",
        "humidite": f"{main['humidity']}%",
        "vent": f"{wind.get('speed', 0):.1f} m/s {_wind_direction(wind.get('deg', 0))}",
        "precipitation_3h_mm": entry.get("rain", {}).get("3h", 0)
        + entry.get("snow", {}).get("3h", 0),
    }


# ── Outils MCP ───────────────────────────────────────────────────────────────


@mcp.tool()
async def get_current_weather(city: str) -> dict:
    """
    Récupère la météo actuelle d'une ville.

    Args:
        city: Nom de la ville (ex: "Paris", "London,GB", "New York,US")

    Returns:
        Données météo actuelles : température, conditions, vent, humidité, etc.
    """
    _check_api_key()

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{BASE_URL}/weather",
            params={
                "q": city,
                "appid": API_KEY,
                "units": DEFAULT_UNITS,
                "lang": DEFAULT_LANG,
            },
        )

    if resp.status_code == 404:
        return {"erreur": f"Ville '{city}' introuvable. Vérifie l'orthographe."}
    if resp.status_code == 401:
        return {"erreur": "Clé API invalide. Vérifie OPENWEATHERMAP_API_KEY."}

    resp.raise_for_status()
    return _format_current(resp.json())


@mcp.tool()
async def get_forecast(city: str, days: int = 5) -> dict:
    """
    Récupère les prévisions météo (jusqu'à 5 jours, par créneaux de 3h).

    Args:
        city: Nom de la ville (ex: "Paris", "London,GB", "New York,US")
        days: Nombre de jours de prévisions (1 à 5, défaut: 5)

    Returns:
        Prévisions météo détaillées par créneaux de 3 heures.
    """
    _check_api_key()

    days = max(1, min(days, 5))
    cnt = days * 8  # 8 créneaux de 3h par jour

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{BASE_URL}/forecast",
            params={
                "q": city,
                "appid": API_KEY,
                "units": DEFAULT_UNITS,
                "lang": DEFAULT_LANG,
                "cnt": cnt,
            },
        )

    if resp.status_code == 404:
        return {"erreur": f"Ville '{city}' introuvable. Vérifie l'orthographe."}
    if resp.status_code == 401:
        return {"erreur": "Clé API invalide. Vérifie OPENWEATHERMAP_API_KEY."}

    resp.raise_for_status()
    data = resp.json()
    city_info = data.get("city", {})

    # Regrouper par jour
    jours: dict[str, list[dict]] = {}
    for entry in data.get("list", []):
        date_str = entry.get("dt_txt", "")[:10]
        jours.setdefault(date_str, []).append(_format_forecast_entry(entry))

    return {
        "ville": city_info.get("name", city),
        "pays": city_info.get("country", "??"),
        "nombre_jours": len(jours),
        "previsions": jours,
    }


@mcp.tool()
def get_system_time() -> dict:
    """
    Renvoie la date et l'heure actuelles du système (PC local).

    Returns:
        Date, heure, fuseau horaire et infos système.
    """
    now = datetime.datetime.now()
    utc_now = datetime.datetime.now(datetime.timezone.utc)

    # Essayer de détecter le fuseau horaire local
    try:
        local_tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
        tz_name = str(local_tz)
    except Exception:
        tz_name = "Inconnu"

    # Offset UTC
    utc_offset = now.astimezone().strftime("%z")
    utc_offset_formatted = f"UTC{utc_offset[:3]}:{utc_offset[3:]}" if utc_offset else "UTC"

    return {
        "date": now.strftime("%A %d %B %Y"),
        "heure": now.strftime("%H:%M:%S"),
        "iso8601": now.astimezone().isoformat(),
        "timestamp_unix": int(now.timestamp()),
        "fuseau_horaire": tz_name,
        "offset_utc": utc_offset_formatted,
        "heure_utc": utc_now.strftime("%H:%M:%S"),
        "systeme": {
            "os": platform.system(),
            "version_os": platform.version(),
            "machine": platform.node(),
        },
    }


# ── Point d'entrée ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
