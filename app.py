#!/usr/bin/env python3
"""
Video Semantic Search - Single File Multi-Page App
"""

import streamlit as st
from typing import Optional, Dict, Any, List
import time

from tl_utils import get_client

# Configure page
st.set_page_config(
    page_title="Video Semantic Search",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for brand colors
st.markdown("""
<style>
    /* Primary button styling */
    .stButton > button[kind="primary"] {
        background-color: #557efb !important;
        border-color: #557efb !important;
        color: white !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #456eeb !important;
        border-color: #456eeb !important;
        color: white !important;
    }
    
    .stButton > button[kind="primary"]:active {
        background-color: #355edb !important;
        border-color: #355edb !important;
        color: white !important;
    }
    
    /* Secondary button styling */
    .stButton > button[kind="secondary"] {
        background-color: transparent !important;
        border-color: #557efb !important;
        color: #557efb !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #557efb !important;
        border-color: #557efb !important;
        color: white !important;
    }
    
    /* Selectbox and other interactive elements */
    .stSelectbox > div > div > div {
        border-color: #557efb !important;
    }
    
    /* Radio button styling */
    .stRadio > div {
        color: #557efb !important;
    }
    
    /* File uploader */
    .stFileUploader > div > div {
        border-color: #557efb !important;
    }
    
    /* Progress bars and spinners */
    .stProgress > div > div {
        background-color: #557efb !important;
    }
    
    /* Success/info messages accent */
    .stSuccess {
        border-left-color: #557efb !important;
    }
    
    .stInfo {
        border-left-color: #557efb !important;
    }
</style>
""", unsafe_allow_html=True)


def index_selection_page():
    """Show only index selection when no index is selected"""
    # Logo header
    
    col1, col2, col3 = st.columns(3)
    with col2:
        st.markdown(f"""<div style="text-align: center; margin-bottom: 0px;"><a href="http://localhost:8501/"><img src="https://raw.githubusercontent.com/erickfm/assets/main/images/snip.png" style="padding-right: 10px;" width="100%" height="10%"></a></div>""", unsafe_allow_html=True)
        try:
            client = get_client()
            indexes = list(client.index.list())
            
            if not indexes:
                st.error("No indexes found. Please create an index first using the CLI.")
                st.subheader("🚀 Quick Start")
                st.code("""
# Create your first index
python indexing.py create-index "My Videos" --engines marengo2.6

# Upload videos
python indexing.py upload-video <index_id> path/to/video.mp4
                """, language="bash")
                return
            
            # Create index options
            index_options = {f"{idx.name} ({idx.id})": idx.id for idx in indexes}
            
            # Show index selection
            selected_index_display = st.selectbox(
                "",
                list(index_options.keys()),
            )
            
            if st.button("📂 Use This Index", use_container_width=True, type="primary"):
                selected_index_id = index_options[selected_index_display]
                st.query_params["index_id"] = selected_index_id
                st.rerun()
            
            # Show index details
            if selected_index_display:
                selected_id = index_options[selected_index_display]
                st.markdown("---")
                
                try:
                    videos = list(client.index.video.list(index_id=selected_id, page_limit=5))
                    if videos:
                        st.success(f"✅ Found {len(videos)} video(s) in this index")
                        for i, video in enumerate(videos[:3], 1):
                            filename = video.system_metadata.filename if hasattr(video, 'system_metadata') else video.id
                            st.write(f"{i}. {filename}")
                        if len(videos) > 3:
                            st.write(f"... and {len(videos) - 3} more")
                    else:
                        st.warning("⚠️ This index is empty. Upload videos first:")
                        st.code(f"python indexing.py upload-video {selected_id} path/to/video.mp4")
                except Exception as e:
                    st.error(f"Error loading videos: {e}")
            
        except Exception as e:
            st.error(f"Failed to load indexes: {e}")


def get_current_index():
    """Get the current index from query params (assumes it exists)"""
    index_id = st.query_params.get("index_id")
    
    try:
        client = get_client()
        indexes = list(client.index.list())
        
        # Find the index name for the current ID
        for idx in indexes:
            if idx.id == index_id:
                return index_id, idx.name
        
        # Index not found, clear query params
        st.query_params.clear()
        st.rerun()
        
    except Exception as e:
        st.error(f"Failed to validate index: {e}")
        st.query_params.clear()
        st.rerun()


def search_page(index_id: str, index_name: str):
    """Search page functionality"""
    st.title("🔍 Video Search")
    st.markdown("Search through your video content using natural language, images, or both!")
    
    # Initialize client
    try:
        client = get_client()
    except SystemExit as e:
        st.error(str(e))
        return
    
    st.info(f"Searching in index: **{index_name}**")
    
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
            st.image(search_image, caption="Uploaded search image", use_container_width=True)
    
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
            search_options['threshold'] = st.selectbox(
                "Confidence Threshold:", 
                options=["none", "low", "medium", "high"],
                index=2  # Default to "medium"
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
                    "index_id": index_id,
                    "query_text": search_query if search_query else None,
                    "query_media_file": search_image if search_image else None,
                    "options": ["visual", "audio"],  # Fixed: Only valid options are "visual" and "audio"
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
                
                # Display results
                if not results or not hasattr(results, 'data') or not results.data:
                    st.warning("No results found for your search.")
                else:
                    st.success(f"Found {len(results.data)} result(s)")
                    
                    for i, result in enumerate(results.data):
                        with st.expander(f"Result {i+1} - Score: {result.score:.3f}", expanded=i<3):
                            col1, col2 = st.columns([1, 2])
                            
                            with col1:
                                if hasattr(result, 'thumbnail_url') and result.thumbnail_url:
                                    st.image(result.thumbnail_url, use_container_width=True)
                                
                                st.write(f"**Video ID:** `{result.video_id}`")
                                if hasattr(result, 'start') and hasattr(result, 'end'):
                                    st.write(f"**Time:** {result.start:.1f}s - {result.end:.1f}s")
                                st.write(f"**Confidence:** {result.score:.3f}")
                            
                            with col2:
                                if hasattr(result, 'text') and result.text:
                                    st.write("**Matching Text:**")
                                    st.write(result.text)
                
            except Exception as e:
                st.error(f"Search failed: {e}")


def summary_page(index_id: str, index_name: str):
    """Summary page with two-state flow: thumbnail grid or video-specific view"""
    
    st.header("📝 Video Summary")
    st.info(f"Generating summaries for videos in index: **{index_name}**")
    
    # Initialize client
    try:
        client = get_client()
    except SystemExit as e:
        st.error(str(e))
        return
    

    # Check if a specific video is selected via query params
    selected_video_id = st.query_params.get("video_id")
    
    # Load videos
    with st.spinner("Loading videos..."):
        try:
            videos = list(client.index.video.list(index_id=index_id, page_limit=50))
            if not videos:
                st.warning("No videos found in this index. Upload some videos first.")
                st.code(f"python indexing.py upload-video {index_id} path/to/video.mp4")
                return
        except Exception as e:
            st.error(f"Failed to load videos: {e}")
            return
    
    # State 1: No video selected - Show thumbnail grid
    if not selected_video_id:
        # Summary options (moved to top)
        with st.expander("📋 Summary Options", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                summary_type = st.selectbox(
                    "Summary Type:",
                    ["summary", "chapter", "highlight"],
                    index=0,
                    key="summary_type_global"
                )
            
            with col2:
                custom_prompt = st.text_input(
                    "Custom Instructions (optional):",
                    placeholder="e.g., 'Focus on technical details'",
                    key="custom_prompt_global"
                )
        
        st.markdown("---")
        
        # Display videos in a grid
        st.subheader(f"📺 Select a Video to Summarize ({len(videos)})")
        
        # Create grid layout (3 columns)
        cols_per_row = 3
        for i in range(0, len(videos), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, col in enumerate(cols):
                video_idx = i + j
                if video_idx < len(videos):
                    video = videos[video_idx]
                    
                    with col:
                        # Get video info
                        filename = video.system_metadata.filename if hasattr(video, 'system_metadata') else video.id
                        duration = None
                        if hasattr(video, 'metadata') and video.metadata and hasattr(video.metadata, 'duration'):
                            duration = video.metadata.duration
                            minutes = int(duration // 60)
                            seconds = int(duration % 60)
                            duration_str = f"{minutes}:{seconds:02d}"
                        else:
                            duration_str = "Unknown"
                        
                        # Video thumbnail container (clickable)
                        with st.container():
                            # Try to display thumbnail using the standard TwelveLabs attribute
                            thumbnail_displayed = False
                            
                            # Based on official TwelveLabs docs, thumbnails should be available as 'thumbnail_url'
                            if hasattr(video, 'thumbnail_url') and video.thumbnail_url:
                                try:
                                    st.image(video.thumbnail_url, use_container_width=True)
                                    thumbnail_displayed = True
                                except Exception:
                                    pass  # Fall through to the fallback
                            
                            # Fallback if no thumbnail available yet
                            if not thumbnail_displayed:
                                st.markdown(
                                    f"""
                                    <div style='
                                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                        height: 120px;
                                        border-radius: 8px;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        color: white;
                                        font-size: 24px;
                                        margin-bottom: 8px;
                                    '>
                                        🎬
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                            
                            # Video details
                            st.markdown(f"**{filename}**")
                            st.caption(f"⏱️ {duration_str} | 🆔 {video.id[:8]}...")
                            
                            # Select button that sets query param
                            button_key = f"select_summary_{video.id}"
                            if st.button("📝 Summarize This Video", key=button_key, use_container_width=True):
                                st.query_params.video_id = video.id
                                st.rerun()
    
    else:
        # State 2: Video selected - Show video player and summary interface
        # Find the selected video
        selected_video = None
        for video in videos:
            if video.id == selected_video_id:
                selected_video = video
                break
        
        if not selected_video:
            st.error("Selected video not found. Returning to video list.")
            if st.button("← Back to Video List"):
                del st.query_params.video_id
                st.rerun()
            return
        
        # Get video info
        filename = selected_video.system_metadata.filename if hasattr(selected_video, 'system_metadata') else selected_video.id
        
        # Back button
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("← Back to Videos"):
                del st.query_params.video_id
                st.rerun()
        
        # Video player and info
        st.subheader(f"📹 {filename}")
        
        # Try to display video if URL is available
        if hasattr(selected_video, 'video_url') and selected_video.video_url:
            try:
                st.video(selected_video.video_url)
            except:
                st.info("Video player not available. Showing summary interface only.")
        elif hasattr(selected_video, 'url') and selected_video.url:
            try:
                st.video(selected_video.url)
            except:
                st.info("Video player not available. Showing summary interface only.")
        else:
            # Show thumbnail instead
            if hasattr(selected_video, 'thumbnail_url') and selected_video.thumbnail_url:
                st.image(selected_video.thumbnail_url, width=400)
            else:
                st.info("Video preview not available.")
        
        # Video metadata
        if hasattr(selected_video, 'metadata') and selected_video.metadata:
            duration = getattr(selected_video.metadata, 'duration', None)
            if duration:
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                st.caption(f"⏱️ Duration: {minutes}:{seconds:02d}")
        
        st.caption(f"🆔 Video ID: {selected_video.id}")
        
        st.markdown("---")
        
        # Summary options
        with st.expander("📋 Summary Options", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                summary_type = st.selectbox(
                    "Summary Type:",
                    ["summary", "chapter", "highlight"],
                    index=0,
                    key="summary_type_video"
                )
            
            with col2:
                custom_prompt = st.text_input(
                    "Custom Instructions (optional):",
                    placeholder="e.g., 'Focus on technical details'",
                    key="custom_prompt_video"
                )
        
        # Generate summary button
        if st.button("🚀 Generate Summary", use_container_width=True, type="primary"):
            generate_summary(client, selected_video, filename, summary_type, custom_prompt)


def generate_summary(client, video, filename, summary_type, custom_prompt):
    """Generate and display summary for a specific video"""
    
    with st.spinner(f"Analyzing '{filename}' and generating summary..."):
        try:
            summary_params = {
                "video_id": video.id,
                "type": summary_type
            }
            
            if custom_prompt.strip():
                summary_params["prompt"] = custom_prompt
            
            start_time = time.time()
            # Build summarize parameters
            summarize_kwargs = {
                "video_id": summary_params["video_id"],
                "type": summary_params.get("type", "summary")
            }
            
            # Add prompt if provided
            if "prompt" in summary_params:
                summarize_kwargs["prompt"] = summary_params["prompt"]
            
            summary_result = client.summarize(**summarize_kwargs)
            analysis_time = time.time() - start_time
            
            # Create a modal-like display for the summary
            st.markdown("---")
            st.success(f"Summary generated in {analysis_time:.1f} seconds!")
            
            # Video info header
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(f"📄 Summary: {filename}")
            with col2:
                summary_text = ""
                if hasattr(summary_result, 'summary') and summary_result.summary:
                    summary_text = summary_result.summary
                elif hasattr(summary_result, 'data') and summary_result.data:
                    summary_text = str(summary_result.data)
                else:
                    summary_text = str(summary_result)
                
                if summary_text:
                    st.download_button(
                        "💾 Download",
                        data=summary_text,
                        file_name=f"summary_{filename}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            
            # Display summary content
            with st.container():
                if hasattr(summary_result, 'summary') and summary_result.summary:
                    st.write(summary_result.summary)
                elif hasattr(summary_result, 'data') and summary_result.data:
                    st.write(str(summary_result.data))
                else:
                    st.write(str(summary_result))
            
            st.markdown("---")
            
        except Exception as e:
            st.error(f"Failed to generate summary: {e}")
            st.info("Please check that the video has been fully processed and try again.")


def qa_page(index_id: str, index_name: str):
    """Q&A page with two-state flow: thumbnail grid or video-specific chat"""
    
    st.header("💬 Video Q&A Chat")
    st.info(f"Ask questions about videos in index: **{index_name}**")
    
    # Initialize client
    try:
        client = get_client()
    except SystemExit as e:
        st.error(str(e))
        return
    
    # Check if a specific video is selected via query params
    selected_video_id = st.query_params.get("video_id")
    
    # Session state keys for chat history
    chat_history_key = f"chat_history_{index_id}_{selected_video_id}" if selected_video_id else None
    
    # Load videos
    with st.spinner("Loading videos..."):
        try:
            videos = list(client.index.video.list(index_id=index_id, page_limit=50))
            if not videos:
                st.warning("No videos found in this index. Upload some videos first.")
                st.code(f"python indexing.py upload-video {index_id} path/to/video.mp4")
                return
        except Exception as e:
            st.error(f"Failed to load videos: {e}")
            return
    
    # State 1: No video selected - Show thumbnail grid
    if not selected_video_id:
        # Display videos in a grid
        st.subheader(f"📺 Select a Video to Chat With ({len(videos)})")
        
        # Create grid layout (3 columns)
        cols_per_row = 3
        for i in range(0, len(videos), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, col in enumerate(cols):
                video_idx = i + j
                if video_idx < len(videos):
                    video = videos[video_idx]
                    
                    with col:
                        # Get video info
                        filename = video.system_metadata.filename if hasattr(video, 'system_metadata') else video.id
                        duration = None
                        if hasattr(video, 'metadata') and video.metadata and hasattr(video.metadata, 'duration'):
                            duration = video.metadata.duration
                            minutes = int(duration // 60)
                            seconds = int(duration % 60)
                            duration_str = f"{minutes}:{seconds:02d}"
                        else:
                            duration_str = "Unknown"
                        
                        # Video thumbnail container (clickable)
                        with st.container():
                            # Try to display thumbnail using the standard TwelveLabs attribute
                            thumbnail_displayed = False
                            
                            # Based on official TwelveLabs docs, thumbnails should be available as 'thumbnail_url'
                            if hasattr(video, 'thumbnail_url') and video.thumbnail_url:
                                try:
                                    st.image(video.thumbnail_url, use_container_width=True)
                                    thumbnail_displayed = True
                                except Exception:
                                    pass  # Fall through to the fallback
                            
                            # Fallback if no thumbnail available yet
                            if not thumbnail_displayed:
                                st.markdown(
                                    f"""
                                    <div style='
                                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                        height: 120px;
                                        border-radius: 8px;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        color: white;
                                        font-size: 24px;
                                        margin-bottom: 8px;
                                    '>
                                        🎬
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                            
                            # Video details
                            st.markdown(f"**{filename}**")
                            st.caption(f"⏱️ {duration_str} | 🆔 {video.id[:8]}...")
                            
                            # Select button that sets query param
                            button_key = f"select_qa_{video.id}"
                            if st.button("💬 Chat About This Video", key=button_key, use_container_width=True):
                                st.query_params.video_id = video.id
                                st.rerun()
    
    else:
        # State 2: Video selected - Show video player and Q&A interface
        # Find the selected video
        selected_video = None
        for video in videos:
            if video.id == selected_video_id:
                selected_video = video
                break
        
        if not selected_video:
            st.error("Selected video not found. Returning to video list.")
            if st.button("← Back to Video List"):
                del st.query_params.video_id
                st.rerun()
            return
        
        # Initialize chat history for this video
        if chat_history_key not in st.session_state:
            st.session_state[chat_history_key] = []
        
        # Get video info
        filename = selected_video.system_metadata.filename if hasattr(selected_video, 'system_metadata') else selected_video.id
        
        # Back button
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("← Back to Videos"):
                del st.query_params.video_id
                st.rerun()
        
        # Video player and info
        st.subheader(f"💬 Chat with: {filename}")
        
        # Video player section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Try to display video if URL is available
            if hasattr(selected_video, 'video_url') and selected_video.video_url:
                try:
                    st.video(selected_video.video_url)
                except:
                    st.info("Video player not available.")
            elif hasattr(selected_video, 'url') and selected_video.url:
                try:
                    st.video(selected_video.url)
                except:
                    st.info("Video player not available.")
            else:
                # Show thumbnail instead
                if hasattr(selected_video, 'thumbnail_url') and selected_video.thumbnail_url:
                    st.image(selected_video.thumbnail_url, width=400)
                else:
                    st.info("Video preview not available.")
        
        with col2:
            # Video metadata
            st.markdown("**Video Info:**")
            if hasattr(selected_video, 'metadata') and selected_video.metadata:
                duration = getattr(selected_video.metadata, 'duration', None)
                if duration:
                    minutes = int(duration // 60)
                    seconds = int(duration % 60)
                    st.write(f"⏱️ Duration: {minutes}:{seconds:02d}")
            
            st.write(f"🆔 ID: {selected_video.id[:12]}...")
            
            # Clear chat button
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                st.session_state[chat_history_key] = []
                st.rerun()
        
        st.markdown("---")
        
        # Chat interface
        st.subheader("💭 Ask Questions")
        
        # Display chat history
        for item in st.session_state[chat_history_key]:
            with st.chat_message("user"):
                st.write(item["question"])
            with st.chat_message("assistant"):
                st.write(item["answer"])
                st.caption(f"⏱️ {item.get('response_time', 'N/A')}")
        
        # Question input
        with st.form("question_form", clear_on_submit=True):
            question = st.text_area(
                "Ask a question about the video:",
                placeholder="e.g., 'What is this video about?', 'Who are the speakers?', 'What happens at 2:30?'",
                height=100
            )
            
            submitted = st.form_submit_button("💬 Ask Question", use_container_width=True)
            
            if submitted and question.strip():
                with st.spinner("Analyzing video and generating answer..."):
                    try:
                        start_time = time.time()
                        result = client.analyze(
                            video_id=selected_video.id,
                            prompt=question
                        )
                        response_time = time.time() - start_time
                        
                        # Extract answer
                        if hasattr(result, 'answer'):
                            answer = result.answer
                        elif hasattr(result, 'data') and result.data:
                            answer = str(result.data)
                        else:
                            answer = str(result)
                        
                        # Add to chat history
                        st.session_state[chat_history_key].append({
                            "question": question,
                            "answer": answer,
                            "response_time": f"{response_time:.1f}s"
                        })
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Failed to get answer: {e}")
        
        # Suggested questions
        if len(st.session_state[chat_history_key]) == 0:
            st.markdown("**💡 Suggested questions:**")
            suggested_questions = [
                "What is this video about?",
                "Who are the main speakers or people in this video?",
                "What are the key topics discussed?",
                "Summarize the main points",
                "What happens in the first minute?"
            ]
            
            cols = st.columns(2)
            for i, suggestion in enumerate(suggested_questions):
                col = cols[i % 2]
                with col:
                    if st.button(f"💭 {suggestion}", key=f"suggestion_{i}", use_container_width=True):
                        # Add suggested question to form (this is a simple way to demonstrate)
                        st.info(f"Try asking: '{suggestion}'")


def full_app_with_sidebar(index_id: str, index_name: str):
    """Full app with sidebar when index is selected"""
    
    # Sidebar with logo
    st.sidebar.markdown(f"""<div style="text-align: center; margin-bottom: 15px;"><a href="http://localhost:8501/"><img src="https://raw.githubusercontent.com/erickfm/assets/main/images/snip.png" style="padding-right: 10px;" width="100%" height="60%"></a></div>""", unsafe_allow_html=True)
    
    # Get current page from query params
    current_page = st.query_params.get("page", "search")
    
    # Page navigation buttons
    
    # Search button
    if st.sidebar.button("🔍 Search", use_container_width=True, type="primary" if current_page == "search" else "secondary"):
        st.query_params["page"] = "search"
        st.rerun()
    
    # Summary button  
    if st.sidebar.button("📝 Summary", use_container_width=True, type="primary" if current_page == "summary" else "secondary"):
        st.query_params["page"] = "summary"
        st.rerun()
    
    # Q&A button
    if st.sidebar.button("💬 Q&A", use_container_width=True, type="primary" if current_page == "qa" else "secondary"):
        st.query_params["page"] = "qa"
        st.rerun()
    
    # Route to appropriate page based on query params
    if current_page == "search":
        search_page(index_id, index_name)
    elif current_page == "summary":
        summary_page(index_id, index_name)
    elif current_page == "qa":
        qa_page(index_id, index_name)
    else:
        # Default to search if invalid page
        st.query_params["page"] = "search"
        st.rerun()


def main():
    """Main application router"""
    
    # Check if index is selected via query params
    index_id = st.query_params.get("index_id")
    
    if not index_id:
        # No index selected - show index selection page
        index_selection_page()
    else:
        # Index selected - show full app
        result = get_current_index()
        if result:
            index_id, index_name = result
            full_app_with_sidebar(index_id, index_name)
        else:
            # Invalid index, fall back to selection
            index_selection_page()


if __name__ == "__main__":
    main() 