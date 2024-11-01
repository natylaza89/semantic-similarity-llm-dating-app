from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.state_manager import state_manager
from app.custom_types import ChatID, UserID, ActiveChat

router = APIRouter()


@router.websocket("/ws/{chat_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: ChatID, user_id: UserID):
    await websocket.accept()
    state_manager.set_active_chats(chat_id, websocket)
    active_chat: ActiveChat = state_manager.get_active_chat(chat_id)

    try:
        while True:
            data = await websocket.receive_text()
            for client in active_chat:
                if client != websocket:
                    await client.send_text(f"User {user_id}: {data}")
    except WebSocketDisconnect:
        state_manager.delete_chat_from_active_chats(chat_id, websocket)

        for client in active_chat:
            await client.send_text(f"User {user_id} has left the chat")
