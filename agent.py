import os
import logfire

from pydantic_ai import Agent
from google import genai
from google.genai import types

logfire.configure()  
logfire.instrument_pydantic_ai()

def web_search_tool(question: str) -> str | None:
    """Given a question only, search the web to answer the question.

        Args:
            question (str): Question to answer
            
        Returns:
            str: Answer to the question
            
        Raises:
            RuntimeError: If processing fails"""
    try:
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            contents=question,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )

        return response.text
    except Exception as e:
        raise RuntimeError(f"Processing failed: {str(e)}") from e

def youtube_analysis_tool(question: str, url: str) -> str | None:
    """Given a question and YouTube URL, analyze the video to answer the question.

        Args:
            question (str): Question about a YouTube video
            url (str): The YouTube URL
            
        Returns:
            str: Answer to the question about the YouTube video
            
        Raises:
            RuntimeError: If processing fails"""
    try:
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            contents=types.Content(
                parts=[types.Part(file_data=types.FileData(file_uri=url)),
                        types.Part(text=question)]
            )
        )

        return response.text
    except Exception as e:
        raise RuntimeError(f"Processing failed: {str(e)}") from e

class BasicAgent:
    def __init__(self):
        self.agent = Agent(
            "gemini-2.5-flash-preview-05-20",
            tools=[web_search_tool, youtube_analysis_tool],
            system_prompt="You are a helpful assistant that can answer questions about the world.",
        )

    def __call__(self, question: str) -> str:
        print(f"Agent received question (first 50 chars): {question[:50]}...")
        result = self.agent.run_sync(question).output
        print(f"Agent returning fixed answer: {result}")
        return result
