# Serveur MCP Météo & Heure Système

[English 🇬🇧](./README.md)

Un serveur Python Model Context Protocol (MCP) simple qui expose 3 outils pour un assistant IA :

| Outil | Description |
|---|---|
| `get_current_weather` | Météo actuelle d'une ville (température, vent, humidité, visibilité) |
| `get_forecast` | Prévisions jusqu'à 5 jours par créneaux de 3h |
| `get_system_time` | Date/heure locale et informations de fuseau de ton PC |

## Prérequis

- Python 3.11+
- Une clé API gratuite [OpenWeatherMap](https://openweathermap.org/api)

## Installation

```bash
# 1) Aller dans le dossier projet
cd meteo

# 2) Créer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS

# 3) Installer les dépendances
pip install -r requirements.txt

# 4) Configurer la variable d'environnement
copy .env.example .env
# Puis éditer .env et remplacer your_api_key_here
```

## Lancer le serveur MCP

```bash
python server.py
```

Le serveur fonctionne en stdio (par défaut), mode attendu par la plupart des clients MCP.

## Connexion depuis un client MCP

Ajoute ceci dans la config MCP (Claude Desktop / Cursor / OpenCode, etc.) :

```json
{
  "mcpServers": {
    "meteo-heure": {
      "command": "python",
      "args": ["C:\\Users\\MZayim\\Desktop\\Projet\\ia GENERAL\\meteo\\server.py"],
      "env": {
        "OPENWEATHERMAP_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

> Adapte le chemin absolu vers `server.py` selon ta machine.

## Exemples de prompts

- « Quel temps fait-il à Paris ? » → `get_current_weather(city="Paris")`
- « Donne-moi les prévisions pour Lyon sur 3 jours » → `get_forecast(city="Lyon", days=3)`
- « Quelle heure est-il sur ce PC ? » → `get_system_time()`

## Notes de sécurité

- Ne **jamais** versionner le fichier `.env`.
- Utiliser uniquement `.env.example` comme modèle.
- Révoquer/rotater tout token ou secret qui a été copié dans un chat, un log ou une capture.

## Structure du projet

```text
meteo/
├── server.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── README.fr.md
```
