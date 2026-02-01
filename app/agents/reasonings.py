from state.agent_state import AgentState
from config import get_llm, log_llm_interaction, ENABLE_LLM_REASONING, LLM_RETRY_ATTEMPTS
import json


# def planning_node(state: AgentState) -> AgentState:
#     """
#     Use LLM to analyze the query and create an intelligent action plan.
#     This is where the agent decides what to do autonomously using AI.
#     """
#     query = state['query']
#     document_metadata = state['document'].get('metadata', {})
#     sections = document_metadata.get('sections', [])
    
#     if not ENABLE_LLM_REASONING:
#         return fallback_planning(state)
    
#     # Create prompt for LLM to plan
#     planning_prompt = f"""You are an intelligent document analysis agent. Analyze the user's query and create an action plan.

# Available tools:
# 1. heading_search - Search for specific sections/headings in the document
# 2. format_checker - Check document format, structure, and completeness
# 3. diagram_checker - Find and analyze diagrams, figures, charts, or images
# 4. summarizer - Summarize document content or specific sections

# Document Info:
# - Sections found: {', '.join(sections[:10]) if sections else 'None detected'}
# - File type: {document_metadata.get('file_type', 'unknown')}

# User Query: "{query}"

# Analyze this query and respond with a JSON object containing:
# - goal: What the user wants to accomplish
# - plan: Array of tools to use in order
# - reasoning: Why these tools in this order

# Example responses:

# Query: "Is there an overview section?"
# {{
#     "goal": "Check if document contains overview section",
#     "plan": ["heading_search"],
#     "reasoning": "Need to search document structure for overview heading"
# }}

# Query: "check if document has overview, flow diagram and use case diagram"
# {{
#     "goal": "Verify presence of overview section and multiple diagram types",
#     "plan": ["heading_search", "diagram_checker"],
#     "reasoning": "First check for overview in headings, then search for flow and use case diagrams"
# }}

# Query: "Is there a conclusion? If yes, summarize it"
# {{
#     "goal": "Find and summarize conclusion section",
#     "plan": ["heading_search", "summarizer"],
#     "reasoning": "First locate conclusion section, then summarize its content"
# }}

# Query: "check if properly formatted"
# {{
#     "goal": "Validate document format and structure",
#     "plan": ["format_checker", "heading_search"],
#     "reasoning": "Check format compliance and document structure"
# }}

# Now analyze: "{query}"

# Respond ONLY with valid JSON, no additional text."""

#     llm = get_llm(temperature=0.1)
    
#     for attempt in range(LLM_RETRY_ATTEMPTS):
#         try:
#             response = llm.invoke(planning_prompt)
#             response_text = response.content.strip()
            
#             log_llm_interaction(planning_prompt, response_text)
            
#             # Clean response - remove markdown code blocks
#             if '```json' in response_text:
#                 response_text = response_text.split('```json')[1].split('```')[0].strip()
#             elif '```' in response_text:
#                 response_text = response_text.split('```')[1].split('```')[0].strip()
            
#             # Try to find JSON in the response
#             if '{' in response_text:
#                 start = response_text.find('{')
#                 end = response_text.rfind('}') + 1
#                 response_text = response_text[start:end]
            
#             plan_data = json.loads(response_text)
            
#             # Validate plan
#             if 'goal' not in plan_data or 'plan' not in plan_data:
#                 raise ValueError("Missing required fields in plan")
            
#             state['goal'] = plan_data['goal']
#             state['plan'] = plan_data['plan']
#             state['pending_actions'] = plan_data['plan'].copy()
#             state['reasoning'] = plan_data.get('reasoning', 'Plan created')
#             state['status'] = 'executing'
#             state['internal_notes'].append(f"LLM created plan: {plan_data['plan']}")
#             state['actions_taken'].append('planning:complete')
            
#             print(f"🎯 Goal: {state['goal']}")
#             print(f"📝 Reasoning: {state['reasoning']}")
#             print(f"🔧 Plan: {' → '.join(state['plan'])}\n")
            
#             return state
            
