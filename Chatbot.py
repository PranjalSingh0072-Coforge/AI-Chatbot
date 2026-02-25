from langchain_core.language_models import LLM
from langchain_core.prompts import PromptTemplate
import requests
from typing import List, Optional
from dotenv import load_dotenv
import os

load_dotenv(override=True)
config = os.environ

class CustomLLM(LLM):
    model: str
    endpoint_url: str = config['API_URL']
    headers: dict = {
        "Content-Type": "application/json",
        "X-API-KEY": config['API_KEY']
    }
    temperature: float = 0.7
    top_p: float = 1.0
    max_tokens: int = 2000
    enable_stream: bool = False
    stop: Optional[List[str]] = None

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens
        }
        if stop:
            payload["stop"] = stop
        response = requests.post(self.endpoint_url, headers=self.headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']

    @property
    def _llm_type(self) -> str:
        return "custom-llm"

llm = CustomLLM(
    model=config['MODEL_NAME'],
    temperature=0.5,
    top_p=0.9,
    max_tokens=1000
)

prompt = PromptTemplate.from_template("You are helpful AI. Reply to: {text}")

if __name__ == "__main__":
    print("🤖 Simple Chatbot (type 'exit' to quit)\n")
    while True:
        user_question = input("You: ").strip()
        
        if user_question.lower() in ['exit', 'quit', 'q']:
            print("Chatbot: Goodbye!")
            break
        
        if not user_question:
            print("Chatbot: Please enter a question.\n")
            continue
        
        user_input = prompt.format(text=user_question)
        response = llm.invoke(user_input)
        print(f"Chatbot: {response}\n")