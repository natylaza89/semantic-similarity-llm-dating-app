import logging
from typing import Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from app.config import settings
from app.custom_types import LlmTasks
from app.models.llm import LlmConfig, LlmResponse, KeywordsOutput
from app.services.prompts import PROMPT_TEMPLATES

_logger = logging.getLogger(__name__)


class LlmClient:
    def __init__(self, config: Optional[LlmConfig] = None) -> None:
        self._config = config or LlmConfig()
        self._model = self.__init_model()
        self._output_parser = PydanticOutputParser(pydantic_object=KeywordsOutput)

    def __init_model(self) -> BaseChatModel:
        if not self._config:
            raise ValueError("LLM configuration is required")

        if self._config.provider == "gemini":
            return ChatGoogleGenerativeAI(
                api_key=settings.gemini_api_key,
                model=self._config.model,
                temperature=self._config.temperature,
                max_tokens=self._config.max_tokens,
                top_p=self._config.top_p,
                top_k=self._config.top_k,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
                }
            )

        raise ValueError(f"Unsupported provider: {self._config.provider}")

    def __generate_prompt_template(self, task: str = LlmTasks.TEXT_EXTRACTION) -> ChatPromptTemplate:
        template = PROMPT_TEMPLATES.get(task)
        if not template:
            raise ValueError(f"No template found for task: {task}")
        # TODO: make the output parser more generic...
        return ChatPromptTemplate.from_messages(template).partial(format_instructions=self._output_parser.get_format_instructions())

    async def get_response(
        self,
        user_input: str,
        task: str = LlmTasks.TEXT_EXTRACTION
    ) -> LlmResponse:           
            chain = (
                self.__generate_prompt_template(task) | 
                self._model | 
                self._output_parser
            )

            response = []
            try:
                result = await chain.ainvoke({"input": user_input})
                response = result.keywords
            except Exception as e:
                _logger.error(f"Couldn't extract keywords using the LLM service: {str(e)}", exc_info=True)

            return LlmResponse(
                text=response,
            )


llm_client = LlmClient(LlmConfig(
    provider="gemini",
    model="gemini-1.5-flash",
    temperature=0.7,
    max_tokens=512,
    top_p=0.9,
    top_k=64
))
