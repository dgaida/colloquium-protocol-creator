"""Modul zur Erstellung von Discord-Events für Kolloquien in Raum 1.242."""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import dotenv
import requests


class DiscordEventGenerator:
    """Erstellt Scheduled Events in Discord für Kolloquien."""

    def __init__(self):
        """Initialisiert den DiscordEventGenerator und lädt Umgebungsvariablen."""
        if Path("secrets.env").exists():
            dotenv.load_dotenv("secrets.env")
        dotenv.load_dotenv()

    def create_event_if_campus_room_1242(
        self,
        student_name: str,
        date_colloquium: str,
        time_colloquium: str,
        duration_minutes: int = 45,
        location_type: str = "campus",
        room: Optional[str] = None,
    ) -> Optional[dict]:
        """Erstellt ein Discord-Event, falls das Kolloquium in Raum 1.242 am Campus stattfindet.

        Args:
            student_name: Name des Studierenden.
            date_colloquium: Datum im Format "DD.MM.YYYY".
            time_colloquium: Uhrzeit im Format "HH:MM".
            duration_minutes: Dauer des Kolloquiums in Minuten (Standard: 45).
            location_type: "campus", "company" oder "online".
            room: Raumnummer.

        Returns:
            Dict der Discord API-Antwort, wenn das Event erstellt wurde, sonst None.
        """
        if location_type != "campus" or not room or room.strip() != "1.242":
            return None

        bot_token = os.getenv("DISCORD_BOT_TOKEN")
        guild_id = os.getenv("DISCORD_GUILD_ID")

        if not bot_token or not guild_id:
            print("⚠️  Discord-Event für Raum 1.242 konnte nicht erstellt werden:")
            print("   DISCORD_BOT_TOKEN oder DISCORD_GUILD_ID fehlt in der Umgebung/secrets.env")
            return None

        try:
            dt_start = datetime.strptime(
                f"{date_colloquium} {time_colloquium}", "%d.%m.%Y %H:%M"
            ).astimezone()
            dt_end = dt_start + timedelta(minutes=duration_minutes)

            url = f"https://discord.com/api/v10/guilds/{guild_id}/scheduled-events"
            headers = {
                "Authorization": f"Bot {bot_token}",
                "Content-Type": "application/json",
            }
            payload = {
                "name": f"Kolloquium {student_name}",
                "privacy_level": 2,  # GUILD_ONLY
                "scheduled_start_time": dt_start.isoformat(),
                "scheduled_end_time": dt_end.isoformat(),
                "description": f"Kolloquium von {student_name} in Raum 1.242",
                "entity_type": 3,  # EXTERNAL
                "entity_metadata": {
                    "location": "Raum 1.242, Campus Gummersbach",
                },
            }

            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code in (200, 201):
                data = response.json()
                print(f"✅ Discord-Event erstellt: Kolloquium {student_name} in Raum 1.242")
                return data
            else:
                print(
                    f"⚠️  Fehler beim Erstellen des Discord-Events ({response.status_code}): {response.text}"
                )
                return None
        except Exception as e:
            print(f"⚠️  Fehler beim Erstellen des Discord-Events: {e}")
            return None