#         except Exception as e:
#             print(f"⚠️  LLM planning attempt {attempt + 1} failed: {str(e)}")
#             if attempt < LLM_RETRY_ATTEMPTS - 1:
#                 print("🔄 Retrying...")
#                 continue
    
#     # Fallback if all attempts fail
#     print("⚠️  All LLM attempts failed. Using fallback planning...")
#     return fallback_planning(state)

def planning_node(state: AgentState) -> AgentState:
    """
    Use LLM to analyze the query and create an intelligent action plan.
    This is where the agent decides what to do autonomously using AI.
    """
    query = state['query']
    document_metadata = state['document'].get('metadata', {})
    sections = document_metadata.get('sections', [])
    
    if not ENABLE_LLM_REASONING:
        return fallback_planning(state)
    
    planning_prompt = f"""You are an intelligent document analysis agent. Analyze the user's query and create an action plan.

Available tools:
1. heading_search - Search for specific sections/headings in the document
2. format_checker - Check document format, structure, and completeness
3. diagram_checker - Find and analyze diagrams, figures, charts, or images
4. summarizer - Summarize document content or specific sections

Document Info:
- Sections found: {', '.join(sections[:10]) if sections else 'None detected'}
- File type: {document_metadata.get('file_type', 'unknown')}

User Query: "{query}"

Analyze this query and respond with a JSON object containing:
- goal: What the user wants to accomplish
- plan: Array of tools to use in order
- reasoning: Why these tools in this order

Example responses:

Query: "Is there an overview section?"
{{
    "goal": "Check if document contains overview section",
    "plan": ["heading_search"],
    "reasoning": "Need to search document structure for overview heading"
}}

Query: "check if document has overview, flow diagram and use case diagram"
{{
    "goal": "Verify presence of overview section and multiple diagram types",
    "plan": ["heading_search", "diagram_checker"],
    "reasoning": "First check for overview in headings, then search for flow and use case diagrams"
}}

Now analyze: "{query}"

Respond ONLY with valid JSON, no additional text."""

    llm = get_llm(temperature=0.1)
    
    for attempt in range(LLM_RETRY_ATTEMPTS):
        try:
            response = llm.invoke(planning_prompt)
            response_text = response.content.strip()
            
            # IMPORTANT: Log but DON'T print/yield the raw JSON
            log_llm_interaction(planning_prompt, response_text)
            
            # Clean response - remove markdown code blocks
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            # Try to find JSON in the response
            if '{' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                response_text = response_text[start:end]
            
            plan_data = json.loads(response_text)
            
            # Validate plan
            if 'goal' not in plan_data or 'plan' not in plan_data:
                raise ValueError("Missing required fields in plan")
            
            # Extract clean strings (not the raw JSON)
            state['goal'] = str(plan_data['goal'])
            state['plan'] = plan_data['plan']
            state['pending_actions'] = plan_data['plan'].copy()
            state['reasoning'] = str(plan_data.get('reasoning', 'Plan created'))
            state['status'] = 'executing'
            state['internal_notes'].append(f"LLM created plan: {plan_data['plan']}")
            state['actions_taken'].append('planning:complete')
            
            # Print to console for debugging (this won't go to the stream)
            print(f"🎯 Goal: {state['goal']}")
            print(f"📝 Reasoning: {state['reasoning']}")
            print(f"🔧 Plan: {' → '.join(state['plan'])}\n")
            
            return state
            
        except Exception as e:
            print(f"⚠️  LLM planning attempt {attempt + 1} failed: {str(e)}")
            if attempt < LLM_RETRY_ATTEMPTS - 1:
                print("🔄 Retrying...")
                continue
    
    # Fallback if all attempts fail
    print("⚠️  All LLM attempts failed. Using fallback planning...")
    return fallback_planning(state)


