from state.agent_state import AgentState
from tools.format_checker import check_format
from tools.heading_search import search_headings
from tools.summarizer import summarize_content
from tools.diagram_checker import check_diagram


TOOL_REGISTRY = {
    "format_checker": check_format,
    "heading_search": search_headings,
    "summarizer": summarize_content,
    "diagram_checker": check_diagram
}


def tool_node(state: AgentState) -> AgentState:
    """Execute the planned tool with the document."""
    if not state['pending_actions']:
        return state
    
    tool_name = state['pending_actions'].pop(0)
    tool_fn = TOOL_REGISTRY.get(tool_name)
    
    if not tool_fn:
        state['internal_notes'].append(f"Unknown tool: {tool_name}")
        state['observations'].append(f"Error: Tool {tool_name} not found")
        return state
    
    # Execute tool with actual document
    output = tool_fn(state['document'])
    state['tool_outputs'][tool_name] = output
    
    # Record observation
    observation = f"{tool_name}: {output['summary']}"
    state['observations'].append(observation)
    state['actions_taken'].append(f"tool_executed:{tool_name}")
    
    return state


def user_input_node(state: AgentState) -> AgentState:
    """Handle user input when agent needs clarification."""
    if state.get('awaiting_user_input'):
        print("\n⏸️  Agent is waiting for user input...")
        # In real implementation, collect actual input
        state['observations'].append("User input received")
        state['awaiting_user_input'] = False
        state['actions_taken'].append("user_input:collected")
    return state
