import sys
from agent import GaiaAgent

agent = GaiaAgent()

# Get the question from command-line arguments
if len(sys.argv) > 1:
    question = sys.argv[1]
else:
    question = "In the video https://www.youtube.com/watch?v=L1vXCYZAYYM, what is the highest number of bird species to be on camera simultaneously?"


result = agent(question)

print(result)