def fallback_planning(state: AgentState) -> AgentState:
    """Fallback planning using simple pattern matching."""
    query = state['query'].lower()
    plan = []
    goal = ""
    
    # Enhanced pattern matching
    if 'overview' in query and ('diagram' in query or 'figure' in query):
        goal = "Check for overview and diagrams"
        plan = ['heading_search', 'diagram_checker']
        reasoning = "Query asks for both overview and diagrams"
    elif any(word in query for word in ['overview', 'summary', 'about', 'summarize']):
        goal = "Find and summarize document overview/summary"
        plan = ['heading_search', 'summarizer']
        reasoning = "Query asks for overview/summary"
    elif any(word in query for word in ['diagram', 'figure', 'chart', 'image', 'flow', 'use case']):
        goal = "Locate and analyze diagrams/figures"
        plan = ['diagram_checker', 'heading_search']
        reasoning = "Query asks about diagrams"
    elif any(word in query for word in ['format', 'structure', 'organized', 'layout']):
        goal = "Check document format and structure"
        plan = ['format_checker', 'heading_search']
        reasoning = "Query asks about format"
    elif any(word in query for word in ['conclusion', 'ending', 'final']):
        goal = "Find and analyze conclusion section"
        plan = ['heading_search', 'summarizer']
        reasoning = "Query asks about conclusion"
    elif any(word in query for word in ['complete', 'missing', 'validate', 'check']):
        goal = "Validate document completeness"
        plan = ['format_checker', 'heading_search', 'diagram_checker']
        reasoning = "Query asks for validation"
    else:
        goal = "Comprehensive document analysis"
        plan = ['heading_search', 'format_checker', 'summarizer']
        reasoning = "General query - comprehensive analysis"
    
    state['goal'] = goal
    state['plan'] = plan
    state['pending_actions'] = plan.copy()
    state['reasoning'] = reasoning
    state['status'] = 'executing'
    state['internal_notes'].append(f"Created plan: {plan}")
    state['actions_taken'].append('planning:complete')
    
    return state


def reasoning_node(state: AgentState) -> AgentState:
    """
    Decide what to do next based on current state.
    Can adapt plan based on observations.
    """
    state['loop_counter'] += 1
    
    # Check if we need to re-plan based on observations
    if state['observations'] and len(state['observations']) > 0:
        last_obs = state['observations'][-1]
        
        # If we found something interesting, maybe adjust plan
        if 'not found' in last_obs.lower() and 'heading_search' in state['actions_taken']:
            # Heading not found, maybe try summarizer to get context
            if 'summarizer' not in state['pending_actions'] and 'summarizer' not in state['actions_taken']:
                state['pending_actions'].append('summarizer')
                state['internal_notes'].append("Added summarizer to get more context")
    
    if state['pending_actions']:
        next_action = state['pending_actions'][0]
        state['reasoning'] = f"Will execute: {next_action}"
        state['actions_taken'].append(f'reasoning:plan_to_execute:{next_action}')
    else:
        state['reasoning'] = "All actions completed, will synthesize results"
        state['actions_taken'].append('reasoning:synthesis')
    
    return state
def synthesis_node(state: AgentState) -> AgentState:
    """
    Use LLM to synthesize all tool outputs into a comprehensive final answer.
    """
    query = state['query']
    goal = state['goal']
    outputs = state['tool_outputs']
    
    if not ENABLE_LLM_REASONING:
        return fallback_synthesis(state)
    
    # Prepare tool outputs summary
    tool_results = []
    for tool_name, output in outputs.items():
        tool_results.append(f"{tool_name}:\n  Status: {output['status']}\n  Summary: {output['summary']}\n  Details: {json.dumps(output['details'], indent=2)}")
    
    synthesis_prompt = f"""You are analyzing a document based on a user's query. You have gathered information using various tools.

Original Query: "{query}"
Goal: {goal}

Tool Results:
{chr(10).join(tool_results)}

Based on these tool results, provide a clear, direct answer to the user's query.

Guidelines:
- Answer the specific question asked
- Be concise but complete
- If the query asks "is there X?", clearly say YES or NO first
- If asked to summarize, provide the actual summary from the tool results
- Reference specific findings from the tools
- If something wasn't found, say so clearly
- Use natural, conversational language

Provide your answer now:"""

    llm = get_llm(temperature=0.3)
    
    for attempt in range(LLM_RETRY_ATTEMPTS):
        try:
            response = llm.invoke(synthesis_prompt)
            final_answer = response.content.strip()
            
            log_llm_interaction(synthesis_prompt, final_answer)
            
            state['final_answer'] = final_answer
            state['status'] = 'completed'
            state['actions_taken'].append('synthesis:complete')
            
            return state
            
        except Exception as e:
            print(f"⚠️  LLM synthesis attempt {attempt + 1} failed: {str(e)}")
            if attempt < LLM_RETRY_ATTEMPTS - 1:
                print("🔄 Retrying...")
                continue
    
    # Fallback if all attempts fail
    print("⚠️  All LLM attempts failed. Using fallback synthesis...")
    return fallback_synthesis(state)


