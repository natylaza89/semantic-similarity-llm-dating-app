import asyncio
import http

import click
import httpx
import websockets


BASE_URL = "http://localhost:8989/api/v1"
WS_BASE_URL = "ws://localhost:8989/api/v1"

MatchInfo = dict[str, str]
ChatID = str
UserID = str


async def async_register(user_id: UserID, name: str, description: str) -> None:
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/register", json={
            "id": user_id,
            "name": name,
            "description": description
        })
        if response.status_code == http.HTTPStatus.CREATED:
            click.echo("User registered successfully!")
        else:
            click.echo(f"Error: {response.text}")


async def async_find_matches(user_id: UserID, preferences: str) -> MatchInfo | None:
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/match", json={
            "user_id": user_id,
            "preferences": preferences
        })
        if response.status_code == http.HTTPStatus.OK:
            data = response.json()
            if data["match"]:
                click.echo("Match found:")
                match_info = data['match']
                match_info["chat_id"] = data["chat_id"]
                click.echo(f"{match_info}")
                return match_info
            else:
                click.echo("No match found.")
                return None
        else:
            click.echo(f"Error: {response.text}")
            return None


async def async_create_chat(user_id: UserID, match_id: UserID) -> ChatID | None:
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/create_chat", params={
            "user_id": user_id,
            "match_id": match_id
        })
        if response.status_code == http.HTTPStatus.OK:
            data = response.json()
            return data["chat_id"]
        else:
            click.echo(f"Error getting or creating chat: {response.text}")
            return None


async def receive_messages(websocket) -> None:
    try:
        while True:
            message = await websocket.recv()
            click.echo(f"\nReceived: {message}")
    except websockets.exceptions.ConnectionClosed:
        click.echo("Connection closed")

async def send_messages(websocket):
    try:
        event_loop = asyncio.get_event_loop()
        while True:
            message = await event_loop.run_in_executor(None, input, "Enter message (or 'quit' to exit): ")
            if message.lower() == 'quit':
                await websocket.close()
                break
            await websocket.send(message)
    except websockets.exceptions.ConnectionClosed:
        pass

async def async_chat(chat_id: ChatID, user_id: UserID) -> None:
    uri = f"{WS_BASE_URL}/ws/{chat_id}/{user_id}"

    async with websockets.connect(uri) as websocket:
        click.echo(f"Connected to chat. Type 'quit' to exit.")
        receive_task = asyncio.create_task(receive_messages(websocket))
        send_task = asyncio.create_task(send_messages(websocket))

        await asyncio.gather(receive_task, send_task)
