from state.agent_state import AgentState


def critic_node(state: AgentState) -> AgentState:
    """Validate and determine next steps."""
    # Check errors
    if state.get('error_message'):
        state['status'] = 'error'
        return state
    
    # Check iteration limit
    if state['loop_counter'] >= state['max_iterations']:
        state['status'] = 'max_iterations_reached'
        return state
    
    # Check if awaiting input
    if state.get('awaiting_user_input'):
        state['status'] = 'awaiting_input'
        return state
    
    # Check if all actions done
    if not state['pending_actions']:
        state['status'] = 'ready_for_synthesis'
        return state
    
    # Continue
    state['status'] = 'executing'
    return state


def should_continue(state: AgentState) -> str:
    """Route based on status."""
    status = state['status']
    
    if status == 'awaiting_input':
        return "user_input"
    elif status == 'ready_for_synthesis':
        return "synthesis"
    elif status in ['completed', 'error', 'max_iterations_reached']:
        return "end"
    else:
        return "reasoning"