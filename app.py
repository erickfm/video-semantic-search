#!/usr/bin/env python3
"""
app.py
======
Main Streamlit application entry point.
Sets up sidebar navigation and routes to different pages.
"""

import streamlit as st

# Configure page
st.set_page_config(
    page_title="Video Semantic Search",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point."""
    
    # Sidebar navigation
    st.sidebar.title("🎬 Video Semantic Search")
    st.sidebar.markdown("---")
    
    # Navigation menu
    page = st.sidebar.selectbox(
        "Choose a feature:",
        [
            "🔍 Search Videos",
            "📝 Video Summary", 
            "💬 Q&A Chat"
        ]
    )
    
    # About section in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    **About this app:**
    
    This application provides semantic search capabilities for videos using TwelveLabs AI.
    
    **Features:**
    - 🔍 Text, image, and multimodal search
    - 📝 One-click video summarization
    - 💬 Ask questions about video content
    """)
    
    # Main content area
    st.title("Video Semantic Search")
    
    # Route to appropriate page based on selection
    if page == "🔍 Search Videos":
        st.info("Navigate to the Search page using the page selector above, or click the link in the sidebar.")
        st.markdown("""
        ### Search Features:
        - **Text Search**: Find videos using natural language queries
        - **Image Search**: Upload an image to find similar visual content
        - **Multimodal Search**: Combine text and image search for precise results
        """)
        
    elif page == "📝 Video Summary":
        st.info("Navigate to the Summary page using the page selector above, or click the link in the sidebar.")
        st.markdown("""
        ### Summary Features:
        - **Quick Summaries**: Get instant overviews of video content
        - **Customizable Length**: Choose summary detail level
        - **Key Insights**: Extract main points and themes
        """)
        
    elif page == "💬 Q&A Chat":
        st.info("Navigate to the Q&A page using the page selector above, or click the link in the sidebar.")
        st.markdown("""
        ### Q&A Features:
        - **Interactive Chat**: Ask questions about video content
        - **Context-Aware**: Responses based on actual video content
        - **Follow-up Questions**: Continue conversations naturally
        """)

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            Powered by TwelveLabs AI | Built with Streamlit
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main() 