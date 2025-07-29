"""
🔍 Search
=========
Text, image, and multimodal video search functionality.
"""

import streamlit as st
from typing import Optional, Dict, Any
import time

from tl_utils import get_client


st.set_page_config(page_title="Search - Video Semantic Search", page_icon="🔍")

def display_search_results(results, search_type: str):
    """Display search results in a nice format."""
    if not results or not hasattr(results, 'data') or not results.data:
        st.warning("No results found for your search.")
        return
    
    st.success(f"Found {len(results.data)} result(s)")
    
    for i, result in enumerate(results.data):
        with st.expander(f"Result {i+1} - Score: {result.score:.3f}", expanded=i<3):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Display thumbnail if available
                if hasattr(result, 'thumbnail_url') and result.thumbnail_url:
                    st.image(result.thumbnail_url, use_column_width=True)
                
                # Video metadata
                st.write(f"**Video ID:** `{result.video_id}`")
                if hasattr(result, 'start') and hasattr(result, 'end'):
                    st.write(f"**Time:** {result.start:.1f}s - {result.end:.1f}s")
                st.write(f"**Confidence:** {result.score:.3f}")
            
            with col2:
                # Display matching content
                if hasattr(result, 'text') and result.text:
                    st.write("**Matching Text:**")
                    st.write(result.text)
                
                if hasattr(result, 'metadata') and result.metadata:
                    st.write("**Metadata:**")
                    st.json(result.metadata, expanded=False)


def main():
    st.title("🔍 Video Search")
    st.markdown("Search through your video content using natural language, images, or both!")
    
    # Initialize client
    try:
        client = get_client()
    except SystemExit as e:
        st.error(str(e))
        return
    
    # Index selection
    st.subheader("Select Index")
    
    with st.spinner("Loading indexes..."):
        try:
            indexes = list(client.index.list())
            if not indexes:
                st.error("No indexes found. Please create an index first using the CLI tool.")
                return
                
            index_options = {f"{idx.name} ({idx.id})": idx.id for idx in indexes}
            selected_index_name = st.selectbox("Choose an index:", list(index_options.keys()))
            selected_index_id = index_options[selected_index_name]
            
        except Exception as e:
            st.error(f"Failed to load indexes: {e}")
            return
    
    st.markdown("---")
    
    # Search type selection
    search_type = st.radio(
        "Search Type:",
        ["Text Search", "Image Search", "Multimodal Search"],
        horizontal=True
    )
    
    # Search parameters
    search_query = None
    search_image = None
    search_options = {}
    
    if search_type in ["Text Search", "Multimodal Search"]:
        st.subheader("Text Query")
        search_query = st.text_area(
            "Enter your search query:",
            placeholder="e.g., 'person walking in the park', 'red car driving', 'sunset scene'",
            height=100
        )
    
    if search_type in ["Image Search", "Multimodal Search"]:
        st.subheader("Image Upload")
        search_image = st.file_uploader(
            "Upload an image to search for similar visual content:",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp']
        )
        
        if search_image:
            st.image(search_image, caption="Uploaded search image", use_column_width=True)
    
    # Advanced options
    with st.expander("Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            search_options['page_limit'] = st.number_input(
                "Max Results:", 
                min_value=1, 
                max_value=50, 
                value=10
            )
            
        with col2:
            search_options['threshold'] = st.slider(
                "Confidence Threshold:", 
                min_value=0.0, 
                max_value=1.0, 
                value=0.5,
                step=0.1
            )
        
        search_options['sort_option'] = st.selectbox(
            "Sort by:",
            ["score", "created_at"],
            index=0
        )
    
    # Search execution
    st.markdown("---")
    
    # Validate inputs
    can_search = False
    if search_type == "Text Search" and search_query:
        can_search = True
    elif search_type == "Image Search" and search_image:
        can_search = True
    elif search_type == "Multimodal Search" and (search_query or search_image):
        can_search = True
    
    if st.button("🔍 Search", disabled=not can_search, use_container_width=True):
        with st.spinner("Searching videos..."):
            try:
                # Prepare search parameters
                search_params = {
                    "index_id": selected_index_id,
                    "query_text": search_query if search_query else None,
                    "query_media_file": search_image if search_image else None,
                    "options": ["visual", "conversation", "text_in_video"],  # Search all modalities
                    **search_options
                }
                
                # Remove None values
                search_params = {k: v for k, v in search_params.items() if v is not None}
                
                start_time = time.time()
                results = client.search.query(**search_params)
                search_time = time.time() - start_time
                
                st.markdown("---")
                st.subheader("Search Results")
                st.info(f"Search completed in {search_time:.2f} seconds")
                
                display_search_results(results, search_type)
                
            except Exception as e:
                st.error(f"Search failed: {e}")
    
    # Tips and help
    st.markdown("---")
    st.subheader("💡 Search Tips")
    
    with st.expander("How to get better search results"):
        st.markdown("""
        **Text Search Tips:**
        - Use descriptive, natural language queries
        - Include visual details: colors, objects, actions, settings
        - Try different phrasings if you don't get good results
        
        **Image Search Tips:**
        - Use clear, high-quality images
        - Images with similar composition work best
        - Try different crops or angles of the same scene
        
        **Multimodal Search Tips:**
        - Combine text and image for more precise results
        - Use text to describe what the image shows
        - Great for finding specific scenes with particular visual elements
        """)


if __name__ == "__main__":
    main() 