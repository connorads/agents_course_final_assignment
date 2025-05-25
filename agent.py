import logfire

from pydantic_ai import Agent
from tools import safe_duckduckgo_search_tool, get_youtube_transcript
logfire.configure()  
logfire.instrument_pydantic_ai()

class BasicAgent:
    def __init__(self):
        self.agent = Agent(
            "openai:o3-mini",
            tools=[safe_duckduckgo_search_tool(), get_youtube_transcript],
            system_prompt="Search DuckDuckGo for the given query and return the results.",
        )

    def __call__(self, question: str) -> str:
        print(f"Agent received question (first 50 chars): {question[:50]}...")
        result = self.agent.run_sync(question).output
        print(f"Agent returning fixed answer: {result}")
        return result
