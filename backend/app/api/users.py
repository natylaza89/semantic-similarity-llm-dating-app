from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.services.state_manager import state_manager
from app.models.user import User
from app.models.match import MatchResponse, MatchRequest
from app.utils import find_potential_match, create_chat_for_matched_users


router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: User):
    if user.id in state_manager.get_users():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    await state_manager.set_user(user.id, user)
    return JSONResponse(content={"message": "User registered successfully"}, status_code=status.HTTP_201_CREATED)


@router.post("/match", response_model=MatchResponse, status_code=status.HTTP_200_OK)
async def match(request: MatchRequest):
    users = state_manager.get_users()
    if request.user_id not in users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    retries = 3
    potential_match = None
    while retries > 0 and not potential_match:
        potential_match = await find_potential_match(request.user_id, request.preferences, users)
        retries -= 1

    if not potential_match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't find a match")

    chat_id = create_chat_for_matched_users(user_id=request.user_id, match_id=potential_match["match_id"])
    return MatchResponse(
        match=potential_match,
        chat_id=chat_id,
        message="Potential match found" if potential_match else "No potential matches found"
    )
