import sys
from agent import BasicAgent

agent = BasicAgent()

# Get the question from command-line arguments
if len(sys.argv) > 1:
    question = sys.argv[1]
else:
    question = "What is the capital of France?"


result = agent(question)

print(result)