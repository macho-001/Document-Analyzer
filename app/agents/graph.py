from langgraph.graph import StateGraph, END
from state.agent_state import AgentState, create_initial_state
from agents.reasonings import planning_node, reasoning_node, synthesis_node
from agents.actions import tool_node, user_input_node
from tools.critic import critic_node, should_continue


def create_agent_graph() -> StateGraph:
    """
    Create the autonomous agent execution graph.
    
    Graph flow:
    1. START -> planning_node (analyze query and create plan)
    2. planning -> reasoning_node (decide next action)
    3. reasoning -> tool_node (execute tools)
    4. tool -> critic_node (validate and check completion)
    5. critic -> routing:
       - If awaiting_user_input -> user_input_node -> reasoning_node
       - If ready_for_synthesis -> synthesis_node -> END
       - If completed/error -> END
       - Otherwise -> reasoning_node (continue)
    
    Returns:
        Compiled StateGraph ready for execution
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("planning", planning_node)
    workflow.add_node("reasoning", reasoning_node)
    workflow.add_node("tool_execution", tool_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("synthesis", synthesis_node)
    workflow.add_node("user_input", user_input_node)
    
    # Set entry point
    workflow.set_entry_point("planning")
    
    # Add edges
    workflow.add_edge("planning", "reasoning")
    workflow.add_edge("reasoning", "tool_execution")
    workflow.add_edge("tool_execution", "critic")
    workflow.add_edge("user_input", "reasoning")
    workflow.add_edge("synthesis", END)
    
    # Conditional routing from critic
    workflow.add_conditional_edges(
        "critic",
        should_continue,
        {
            "reasoning": "reasoning",
            "synthesis": "synthesis",
            "user_input": "user_input",
            "end": END
        }
    )
    
    return workflow.compile()


def run_agent(query: str, document: dict = None, verbose: bool = True) -> AgentState:
    """
    Run the autonomous agent with just a query!
    
    Args:
        query: User's question (e.g., "Is there an overview in this document?")
        document: The document to analyze (dict with content, metadata, etc.)
        verbose: Whether to print progress
        
    Returns:
        Final agent state with answer
    """
    # Create initial state
    initial_state = create_initial_state(query=query, document=document)
    
    # Create and run graph
    app = create_agent_graph()
    
    if verbose:
        print(f"\n🤖 Agent received query: '{query}'")
        print("🧠 Agent is planning...\n")
    
    try:
        final_state = app.invoke(initial_state)
        
        if verbose:
            print_execution_summary(final_state)
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ Agent execution failed: {str(e)}")
        raise


async def run_agent_stream(query: str, document: dict):
    """
    Asynchronous generator that yields tokens for the UI.
    """
    initial_state = create_initial_state(query=query, document=document)
    app = create_agent_graph()

    # We use astream_events to catch tokens from the LLM mid-execution
    async for event in app.astream_events(initial_state, version="v2"):
        kind = event["event"]
        if kind == "on_chain_start" and event["name"] in ["planning", "reasoning", "tool_execution", "synthesis"]:
            node_name = event["name"].replace("_", " ").title()
            yield f"🔄 [Working: {node_name}...]\n"
        # Handle Token Streaming (The actual text answer)
        # In LangGraph, synthesis_node usually generates the final text.
        # This captures tokens from the chat model during that (and other) nodes.
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                yield content

        # OPTIONAL: Handle Node Transitions (e.g., telling the user what the agent is doing)
        elif kind == "on_chain_start" and event["name"] in ["planning", "reasoning", "synthesis"]:
            # You could yield special tags to show status in UI
            # yield f" [Status: {event['name']}...] "
            pass

    print("\n\n✅ Done")

# async def run_agent_stream_v2(query: str, document: dict):
#         initial_state = create_initial_state(query=query, document=document)
#         app = create_agent_graph()

#         async for event in app.astream_events(initial_state, version="v2"):
#             kind = event["event"]
#             name = event["name"]

#             # 1. Stream the Planning Phase Results
#             if kind == "on_chain_end" and name == "planning":
#                 output = event["data"]["output"]
#                 goal = output.get('goal', '')
#                 reasoning = output.get('reasoning', '')
                
#                 yield f"THOUGHT: \n### 🎯 Goal\n{goal}\n"
#                 yield f"THOUGHT: \n### 🧠 Strategy\n{reasoning}\n"
#                 yield f"THOUGHT: \n---\n" # Divider before the answer starts

#             # 2. Stream the Reasoning/Thought Process (Optional, if you want step-by-step)
#             elif kind == "on_chain_end" and name == "reasoning":
#                 output = event["data"]["output"]
#                 thought = output.get('thought', '')
#                 if thought:
#                     yield f"\n> **Thinking:** {thought}\n"

#             # 3. Stream the Actual Final Answer (Tokens)
#             elif kind == "on_chat_model_stream":
#                 content = event["data"]["chunk"].content
#                 if content:
#                     yield f"ANSWER:{content}"
# version 3
# async def run_agent_stream_v2(query: str, document: dict):
#     initial_state = create_initial_state(query=query, document=document)
#     app = create_agent_graph()

#     async for event in app.astream_events(initial_state, version="v2"):
#         kind = event["event"]
#         name = event["name"]

#         # 1. CATCH THE PLANNING NODE OUTPUT
#         if kind == "on_chain_end" and name == "planning":
#             output = event["data"]["output"]
#             # Extract the fields from the state returned by planning_node
#             goal = output.get('goal', '')
#             reasoning = output.get('reasoning', '')
#             plan = " → ".join(output.get('plan', []))
            
#             # Yield as a formatted thought
#             yield f"THOUGHT:\n### 🎯 Goal\n{goal}\n\n"
#             yield f"THOUGHT:### 🧠 Strategy\n{reasoning}\n\n"
#             yield f"THOUGHT:### 🔧 Action Plan\n`{plan}`\n\n---\n"

#         # 2. CATCH THE FINAL LLM STREAM
#         elif kind == "on_chat_model_stream":
#             content = event["data"]["chunk"].content
#             if content:
#                 yield f"ANSWER:{content}"

#version#4
async def run_agent_stream_v2(query: str, document: dict):
    initial_state = create_initial_state(query=query, document=document)
    app = create_agent_graph()

    planning_shown = False  # Track if we've shown planning output

    async for event in app.astream_events(initial_state, version="v2"):
        kind = event["event"]
        name = event["name"]

        # 1. CATCH THE PLANNING NODE OUTPUT
        if kind == "on_chain_end" and name == "planning" and not planning_shown:
            output = event["data"]["output"]
            
            # Only extract clean, parsed fields from the state
            goal = output.get('goal', '')
            reasoning = output.get('reasoning', '')
            plan = output.get('plan', [])
            
            # Validate that we have actual data (not raw JSON strings)
            if goal and isinstance(goal, str) and not goal.strip().startswith('{'):
                yield f"THOUGHT:\n### 🎯 Goal\n{goal}\n\n"
            
            if reasoning and isinstance(reasoning, str) and not reasoning.strip().startswith('{'):
                yield f"THOUGHT:### 🧠 Strategy\n{reasoning}\n\n"
            
            if plan and isinstance(plan, list):
                plan_str = " → ".join(plan)
                yield f"THOUGHT:### 🔧 Action Plan\n`{plan_str}`\n\n---\n"
            
            planning_shown = True

        # 2. CATCH LLM STREAMING FROM SYNTHESIS NODE
        elif kind == "on_chat_model_stream":
            # Only stream content from the synthesis node (final answer)
            # Ignore any LLM streams from the planning node
            if name == "synthesis" or "synthesis" in str(event.get("tags", [])):
                content = event["data"]["chunk"].content
                if content:
                    # Additional filter: Don't send if it looks like JSON
                    if not (content.strip().startswith('{') or 
                            '"goal"' in content or 
                            '"reasoning"' in content or
                            '"plan"' in content):
                        yield f"ANSWER:{content}"
        
        # 3. FALLBACK: Catch the final answer from state if streaming didn't work
        elif kind == "on_chain_end" and name == "synthesis":
            output = event["data"]["output"]
            final_answer = output.get('final_answer', '')
            
            if final_answer and isinstance(final_answer, str):
                # Only yield if it's not JSON
                if not final_answer.strip().startswith('{'):
                    yield f"ANSWER:{final_answer}"


def print_execution_summary(state: AgentState) -> None:
    """Print a formatted summary of agent execution."""
    print("\n" + "="*70)
    print("📋 AGENT PLAN")
    print("="*70)
    print(f"Goal: {state['goal']}")
    print(f"Plan: {' → '.join(state['plan'])}")
    
    print("\n" + "="*70)
    print("🔍 OBSERVATIONS")
    print("="*70)
    for obs in state['observations']:
        print(f"  • {obs}")
    
    print("\n" + "="*70)
    print("✨ FINAL ANSWER")
    print("="*70)
    print(state['final_answer'])
    print("="*70 + "\n")