# async def synthesis_node(state: AgentState) -> AgentState:
#     """
#     Use LLM to synthesize all tool outputs into a comprehensive final answer.
#     """
#     query = state['query']
#     goal = state['goal']
#     outputs = state['tool_outputs']
    
#     if not ENABLE_LLM_REASONING:
#         return fallback_synthesis(state)
    
#     # Prepare tool outputs summary
#     tool_results = []
#     for tool_name, output in outputs.items():
#         tool_results.append(f"{tool_name}:\n  Status: {output['status']}\n  Summary: {output['summary']}\n  Details: {json.dumps(output['details'], indent=2)}")
    
#     synthesis_prompt = f"""You are analyzing a document based on a user's query. You have gathered information using various tools.

# Original Query: "{query}"
# Goal: {goal}

# Tool Results:
# {chr(10).join(tool_results)}

# Based on these tool results, provide a clear, direct answer to the user's query.

# Guidelines:
# - Answer the specific question asked
# - Be concise but complete
# - If the query asks "is there X?", clearly say YES or NO first
# - If asked to summarize, provide the actual summary from the tool results
# - Reference specific findings from the tools
# - If something wasn't found, say so clearly
# - Use natural, conversational language

# Provide your answer now:"""
    
#     llm = get_llm(temperature=0.3) # Ensure streaming=True
#     try:
#         # We use ainvoke so the graph doesn't block
#         response = await llm.ainvoke(synthesis_prompt)
        
#         state['final_answer'] = response.content
#         state['status'] = 'completed'
#         return state

#     except Exception as e:
#         state['error_message'] = str(e)
#         state['status'] = 'error'
#         return state
    
#     # Fallback if all attempts fail
#     print("⚠️  All LLM attempts failed. Using fallback synthesis...")
#     return fallback_synthesis(state)


def fallback_synthesis(state: AgentState) -> AgentState:
    """Fallback synthesis without LLM."""
    query = state['query']
    outputs = state['tool_outputs']
    
    answer_parts = [f"Based on analyzing the document for: '{query}'\n"]
    
    for tool_name, output in outputs.items():
        answer_parts.append(f"• {output['summary']}")
    
    # Add specific answers based on query
    query_lower = query.lower()
    if 'overview' in query_lower:
        if 'heading_search' in outputs:
            sections = outputs['heading_search']['details'].get('sections', [])
            if any('overview' in s.lower() for s in sections):
                answer_parts.append("\n✅ YES - Document has an Overview section")
            else:
                answer_parts.append("\n❌ NO - No Overview section found")
    
    if any(word in query_lower for word in ['diagram', 'figure', 'flow', 'use case']):
        if 'diagram_checker' in outputs:
            status = outputs['diagram_checker']['status']
            if status == 'found':
                answer_parts.append("\n✅ YES - Diagrams/figures found in document")
            else:
                answer_parts.append("\n❌ NO - No diagrams found")
    
    if 'conclusion' in query_lower:
        if 'heading_search' in outputs:
            sections = outputs['heading_search']['details'].get('sections', [])
            if any('conclusion' in s.lower() for s in sections):
                answer_parts.append("\n✅ YES - Document has a Conclusion section")
            else:
                answer_parts.append("\n❌ NO - No Conclusion section found")
    
    state['final_answer'] = '\n'.join(answer_parts)
    state['status'] = 'completed'
    state['actions_taken'].append('synthesis:complete')
    
    return state