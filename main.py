
from agno.agent import Agent
from agno.models.groq import Groq
from dotenv import load_dotenv

load_dotenv()


def main():
    print("Hello from brifai!")

    

    agente_brifAi = Agent(
     name="BrifAi",
     model=Groq(id="llama-3.1-8b-instant")
    )

   # resposta =  agente_brifAi.run("Tell me a curiosity!")
    # print(resposta.content)


    agente_brifAi.print_response("Tell me a curiosity!")
if __name__ == "__main__":
    main()
