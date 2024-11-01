from typing import List

from google.generativeai.types import HarmCategory, HarmBlockThreshold

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from app.config import settings


class KeywordsOutput(BaseModel):
    keywords: List[str] = Field(description="Top 5 keywords describing personality, hobbies, interests, or qualities")


def main():
    # input_text = "I love hiking, have a passion for cooking, and am looking for someone who is also a dog lover"
    input_text = "I want someone who enjoys hiking, loves animals, and is into music festivals"
    safety_settings={
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
    }
    output_parser = PydanticOutputParser(pydantic_object=KeywordsOutput)

    # Prepare the prompt template
    prompt = ChatPromptTemplate.from_messages([
      ("system", "Extract top 5 keywords that describe personality, hobbies, interests, or qualities. "
                   "Provide a JSON response with keywords. {format_instructions}"),
        ("user", "{input}")
    ]).partial(format_instructions=output_parser.get_format_instructions())
    
    # Configure the model with safety settings
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=settings.gemini_api_key,
        temperature=0.7,
        max_output_tokens=100,
        top_p=0.9,
        top_k=40,
        safety_settings=safety_settings,
    )
    
    # Create the processing chain
    chain = (
        prompt | 
        model | 
        output_parser
    )
    
    try:
        result = chain.invoke({"input": input_text})
        return result.keywords
    
    except Exception as e:
        # Error handling
        print(f"Error extracting keywords: {e}")
        return []

if __name__ == "__main__":
    res = main()
    print(res)
