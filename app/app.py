from flask import Flask, render_template, request, jsonify, session, Response, stream_with_context
import tempfile
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import asyncio
from agents.graph import run_agent_stream, run_agent_stream_v2 
from main import load_document

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
app.secret_key = 'your-secret-key-here-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config.update(
    SESSION_PERMANENT=False,  # cookie will expire when the browser closes
    SESSION_TYPE='filesystem' # Or your preferred session type
)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'md'}
documents_store = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/')
# def index():
#     if 'conversations' not in session:
#         session['conversations'] = []
#     if 'session_id' not in session:
#         session['session_id'] = os.urandom(16).hex()
    
#     conversation_index = request.args.get('conversation', type=int)
#     current_conversation = None
#     if conversation_index is not None and conversation_index < len(session['conversations']):
#         current_conversation = session['conversations'][conversation_index]
    
#     session_id = session['session_id']
#     document_info = None
#     if session_id in documents_store:
#         document_info = session.get('document_info')
    
#     return render_template('index.html', 
#                          chat_history=session.get('conversations', []),
#                          current_conversation=current_conversation,
#                          document_info=document_info)
@app.route('/')
def index():
    if 'conversations' not in session:
        session['conversations'] = []
    if 'session_id' not in session:
        session['session_id'] = os.urandom(16).hex()
    
    conversation_index = request.args.get('conversation', type=int)
    current_conversation = None
    
    # 1. Logic for existing conversations
    if conversation_index is not None and conversation_index < len(session['conversations']):
        current_conversation = session['conversations'][conversation_index]
        # When viewing an old conversation, we do NOT want the "active" upload pill to show
        document_info = None 
    else:
        # 2. Logic for New Chat / Fresh Uploads
        session_id = session['session_id']
        document_info = None
        # Only show the pill if we are NOT in an old conversation
        if session_id in documents_store:
            document_info = session.get('document_info')
    
    return render_template('index.html', 
                         chat_history=session.get('conversations', []),
                         current_conversation=current_conversation,
                         document_info=document_info,
                         conversation_index=conversation_index)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        document = load_document(filepath)
        
        if 'session_id' not in session:
            session['session_id'] = os.urandom(16).hex()
        session_id = session['session_id']
        
        # documents_store[session_id] = {'document': document, 'filepath': filepath}
        documents_store[session_id] = {
                                        'document': document,
                                        'filepath': filepath,
                                        'loaded': True
                                      }
        print("SESSION ID:", session.get('session_id'))
        print("DOCUMENT STORE KEYS:", list(documents_store.keys()))
        
        metadata = document.get('metadata', {})
        doc_info = {
            'filename': metadata.get('filename', filename),
            'file_type': document.get('file_type', 'unknown').upper(),
            'num_pages': metadata.get('num_pages'),
            'sections': len(metadata.get('sections', []))
        }
        session['document_info'] = doc_info
        session.modified = True
        return jsonify({'success': True, 'document_info': doc_info})
    except Exception as e:
        return jsonify({'error': f'Failed to load document: {str(e)}'}), 500

# @app.route('/analyze-stream', methods=['POST'])
# def analyze_stream():
#     """Streams the agent output token by token"""
#     data = request.json
#     query = data.get('query', '').strip()
#     session_id = session.get('session_id')

#     if not query:
#         return jsonify({'error': 'Please enter a question'}), 400
#     if not session_id or session_id not in documents_store:
#         return jsonify({'error': 'Please upload a document first'}), 400

#     document = documents_store[session_id]['document']
#     # def generate():
#     #     loop = asyncio.new_event_loop()
#     #     asyncio.set_event_loop(loop)
        
#     #     # Get the async generator
#     #     gen = run_agent_stream_v2(query=query, document=document)
        
#     #     try:
            
#     #         # version 3 stream compatible
#     #         while True:
#     #             try:
#     #                 token = loop.run_until_complete(gen.__anext__())
                    
#     #                 # If it's a dictionary (The raw state from LangGraph), skip it 
#     #                 # or force it into thoughts because we already handled it above
#     #                 if isinstance(token, dict):
#     #                     # Option: Skip it to avoid double-printing
#     #                     continue 

