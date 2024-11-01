from pydantic import BaseModel, Field


class LlmConfig(BaseModel):
    provider: str = "gemini"
    model: str = "gemini-1.5-flash"
    temperature: float = 0.7
    max_tokens: int = 100
    top_p: float = 0.9
    top_k: int = 64


class LlmResponse(BaseModel):
    text: list[str] | list


class KeywordsOutput(BaseModel):
    keywords: list[str] = Field(description="Top 5 keywords describing personality, hobbies, interests, or qualities")
