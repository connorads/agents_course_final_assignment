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
    def _generate_final_answer(self, question: str, answer: str) -> str:
        prompt = f"""
        **Question:** {question}
        
        **Initial answer:** {answer}
        
        **Example 1:** What is the biggest city in California? Los Angeles
        **Example 2:** How many 'r's are in strawberry? 3
        **Example 3:** What is the opposite of black? White
        **Example 4:** What are the first 5 numbers in the Fibonacci sequence? 0, 1, 1, 2, 3
        **Example 5:** What is the opposite of bad, worse, worst? good, better, best
        
        **Final answer:** 
        """
        return self.final_answer_agent.run_sync(prompt).output

    def __init__(self):
        self.agent = Agent(
            "gemini-2.5-flash-preview-05-20",
            tools=[web_search_tool, youtube_analysis_tool],
            system_prompt="You are a helpful assistant that can answer questions about the world.",
        )
        self.final_answer_agent = Agent(
            "gemini-2.5-flash-preview-05-20",
            system_prompt="""
        You are an expert question answering assistant. Given a question and an initial answer, your task is to provide the final answer.
        Your final answer must be a number and/or string OR as few words as possible OR a comma-separated list of numbers and/or strings.
        If you are asked for a number, don't use comma to write your number neither use units such as USD, $, percent, or % unless specified otherwise.
        If you are asked for a string, don't use articles, neither abbreviations (for example cities), and write the digits in plain text unless specified otherwise.
        If you are asked for a comma-separated list, apply the above rules depending of whether the element to be put in the list is a number or a string.
        If the final answer is a number, use a number not a word.
        If the final answer is a string, start with an uppercase character.
        If the final answer is a comma-separated list of numbers, use a space character after each comma.
        If the final answer is a comma-separated list of strings, use a space character after each comma and start with a lowercase character.
        Do not add any content to the final answer that is not in the initial answer.
        """,
        )

    def __call__(self, question: str) -> str:
        print(f"Agent received question (first 50 chars): {question[:50]}...")
        result = self.agent.run_sync(question).output
        print(f"Agent returning initial answer: {result}")
        final_answer = self._generate_final_answer(question, result)
        print(f"Agent returning final answer: {final_answer}")
        return final_answer
