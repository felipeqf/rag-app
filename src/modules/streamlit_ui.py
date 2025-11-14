import streamlit as st
import uuid
import markdown
from datetime import datetime
from src.modules.db import Database
from src.modules.rag import Rag
from src.config.logs import logger

def run_ui():
    """Main Streamlit UI function."""
    # Initialize classes
    db = Database()
    rag = Rag()
    db.init_db()

    # Page config
    st.set_page_config(page_title="RAG Chat", layout="wide")

    # Header with user info and logout
    if not st.user.is_logged_in:
        # Show login in header if not logged in
        header_col1, header_col2 = st.columns([3, 1])
        with header_col1:
            st.title("LLMs Research Assistant")
        with header_col2:
            st.markdown("<div style='padding-top: 20px;'></div>", unsafe_allow_html=True)
            if st.button("Log in with Google", use_container_width=True, type="primary"):
                st.login()
    else:
        # Show user info and logout in header when logged in
        header_col1, header_col2 = st.columns([3, 1])
        with header_col1:
            st.title("LLMs Research Assistant")
        with header_col2:
            # Anchor to target the following horizontal block
            st.markdown('<div id="user-info-anchor"></div>', unsafe_allow_html=True)
            user_cols = st.columns([1, 4, 2])
            with user_cols[0]:
                st.markdown(f"<img src='{st.user.picture}' alt='profile'/>", unsafe_allow_html=True)
            with user_cols[1]:
                st.markdown(f"<div class='user-name'>{st.user.name}</div>", unsafe_allow_html=True)
            with user_cols[2]:
                if st.button("Log out", key="logout_header", type="secondary"):
                    st.logout()

    # Initialize session state
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "pending_user_input" not in st.session_state:
        st.session_state.pending_user_input = None

    # Custom CSS for chat styling
    st.markdown("""
    <style>
        /* add border to avatar */
        .st-emotion-cache-467cry img {
            border-radius: 8px;
        }
        .st-emotion-cache-1permvm {
            align-items: center;
            margin-bottom: 10px;
        }
        .st-emotion-cache-1krtkoa {
            background-color: #333;
            border: none;
        }
        .st-emotion-cache-1krtkoa:hover{
            background-color: #333;
        }

        /* Message alignment */
        .user-message-container {
            display: flex;
            justify-content: flex-end;
            margin: 10px 0;
        }
        .user-message {
            background-color: #333;
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 70%;
            text-align: right;
            color: white;
        }
        
        /* Bot message styling */
        .bot-message-container {
            display: flex;
            justify-content: flex-start;
            margin: 10px 0;
        }
        .bot-message {
            background-color: #1e1e1e;
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 70%;
            text-align: left;
            color: white;
        }

        div[data-testid="stButton"],
        div[data-testid="stFormSubmitButton"] {
            padding-top: 1.55rem;
        }
        
        
        /* Custom scrollbar for session history */
        .session-history-container::-webkit-scrollbar {
            width: 6px;
        }
        
        .session-history-container::-webkit-scrollbar-track {
            background: transparent;
        }
        
        .session-history-container::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 3px;
        }
        
        .session-history-container::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
        
        /* Session history styling */
        .session-card-button {
            margin-bottom: 0px !important;
            gap: 0px !important;
        }
        .st-emotion-cache-tn0cau {
            gap: 2px !important;
        }

        
        /* New Conversation button styling - simple solid color */
        section[data-testid="stSidebar"] button[kind="primary"] {
            background-color: #4CAF50;
            border: none;
            font-weight: 600;
        }
        
        section[data-testid="stSidebar"] button[kind="primary"]:hover {
            background-color: #45a049;
        }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar for session history (only show when logged in)
    if st.user.is_logged_in:
        with st.sidebar:
            # New Conversation button at the top
            if st.button("➕ New Conversation", use_container_width=True, type="primary", key="new_conversation_sidebar"):
                # Save current session before creating new one
                if st.session_state.messages:
                    db.save_session(st.session_state.session_id, st.session_state.messages, st.user.sub)
                
                # Create new session
                st.session_state.session_id = str(uuid.uuid4())
                st.session_state.messages = []
                st.session_state.pending_user_input = None
                st.rerun()
            
            st.markdown("---")
            st.markdown("### 📚 Session History")
            
            # Create a scrollable container for session history
            st.markdown('<div class="session-history-container">', unsafe_allow_html=True)
            
            # Get all sessions for the current user
            user_sessions = db.get_user_sessions(st.user.sub)
            
            if user_sessions:
                for idx, session in enumerate(user_sessions):
                    # Get the first user message for preview
                    first_message = ""
                    for msg in session["messages"]:
                        if msg["role"] == "user":
                            first_message = msg["content"]
                            break
                    
                    # Truncate preview to fit inline with date
                    preview = first_message[:24] + ".." if len(first_message) > 24 else first_message
                    if not preview:
                        preview = "Empty session"
                    
                    # Format the date (just month and day)
                    try:
                        dt = datetime.fromisoformat(session["dt_created"])
                        date_str = dt.strftime("%b %d")
                    except:
                        date_str = session["dt_created"]
                    
                    # Create button label with title and date inline, separated by spaces
                    # Use em space (wider space) to separate them visually
                    button_label = f"{preview}"
                    
                    st.markdown('<div class="session-card-button">', unsafe_allow_html=True)
                    session_clicked = st.button(
                        button_label,
                        key=f"load_{session['session_id']}",
                        use_container_width=True,
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    if session_clicked:
                        # Save current session before switching
                        if st.session_state.messages:
                            db.save_session(
                                st.session_state.session_id, 
                                st.session_state.messages, 
                                st.user.sub
                            )
                        
                        # Load the selected session
                        st.session_state.session_id = session["session_id"]
                        st.session_state.messages = session["messages"]
                        st.session_state.pending_user_input = None
                        st.rerun()
            else:
                st.info("No previous sessions found. Start chatting to create your first session!")
            
            st.markdown('</div>', unsafe_allow_html=True)

    # Chat container with border (reduced height to fit on one screen)
    chat_container = st.container(border=True, height=480)

    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                    <div class="user-message-container">
                        <div class="user-message">
                            {message["content"]}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                # Convert markdown to HTML for bot messages
                content_html = markdown.markdown(message["content"], extensions=['nl2br'])
                st.markdown(f"""
                    <div class="bot-message-container">
                        <div class="bot-message">
                            {content_html}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # Message input and send button (using form to enable Enter key submission)
    with st.form(key="message_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input("message", label_visibility="visible", placeholder="Type your message here...", key="user_input")
        with col2:
            send_button = st.form_submit_button("send", use_container_width=True, type="primary")

    # Process pending bot response first (if any)
    if st.session_state.pending_user_input:
        # Stream bot response
        with chat_container:
            # Create a placeholder for the streaming response
            message_placeholder = st.empty()
            full_response = ""
            
            # Stream the response and update the placeholder
            for chunk in rag.get_response(st.session_state.pending_user_input, st.session_state.session_id):
                full_response += chunk
                # Convert markdown to HTML for consistent rendering
                content_html = markdown.markdown(full_response, extensions=['nl2br'])
                # Update the placeholder with the accumulated response in styled container
                message_placeholder.markdown(f"""
                    <div class="bot-message-container">
                        <div class="bot-message">
                            {content_html}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        # Add bot message to history
        st.session_state.messages.append({"role": "bot", "content": full_response})
        
        # Save session to database with user_id if logged in
        user_id = st.user.sub if st.user.is_logged_in else None
        db.save_session(st.session_state.session_id, st.session_state.messages, user_id)
        
        # Clear pending input
        st.session_state.pending_user_input = None
        
        # Rerun to show bot response in chat history
        st.rerun()

    # Handle send button (triggered by button click or Enter key)
    if send_button and user_input:
        # Add user message immediately
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Store the input for bot processing on next run
        st.session_state.pending_user_input = user_input
        
        # Rerun to show user message (form will clear input automatically)
        st.rerun()

