from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict):
    """Enhanced state that supports autonomous planning."""
    # User input
    query: str
    document: Dict[str, Any]  # The document to analyze
    
    # Planning
    goal: str  # Derived from query
    plan: List[str]  # List of actions to execute
    pending_actions: List[str]
    
    # Execution tracking
    actions_taken: List[str]
    tool_outputs: Dict[str, Any]
    observations: List[str]
    
    # Agent reasoning
    reasoning: str  # Current reasoning step
    internal_notes: List[str]
    
    # Control flow
    status: str  # planning, executing, awaiting_input, completed, error
    awaiting_user_input: bool
    user_response: str
    
    # Limits
    loop_counter: int
    max_iterations: int
    
    # Results
    final_answer: str
    error_message: str


def create_initial_state(query: str, document: Dict[str, Any] = None) -> AgentState:
    """Create initial state for autonomous agent."""
    return {
        'query': query,
        'document': document or {},
        'goal': '',
        'plan': [],
        'pending_actions': [],
        'actions_taken': [],
        'tool_outputs': {},
        'observations': [],
        'reasoning': '',
        'internal_notes': [],
        'status': 'planning',
        'awaiting_user_input': False,
        'user_response': '',
        'loop_counter': 0,
        'max_iterations': 20,
        'final_answer': '',
        'error_message': ''
    }