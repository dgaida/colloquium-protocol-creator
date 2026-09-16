"""Tests for DiscordEventGenerator."""

from unittest.mock import MagicMock, patch

from academic_doc_generator.colloquium.discord_event_generator import DiscordEventGenerator


def test_discord_event_creation_ignored_when_not_campus():
    generator = DiscordEventGenerator()
    result = generator.create_event_if_campus_room_1242(
        student_name="Max Mustermann",
        date_colloquium="20.01.2026",
        time_colloquium="14:00",
        location_type="company",
        room="1.242",
    )
    assert result is None


def test_discord_event_creation_ignored_when_room_not_1242():
    generator = DiscordEventGenerator()
    result = generator.create_event_if_campus_room_1242(
        student_name="Max Mustermann",
        date_colloquium="20.01.2026",
        time_colloquium="14:00",
        location_type="campus",
        room="3.217",
    )
    assert result is None


def test_discord_event_creation_missing_env_variables(monkeypatch):
    monkeypatch.delenv("DISCORD_BOT_TOKEN", raising=False)
    monkeypatch.delenv("DISCORD_GUILD_ID", raising=False)

    generator = DiscordEventGenerator()
    result = generator.create_event_if_campus_room_1242(
        student_name="Max Mustermann",
        date_colloquium="20.01.2026",
        time_colloquium="14:00",
        location_type="campus",
        room="1.242",
    )
    assert result is None


@patch("requests.post")
def test_discord_event_creation_success(mock_post, monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "fake-token")
    monkeypatch.setenv("DISCORD_GUILD_ID", "123456789")

    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": "99999", "name": "Kolloquium Max Mustermann"}
    mock_post.return_value = mock_response

    generator = DiscordEventGenerator()
    result = generator.create_event_if_campus_room_1242(
        student_name="Max Mustermann",
        date_colloquium="20.01.2026",
        time_colloquium="14:00",
        location_type="campus",
        room="1.242",
    )

    assert result == {"id": "99999", "name": "Kolloquium Max Mustermann"}
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "https://discord.com/api/v10/guilds/123456789/scheduled-events"
    assert kwargs["headers"]["Authorization"] == "Bot fake-token"
    assert kwargs["json"]["name"] == "Kolloquium Max Mustermann"
    assert kwargs["json"]["entity_metadata"]["location"] == "Raum 1.242, Campus Gummersbach"


@patch("requests.post")
def test_discord_event_creation_api_error(mock_post, monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "fake-token")
    monkeypatch.setenv("DISCORD_GUILD_ID", "123456789")

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_post.return_value = mock_response

    generator = DiscordEventGenerator()
    result = generator.create_event_if_campus_room_1242(
        student_name="Max Mustermann",
        date_colloquium="20.01.2026",
        time_colloquium="14:00",
        location_type="campus",
        room="1.242",
    )

    assert result is None
