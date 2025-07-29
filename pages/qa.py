"""
💬 Q&A Chat
===========
Ask questions about video content using conversational AI.
"""

import streamlit as st
from typing import Dict, Any, List
import time

from tl_utils import get_client


st.set_page_config(page_title="Q&A - Video Semantic Search", page_icon="💬")


def initialize_chat_history():
    """Initialize chat history in session state."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "selected_video_id" not in st.session_state:
        st.session_state.selected_video_id = None


def display_chat_message(role: str, content: str, timestamp: str = None):
    """Display a chat message with proper styling."""
    if role == "user":
        with st.chat_message("user"):
            st.write(content)
    else:
        with st.chat_message("assistant"):
            st.write(content)
            if timestamp:
                st.caption(f"Response time: {timestamp}")


def ask_question(client, video_id: str, question: str, context_history: List[Dict] = None) -> str:
    """
    Ask a question about the video content.
    
    Args:
        client: TwelveLabs client
        video_id: ID of the video to ask about
        question: The question to ask
        context_history: Previous conversation context
        
    Returns:
        str: The answer from the AI
    """
    try:
        # Prepare the query parameters
        query_params = {
            "video_id": video_id,
            "question": question
        }
        
        # Add conversation context if available
        if context_history:
            # Include recent context (last 5 exchanges)
            recent_context = context_history[-10:]  # Last 5 Q&A pairs
            context_text = "\n".join([
                f"Q: {item['question']}\nA: {item['answer']}" 
                for item in recent_context if 'question' in item and 'answer' in item
            ])
            if context_text:
                query_params["prompt"] = f"Previous conversation context:\n{context_text}\n\nCurrent question: {question}"
        
        # Make the API call
        start_time = time.time()
        result = client.analyze.open_ended(**query_params)
        response_time = time.time() - start_time
        
        # Extract the answer from the result
        if hasattr(result, 'answer'):
            answer = result.answer
        elif hasattr(result, 'data') and result.data:
            if isinstance(result.data, list) and len(result.data) > 0:
                answer = str(result.data[0])
            else:
                answer = str(result.data)
        else:
            answer = str(result)
        
        return answer, response_time
        
    except Exception as e:
        raise Exception(f"Failed to get answer: {e}")


def main():
    st.title("💬 Q&A Chat")
    st.markdown("Ask questions about your video content and get intelligent, context-aware answers!")
    
    initialize_chat_history()
    
    # Initialize client
    try:
        client = get_client()
    except SystemExit as e:
        st.error(str(e))
        return
    
    # Sidebar for video selection
    with st.sidebar:
        st.subheader("🎬 Select Video")
        
        # Index selection
        try:
            indexes = list(client.index.list())
            if not indexes:
                st.error("No indexes found.")
                return
                
            index_options = {f"{idx.name} ({idx.id})": idx.id for idx in indexes}
            selected_index_name = st.selectbox("Index:", list(index_options.keys()))
            selected_index_id = index_options[selected_index_name]
            
        except Exception as e:
            st.error(f"Failed to load indexes: {e}")
            return
        
        # Video selection
        try:
            videos = list(client.index.video.list(index_id=selected_index_id, page_limit=50))
            if not videos:
                st.warning("No videos found.")
                return
                
            video_options = {}
            for video in videos:
                filename = video.system_metadata.filename if hasattr(video, 'system_metadata') else video.id
                duration_info = ""
                if hasattr(video, 'metadata') and video.metadata and hasattr(video.metadata, 'duration'):
                    minutes = int(video.metadata.duration // 60)
                    seconds = int(video.metadata.duration % 60)
                    duration_info = f" ({minutes}:{seconds:02d})"
                
                video_options[f"{filename}{duration_info}"] = video.id
            
            selected_video_name = st.selectbox("Video:", list(video_options.keys()))
            current_video_id = video_options[selected_video_name]
            
            # Clear chat history if video changed
            if current_video_id != st.session_state.selected_video_id:
                st.session_state.chat_history = []
                st.session_state.selected_video_id = current_video_id
            
        except Exception as e:
            st.error(f"Failed to load videos: {e}")
            return
        
        # Chat controls
        st.markdown("---")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
        
        # Chat history export
        if st.session_state.chat_history:
            chat_export = "\n\n".join([
                f"Q: {item.get('question', '')}\nA: {item.get('answer', '')}"
                for item in st.session_state.chat_history
            ])
            st.download_button(
                "💾 Export Chat",
                data=chat_export,
                file_name=f"chat_{selected_video_name.split(' (')[0]}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    # Main chat interface
    st.subheader(f"Chat about: {selected_video_name}")
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for item in st.session_state.chat_history:
            display_chat_message("user", item["question"])
            display_chat_message("assistant", item["answer"], item.get("response_time"))
    
    # Question input
    st.markdown("---")
    
    # Suggested questions
    if not st.session_state.chat_history:
        st.subheader("💡 Suggested Questions")
        suggested_questions = [
            "What is this video about?",
            "Who are the main people in this video?",
            "What are the key topics discussed?",
            "Can you summarize the main points?",
            "What happens at the beginning/middle/end?",
            "Are there any important quotes or statements?",
            "What products or brands are mentioned?",
            "What is the overall tone or mood?"
        ]
        
        cols = st.columns(2)
        for i, question in enumerate(suggested_questions):
            with cols[i % 2]:
                if st.button(question, key=f"suggested_{i}", use_container_width=True):
                    st.session_state.current_question = question
    
    # Question input form
    with st.form("question_form", clear_on_submit=True):
        question = st.text_area(
            "Ask a question about the video:",
            placeholder="e.g., 'What products are mentioned in this video?', 'Who is speaking at 2:30?', 'What are the main takeaways?'",
            height=100,
            value=st.session_state.get("current_question", "")
        )
        
        submitted = st.form_submit_button("💬 Ask Question", use_container_width=True)
        
        if submitted and question.strip():
            # Clear any suggested question from session state
            if "current_question" in st.session_state:
                del st.session_state.current_question
            
            with st.spinner("Thinking..."):
                try:
                    answer, response_time = ask_question(
                        client, 
                        current_video_id, 
                        question, 
                        st.session_state.chat_history
                    )
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": answer,
                        "response_time": f"{response_time:.1f}s",
                        "timestamp": time.time()
                    })
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Failed to get answer: {e}")
    
    # Tips and examples
    if not st.session_state.chat_history:
        st.markdown("---")
        st.subheader("💡 Q&A Tips")
        
        with st.expander("How to ask better questions"):
            st.markdown("""
            **Effective Question Types:**
            - **Content Questions**: "What is this video about?", "What topics are covered?"
            - **People Questions**: "Who appears in this video?", "Who is the speaker?"
            - **Time-based Questions**: "What happens at 2:30?", "How does the video end?"
            - **Analysis Questions**: "What is the main argument?", "What evidence is presented?"
            - **Detail Questions**: "What products are mentioned?", "What locations are shown?"
            
            **Best Practices:**
            - Be specific in your questions for better answers
            - Ask follow-up questions to dive deeper
            - Reference specific parts of the video when relevant
            - The AI remembers previous questions in your conversation
            
            **Example Questions:**
            - "Can you identify all the people who speak in this video?"
            - "What are the key features of the product being demonstrated?"
            - "What questions does the audience ask during the Q&A session?"
            - "What technical specifications are mentioned?"
            """)


if __name__ == "__main__":
    main() 