#     #                 if isinstance(token, str):
#     #                     # Ensure it has a prefix
#     #                     if token.startswith("THOUGHT:") or token.startswith("ANSWER:"):
#     #                         payload = token
#     #                     else:
#     #                         # If it's a thought step from reasoning_node, prefix it
#     #                         if "> **Thinking:**" in token:
#     #                             payload = f"THOUGHT:{token}"
#     #                         else:
#     #                             payload = f"ANSWER:{token}"
                        
#     #                     yield f"data: {json.dumps({'type': 'token', 'content': payload})}\n\n"
                        
#     #             except StopAsyncIteration:
#     #                 break
            
#     #         yield f"data: {json.dumps({'type': 'done'})}\n\n"
#     #     except Exception as e:
#     #         yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
#     #     finally:
#     #         try:
#     #             pending = asyncio.all_tasks(loop)
#     #             loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
#     #             loop.close()
#     #         except:
#     #             pass
#     def generate():
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         gen = run_agent_stream_v2(query=query, document=document)
        
#         try:
#             while True:
#                 try:
#                     token = loop.run_until_complete(gen.__anext__())
                    
#                     # 1. Skip LangGraph state dictionaries (raw data)
#                     if isinstance(token, dict):
#                         continue 
#                     if isinstance(token, str):
#                         if '{"goal":' in token or '"plan":' in token or token.startswith("THOUGHT:"):
#                             payload = f"THOUGHT:{token.replace('THOUGHT:', '')}"
#                         elif token.startswith("ANSWER:"):
#                             payload = token
#                         else:
#                             # If we are sure this is the final output node of your agent
#                             payload = f"ANSWER:{token}" 
                        
#                         yield f"data: {json.dumps({'type': 'token', 'content': payload})}\n\n"
#                     # if isinstance(token, str):
#                     #     # 2. Check for Plan/Internal JSON (Surgical Filter)
#                     #     # If it looks like JSON or specific planning text, it's a THOUGHT
#                     #     if '{"goal":' in token or '"plan":' in token:
#                     #         payload = f"THOUGHT:{token}"
#                     #     elif token.startswith("THOUGHT:") or "> **Thinking:**" in token:
#                     #         payload = f"THOUGHT:{token.replace('THOUGHT:', '')}"
#                     #     elif token.startswith("ANSWER:"):
#                     #         payload = token
#                     #     else:
#                     #         # 3. Default fallback: If it's not explicitly an answer, 
#                     #         # treat it as a thought to keep the main answer clean
#                     #         payload = f"ANSWER:{token}"
                        
#                     #     yield f"data: {json.dumps({'type': 'token', 'content': payload})}\n\n"
                        
#                 except StopAsyncIteration:
#                     break
            
