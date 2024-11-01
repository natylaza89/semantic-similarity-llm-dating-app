from app.custom_types import LlmTasks

PROMPT_TEMPLATES = {
    LlmTasks.TEXT_EXTRACTION: [
        ("system", "Extract top 5 keywords that describe personality, hobbies, interests, or qualities. "
        "Provide a JSON response with keywords. {format_instructions}"),
        ("user", "{input}")
        ]
}