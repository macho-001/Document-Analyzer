from langchain_ollama import ChatOllama
from typing import Optional

# LLM Configuration
LLM_MODEL = "gemini-3-flash-preview:cloud"
LLM_TEMPERATURE = 0.2

# Agent Configuration
DEFAULT_MAX_ITERATIONS = 50
DEFAULT_LOOP_DETECTION_WINDOW = 3

# Tool Configuration
AVAILABLE_TOOLS = [
    "format_checker",
    "heading_search",
    "diagram_checker",
    "summarizer"
]

# Reasoning Configuration
ENABLE_LLM_REASONING = True  # Set to False to use fallback logic only
LLM_RETRY_ATTEMPTS = 2  # Number of times to retry LLM on failure


def get_llm(temperature: Optional[float] = None, model: Optional[str] = None):
    """
    Get configured LLM instance.
    
    Args:
        temperature: Override default temperature
        model: Override default model
        
    Returns:
        ChatOllama instance
    """
    return ChatOllama(
        model=model or LLM_MODEL,
        temperature=temperature if temperature is not None else LLM_TEMPERATURE,
        streaming=True
    )


def get_llm_with_structured_output():
    """
    Get LLM configured for structured JSON output.
    Some models support structured output modes.
    
    Returns:
        ChatOllama instance optimized for JSON
    """
    return ChatOllama(
        model=LLM_MODEL,
        temperature=0.1,  # Lower temp for more consistent JSON
        format="json"  # Some Ollama models support this
    )


# Logging Configuration
VERBOSE_LOGGING = True
LOG_LLM_PROMPTS = False  # Set to True to debug LLM interactions
LOG_LLM_RESPONSES = False

# Output Configuration
PRETTY_PRINT_STATE = True
SHOW_INTERNAL_NOTES = True


def log_llm_interaction(prompt: str, response: str):
    """
    Log LLM interactions if enabled.
    
    Args:
        prompt: The prompt sent to LLM
        response: The LLM's response
    """
    if LOG_LLM_PROMPTS:
        print("\n" + "="*60)
        print("LLM PROMPT:")
        print("="*60)
        print(prompt)
    
    if LOG_LLM_RESPONSES:
        print("\n" + "="*60)
        print("LLM RESPONSE:")
        print("="*60)
        print(response)
        print("="*60 + "\n")