#             yield f"data: {json.dumps({'type': 'done'})}\n\n"
#         except Exception as e:
#             yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
#         finally:
#             loop.close()
#     return Response(stream_with_context(generate()), content_type='text/event-stream')
@app.route('/analyze-stream', methods=['POST'])
def analyze_stream():
    """Streams the agent output token by token"""
    data = request.json
    query = data.get('query', '').strip()
    session_id = session.get('session_id')
    print("SESSION ID:", session.get('session_id'))
    print("DOCUMENT STORE KEYS:", list(documents_store.keys()))

    # if not query:
    #     return jsonify({'error': 'Please enter a question'}), 400
    # if not session_id or session_id not in documents_store:
    #     return jsonify({'error': 'Please upload a document first'}), 400
    # entry = documents_store.get(session_id)

    # if not entry or not entry.get('loaded'):
    #     return jsonify({'error': 'Please upload a document first'}), 400
    # # if not query:
    #     def generate_error_query():
    #         yield f"data: {json.dumps({'type': 'error', 'message': 'Please enter a question'})}\n\n"
    #         yield f"data: {json.dumps({'type': 'done'})}\n\n"
    #     return Response(stream_with_context(generate_error_query()), content_type='text/event-stream')

    entry = documents_store.get(session_id)
    if not entry or not entry.get('document'):
        # STOP here: return immediately without generating SSE
        return jsonify({'error': 'Please upload a document first'}), 400

    document = entry['document']

    # document = documents_store[session_id]['document']
    
    def generate():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        gen = run_agent_stream_v2(query=query, document=document)
        
        try:
            while True:
                try:
                    token = loop.run_until_complete(gen.__anext__())
                    
                    # Skip raw LangGraph state dictionaries
                    if isinstance(token, dict):
                        continue 
                    
                    if isinstance(token, str):
                        # More robust JSON detection
                        # Check for common JSON patterns and keywords
                        stripped = token.strip()
                        is_json_data = (
                            stripped.startswith('{') or 
                            stripped.startswith('[') or
                            stripped.endswith('}') or
                            '"goal":' in token or 
                            '"plan":' in token or
                            '"reasoning":' in token or
                            '"action":' in token or
                            '"tool":' in token or
                            # Catch partial JSON fragments
                            ('"' in token and ':' in token and any(kw in token for kw in ['goal', 'plan', 'reasoning', 'action']))
                        )
                        
                        if is_json_data:
                            # This is internal planning/reasoning - send as THOUGHT
                            payload = f"THOUGHT:{token}"
                        elif token.startswith("THOUGHT:"):
                            # Already prefixed as thought
                            payload = token
                        elif token.startswith("ANSWER:"):
                            # Already prefixed as answer
                            payload = token
                        else:
                            # Default: treat unprefixed content as answer
                            payload = f"ANSWER:{token}"
                        
                        yield f"data: {json.dumps({'type': 'token', 'content': payload})}\n\n"
                        
                except StopAsyncIteration:
                    break
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        finally:
            try:
                loop.close()
            except:
                pass
    
    return Response(stream_with_context(generate()), content_type='text/event-stream')

from langchain_core.messages import HumanMessage, SystemMessage
from config import get_llm

# def generate_meaningful_title(query):
#     """Uses Ollama to generate a 3-5 word title for the chat."""
#     try:
#         llm = get_llm(temperature=0.3) # Low temperature for consistent titles
        
#         prompt = [
#             SystemMessage(content="You are a helpful assistant that summarizes user queries into very short, meaningful titles. Output ONLY the title (3-5 words). No quotes, no preamble."),
#             HumanMessage(content=f"Summarize this query into a short title: {query}")
#         ]
        
#         response = llm.invoke(prompt)
#         title = response.content.strip().replace('"', '').replace('*', '')
        
#         # Clean up in case it returns something too long
#         if len(title.split()) > 7:
#             title = " ".join(title.split()[:5]) + "..."
            
#         return title
#     except Exception as e:
#         print(f"Title generation failed: {e}")
#         return query[:30] + "..." # Fallback to truncated query

# @app.route('/save-chat', methods=['POST'])
# def save_chat():
#     data = request.json
#     query = data.get('query')
#     answer = data.get('answer')
#     conversation_index = data.get('conversation_index')
    
#     if 'conversations' not in session:
#         session['conversations'] = []

#     # If it's a new chat
#     if conversation_index is None or conversation_index == "" or conversation_index == "null":
#         session['conversations'].append({
#             'title': query[:30] + "...", # Simple naming for now
#             'timestamp': datetime.now().strftime("%H:%M"),
#             'queries': [query],
#             'answers': [answer]
#         })
#         res_idx = len(session['conversations']) - 1
#     else:
#         res_idx = int(conversation_index)
#         session['conversations'][res_idx]['queries'].append(query)
#         session['conversations'][res_idx]['answers'].append(answer)

#     session.modified = True
    
#     # We return the FULL list of conversations so the frontend 
#     # doesn't have to call /get-conversations separately
#     return jsonify({
#         'success': True, 
#         'conversation_index': res_idx,
#         'all_conversations': session['conversations'] 
#     })


from langchain_core.messages import HumanMessage, SystemMessage

