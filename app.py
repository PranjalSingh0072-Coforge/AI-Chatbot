import streamlit as st
from langchain_core.language_models import LLM
from langchain_core.prompts import PromptTemplate
import requests
from typing import List, Optional
from dotenv import load_dotenv
import os

# Page config for better performance
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load environment variables
load_dotenv(override=True)
config = os.environ


class CustomLLM(LLM):
    model: str
    endpoint_url: str = config.get('API_URL', '')
    headers: dict = {
        "Content-Type": "application/json",
        "X-API-KEY": config.get('API_KEY', '')
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
        response = requests.post(self.endpoint_url, headers=self.headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']

    @property
    def _llm_type(self) -> str:
        return "custom-llm"


# Cache LLM initialization
@st.cache_resource
def initialize_llm():
    """Initialize LLM once and reuse across sessions"""
    return CustomLLM(
        model=config.get('MODEL_NAME', 'default-model'),
        temperature=0.5,
        top_p=0.9,
        max_tokens=1000
    )


# Cache prompt template
@st.cache_data
def get_prompt_template():
    """Cache prompt template for reuse"""
    return PromptTemplate.from_template("You are a helpful AI. Reply to: {text}")


# Initialize session state for chat history
def initialize_session_state():
    """Initialize session state for chat management"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "llm" not in st.session_state:
        st.session_state.llm = initialize_llm()
    if "prompt" not in st.session_state:
        st.session_state.prompt = get_prompt_template()


def display_chat_messages():
    """Display chat history with pagination support"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])


def process_user_input(user_input: str):
    """Process user input and generate response"""
    if not user_input.strip():
        st.warning("Please enter a question.")
        return

    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Display user message
    with st.chat_message("user"):
        st.write(user_input)

    # Generate response with loading indicator
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                formatted_input = st.session_state.prompt.format(text=user_input)
                response = st.session_state.llm.invoke(formatted_input)
                
                # Add assistant response to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                st.write(response)
            except requests.exceptions.Timeout:
                st.error("Request timed out. Please try again.")
            except requests.exceptions.RequestException as e:
                st.error(f"API Error: {str(e)}")
            except Exception as e:
                st.error(f"Error: {str(e)}")


def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()

    # Header
    st.title("🤖 AI Chatbot")
    st.markdown("---")

    # Sidebar for settings
    with st.sidebar:
        st.title("⚙️ Settings")
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        
        # Display stats
        st.metric("Messages", len(st.session_state.messages))
    
    # Display chat history
    display_chat_messages()

    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        process_user_input(user_input)


if __name__ == "__main__":
    main()