def generate_meaningful_title(query):
    """Uses Ollama to generate a clean 3-5 word title."""
    try:
        # Using your existing get_llm helper
        llm = get_llm(temperature=0.1) 
        
        prompt = [
            SystemMessage(content="Summarize the user's request into a 3-5 word title. Output ONLY the title text. No quotes, no explanations, no periods."),
            HumanMessage(content=query)
        ]
        
        response = llm.invoke(prompt)
        # Clean up any potential junk formatting
        title = response.content.strip().replace('"', '').replace('*', '')
        
        # Final safety check on length
        if len(title.split()) > 8:
            title = " ".join(title.split()[:5]) + "..."
            
        return title
    except Exception as e:
        print(f"Naming Error: {e}")
        return query[:30] + "..."

@app.route('/save-chat', methods=['POST'])
def save_chat():
    try:
        data = request.json
        query = data.get('query')
        answer = data.get('answer', '')
        conv_idx_raw = data.get('conversation_index')

        # Robust index handling
        conversation_index = None
        if conv_idx_raw not in [None, "null", "", "undefined"]:
            try:
                conversation_index = int(conv_idx_raw)
            except (ValueError, TypeError):
                conversation_index = None

        if 'conversations' not in session:
            session['conversations'] = []

        timestamp = datetime.now().strftime("%H:%M")

        if conversation_index is None:
            is_new = True
        else:
            # Check if the index actually exists in the current session
            if 'conversations' in session and conversation_index < len(session['conversations']):
                is_new = False
            else:
                is_new = True # Force new if index is invalid/out of range

        if is_new:
            meaningful_title = generate_meaningful_title(query)
            session['conversations'].append({
                'title': meaningful_title,
                'timestamp': timestamp,
                'queries': [query],
                'answers': [answer]
            })
            res_idx = len(session['conversations']) - 1
        else:
            res_idx = conversation_index
            session['conversations'][res_idx]['queries'].append(query)
            session['conversations'][res_idx]['answers'].append(answer)

        session.modified = True
        return jsonify({
            'success': True, 
            'conversation_index': res_idx,
            'all_conversations': session['conversations'] 
        })

    except Exception as e:
        print(f"ERROR IN SAVE-CHAT: {e}") # This shows up in your terminal
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/clear-document', methods=['POST'])
def clear_document():
    """Clear uploaded document"""
    session_id = session.get('session_id')
    
    if session_id and session_id in documents_store:
        # Clean up temporary file
        try:
            filepath = documents_store[session_id].get('filepath')
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
        except:
            pass
        
        # Remove from memory store
        del documents_store[session_id]
    
    session.pop('document_info', None)
    session.modified = True
    
    return jsonify({'success': True})

@app.route('/clear-history', methods=['POST'])
def clear_history():
    """Clear chat history"""
    session['conversations'] = []
    return jsonify({'success': True})

@app.route('/get-conversations', methods=['GET'])
def get_conversations():
    """Get all conversations for sidebar update"""
    conversations = session.get('conversations', [])
    return jsonify({'conversations': conversations})


@app.route('/quick-query/<query_type>', methods=['POST'])
def quick_query(query_type):
    """Handle quick query buttons"""
    queries = {
        'format': 'Is the document properly formatted?',
        'overview': 'Is there an overview section?',
        'diagrams': 'Does the document contain diagrams or figures?',
        'summarize': 'Provide a summary of the document'
    }
    
    query = queries.get(query_type, '')
    return jsonify({'query': query})
@app.route('/delete-conversation', methods=['POST'])
def delete_conversation():
    data = request.get_json()
    
    # The fix: wrap data.get('index') in int()
    try:
        index_to_delete = int(data.get('index'))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Invalid index"}), 400

    if 'conversations' in session:
        conversations = session['conversations']
        
        # Now the comparison works because both are integers
        if 0 <= index_to_delete < len(conversations):
            conversations.pop(index_to_delete)
            session['conversations'] = conversations
            session.modified = True
            
            return jsonify({
                "success": True, 
                "all_conversations": conversations
            })
            
    return jsonify({"success": False, "error": "Conversation not found"}), 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)