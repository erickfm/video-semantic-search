#!/usr/bin/env python3
"""
Video Semantic Search - Single File Multi-Page App
"""

from pydoc import visiblename
import streamlit as st
from typing import Optional, Dict, Any, List
import time

from tl_utils import get_client

# Configure page
st.set_page_config(
    page_title="Snippetropolis",
    page_icon="https://raw.githubusercontent.com/erickfm/assets/main/images/snip_logo.png",
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
                st.subheader("Quick Start")
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
            
            if st.button("Use This Index", use_container_width=True, type="primary"):
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
                        st.success(f"Found {len(videos)} video(s) in this index")
                        for i, video in enumerate(videos[:3], 1):
                            filename = video.system_metadata.filename[:-4] if hasattr(video, 'system_metadata') else video.id
                            if len(filename) > 50:
                                filename = filename[:50] + '...'
                            st.write(f"{i}. {filename}")
                        if len(videos) > 3:
                            st.write(f"... and {len(videos) - 3} more")
                    else:
                        st.warning("This index is empty. Upload videos first:")
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
    st.title("Search")
    # st.markdown("Search through your video content using natural language, images, or both!")
    # st.info(f"Search through videos in index: **{index_name}**")

    # Initialize client
    try:
        client = get_client()
    except SystemExit as e:
        st.error(str(e))
        return
        
    # Search type selection
    search_type = st.pills(
        "",
        ["Text Search", "Image Search", "Multimodal Search"],
        default="Text Search",
        label_visibility='collapsed'
    )
    
    # Search parameters
    search_query = None
    search_image = None
    search_options = {'page_limit': 10, 'threshold': 'none'}
    
    if search_type in ["Text Search", "Multimodal Search"]:

        search_query = st.text_area(
            "Enter your search query:",
            placeholder="e.g., 'person walking in the park', 'red car driving', 'sunset scene'",
            height=100
        )
    
    if search_type in ["Image Search", "Multimodal Search"]:
        search_image = st.file_uploader(
            "Upload an image to search for similar visual content:",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp']
        )
        
        if search_image:
            st.image(search_image, caption="Uploaded search image", use_container_width=False)
    
    
    # Validate inputs
    can_search = False
    if search_type == "Text Search" and search_query:
        can_search = True
    elif search_type == "Image Search" and search_image:
        can_search = True
    elif search_type == "Multimodal Search" and (search_query or search_image):
        can_search = True
    
    if st.button("Search", disabled=not can_search, use_container_width=True):
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
                
                # Add query_media_type for image and multimodal searches
                if search_type in ["Image Search", "Multimodal Search"] and search_image:
                    search_params["query_media_type"] = "image"
                
                # Remove None values
                search_params = {k: v for k, v in search_params.items() if v is not None}
                
                start_time = time.time()
                results = client.search.query(**search_params)
                search_time = time.time() - start_time
                
                st.markdown("---")
                
                # Display results
                if not results or not hasattr(results, 'data') or not results.data:
                    st.warning("No results found for your search.")
                else:
                    for i, result in enumerate(results.data):
                        with st.expander(f"Result {i+1} - Score: {result.score:.3f}", expanded=i<3):
                            # Retrieve full video object to get video URL
                            try:
                                video = client.index.video.retrieve(index_id=index_id, id=result.video_id)
                                filename = video.system_metadata.filename[:-4] if hasattr(video, 'system_metadata') else result.video_id
                                if len(filename) > 50:
                                    filename = filename[:50] + '...'
                            except Exception as e:
                                video = None
                                filename = result.video_id
                            
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                # Display video player with time segment if available
                                if video and hasattr(video, 'hls') and hasattr(video.hls, 'video_url') and video.hls.video_url:
                                    try:
                                        # Use Streamlit's native start_time parameter for fast seeking
                                        video_url = video.hls.video_url
                                        if hasattr(result, 'start'):
                                            st.video(video_url, start_time=int(result.start))
                                        else:
                                            st.video(video_url)
                                        if hasattr(result, 'start') and hasattr(result, 'end'):
                                            st.caption(f"Playing segment: {result.start:.1f}s - {result.end:.1f}s")
                                    except Exception:
                                        st.info("Video player not available for this result.")
                                else:
                                    st.info("Video not available for this result.")
                                
                                # Show matching text if available
                                if hasattr(result, 'text') and result.text:
                                    st.write("**Matching Text:**")
                                    st.write(result.text)
                            
                            with col2:
                                st.write(f"**File:** {filename}")
                                st.write(f"**Video ID:** `{result.video_id[:16]}...`")
                                if hasattr(result, 'start') and hasattr(result, 'end'):
                                    start_min = int(result.start // 60)
                                    start_sec = int(result.start % 60)
                                    end_min = int(result.end // 60)
                                    end_sec = int(result.end % 60)
                                    st.write(f"**Segment:** {start_min}:{start_sec:02d} - {end_min}:{end_sec:02d}")
                                st.write(f"**Confidence:** {result.score:.3f}")
                                if hasattr(result, 'confidence'):
                                    st.write(f"**Level:** {result.confidence}")
                                
                                # Add button to view full video
                                if st.button(f"View Full Video", key=f"view_video_{result.video_id}_{i}"):
                                    st.query_params.page = "summary"
                                    st.query_params.video_id = result.video_id
                                    st.rerun()
                
            except Exception as e:
                st.error(f"Search failed: {e}")


def summary_page(index_id: str, index_name: str):
    """Summary page with two-state flow: thumbnail grid or video-specific view"""
    
    st.title("Summarize")
    
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
                        filename = video.system_metadata.filename[:-4] if hasattr(video, 'system_metadata') else video.id
                        if len(filename) > 50:
                            filename = filename[:50] + '...'
                        duration = None
                        if hasattr(video, 'system_metadata') and hasattr(video.system_metadata, 'duration'):
                            duration = video.system_metadata.duration
                            minutes = int(duration // 60)
                            seconds = int(duration % 60)
                            duration_str = f"{minutes}:{seconds:02d}"
                        else:
                            duration_str = "Unknown"
                        
                        # Video thumbnail container (clickable)
                        with st.container():
                            # Try to display thumbnail from HLS thumbnail URLs
                            thumbnail_displayed = False
                            
                            # Thumbnails are located at video.hls.thumbnail_urls (list)
                            try:
                                if (hasattr(video, 'hls') and 
                                    hasattr(video.hls, 'thumbnail_urls') and 
                                    video.hls.thumbnail_urls and 
                                    len(video.hls.thumbnail_urls) > 0):
                                    thumbnail_url = video.hls.thumbnail_urls[0]
                                    st.image(thumbnail_url, use_container_width=True)
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
                                        VIDEO
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                            
                            # Video details
                            st.markdown(f"**{filename}**")
                            st.caption(f"{duration_str} | ID: {video.id[:8]}...")
                            
                            # Select button that sets query param
                            button_key = f"select_summary_{video.id}"
                            if st.button("Summarize This Video", key=button_key, use_container_width=True):
                                st.query_params.video_id = video.id
                                st.rerun()
    
    else:
        # State 2: Video selected - Show video player and auto-generated summary
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
        
        # Back button
        if st.button("← Back to Videos"):
            del st.query_params.video_id
            st.rerun()

        # Get video info
        filename = selected_video.system_metadata.filename[:-4] if hasattr(selected_video, 'system_metadata') else selected_video.id
        if len(filename) > 50:
            filename = filename[:50] + '...'
        
        # Two-column layout: Video on left, Summary on right
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Column title
            st.markdown(f"<h4 style='margin-bottom: 10px;'>{filename}</h4>", unsafe_allow_html=True)
            if (hasattr(selected_video, 'hls') and 
                hasattr(selected_video.hls, 'video_url') and 
                selected_video.hls.video_url):
                try:
                    st.video(selected_video.hls.video_url)
                except Exception as e:
                    st.info("Video player not available.")
            else:
                # Show thumbnail instead
                try:
                    if (hasattr(selected_video, 'hls') and 
                        hasattr(selected_video.hls, 'thumbnail_urls') and 
                        selected_video.hls.thumbnail_urls and 
                        len(selected_video.hls.thumbnail_urls) > 0):
                        st.image(selected_video.hls.thumbnail_urls[0], use_container_width=True)
                    else:
                        st.info("Video preview not available.")
                except:
                    st.info("Video preview not available.")
            
            # Video metadata
            caption = ""
            if hasattr(selected_video, 'system_metadata') and hasattr(selected_video.system_metadata, 'duration'):
                duration = selected_video.system_metadata.duration
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                caption+=f"Duration: {minutes}:{seconds:02d}"
            
            caption+=f" | Video ID: {selected_video.id}"
            st.caption(caption)
        
        with col2:
            # Column title
            st.markdown("<h4 style='text-align: left; margin-bottom: 10px;'>Summary</h4>", unsafe_allow_html=True)
            
            # Summary container with fixed height and scrolling
            with st.container(height=480, border=True):
                # Check if summary is already cached
                cache_key = f"summary_{selected_video.id}"
                
                if cache_key not in st.session_state:
                    # Auto-generate summary with concise prompt
                    with st.spinner("Generating summary..."):
                        try:
                            # Always use "summary" type with a concise prompt
                            summary_result = client.summarize(
                                video_id=selected_video.id,
                                type="summary",
                                prompt="Provide a very concise summary. Focus on the main points without unnecessary details."
                            )
                            
                            # Cache the summary
                            if hasattr(summary_result, 'summary') and summary_result.summary:
                                st.session_state[cache_key] = summary_result.summary
                            elif hasattr(summary_result, 'data') and summary_result.data:
                                st.session_state[cache_key] = str(summary_result.data)
                            else:
                                st.session_state[cache_key] = str(summary_result)
                            
                        except Exception as e:
                            st.error(f"Failed to generate summary: {e}")
                            st.info("Please check that the video has been fully processed and try again.")
                            st.session_state[cache_key] = None
                
                # Display cached summary
                if st.session_state.get(cache_key):
                    st.write(st.session_state[cache_key])
                



def qa_page(index_id: str, index_name: str):
    """Q&A page with two-state flow: thumbnail grid or video-specific chat"""
    
    st.title("Chat")
    
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
                        filename = video.system_metadata.filename[:-4] if hasattr(video, 'system_metadata') else video.id
                        if len(filename) > 50:
                            filename = filename[:50] + '...'
                        duration = None
                        if hasattr(video, 'system_metadata') and hasattr(video.system_metadata, 'duration'):
                            duration = video.system_metadata.duration
                            minutes = int(duration // 60)
                            seconds = int(duration % 60)
                            duration_str = f"{minutes}:{seconds:02d}"
                        else:
                            duration_str = "Unknown"
                        
                        # Video thumbnail container (clickable)
                        with st.container():
                            # Try to display thumbnail from HLS thumbnail URLs
                            thumbnail_displayed = False
                            
                            # Thumbnails are located at video.hls.thumbnail_urls (list)
                            try:
                                if (hasattr(video, 'hls') and 
                                    hasattr(video.hls, 'thumbnail_urls') and 
                                    video.hls.thumbnail_urls and 
                                    len(video.hls.thumbnail_urls) > 0):
                                    thumbnail_url = video.hls.thumbnail_urls[0]
                                    st.image(thumbnail_url, use_container_width=True)
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
                                        VIDEO
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                            
                            # Video details
                            st.markdown(f"**{filename}**")
                            st.caption(f"{duration_str} | ID: {video.id[:8]}...")
                            
                            # Select button that sets query param
                            button_key = f"select_qa_{video.id}"
                            if st.button("Chat About This Video", key=button_key, use_container_width=True):
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
        
        # Back button
        if st.button("← Back to Videos"):
            del st.query_params.video_id
            st.rerun()

        # Get video info
        filename = selected_video.system_metadata.filename[:-4] if hasattr(selected_video, 'system_metadata') else selected_video.id
        if len(filename) > 50:
            filename = filename[:50] + '...'
        
        # Two-column layout: Video on left, Chat on right
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Column title
            st.markdown(f"<h4 style='margin-bottom: 10px;'>{filename}</h4>", unsafe_allow_html=True)
            # Try to display video if URL is available
            if (hasattr(selected_video, 'hls') and 
                hasattr(selected_video.hls, 'video_url') and 
                selected_video.hls.video_url):
                try:
                    st.video(selected_video.hls.video_url)
                except Exception as e:
                    st.info("Video player not available.")
            else:
                # Show thumbnail instead
                try:
                    if (hasattr(selected_video, 'hls') and 
                        hasattr(selected_video.hls, 'thumbnail_urls') and 
                        selected_video.hls.thumbnail_urls and 
                        len(selected_video.hls.thumbnail_urls) > 0):
                        st.image(selected_video.hls.thumbnail_urls[0], use_container_width=True)
                    else:
                        st.info("Video preview not available.")
                except:
                    st.info("Video preview not available.")
            
            # Video metadata
            caption = ""
            if hasattr(selected_video, 'system_metadata') and hasattr(selected_video.system_metadata, 'duration'):
                duration = selected_video.system_metadata.duration
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                caption += f"Duration: {minutes}:{seconds:02d}"
            
            caption += f" | Video ID: {selected_video.id}"
            st.caption(caption)
        
        with col2:
            # Column title
            st.markdown("<h4 style='text-align: left; margin-bottom: 10px;'>Chat</h4>", unsafe_allow_html=True)
            
            # Chat history container with fixed height and scrolling
            with st.container(height=420, border=True):
                # Display chat history
                for item in st.session_state[chat_history_key]:
                    with st.chat_message("user"):
                        st.write(item["question"])
                    with st.chat_message("assistant"):
                        st.write(item["answer"])
                        st.caption(f"Response time: {item.get('response_time', 'N/A')}")
                
                # Chat input at the bottom of the container
                question = st.chat_input("Ask a question about the video...")
                
                if question and question.strip():
                    # Add question to chat immediately with loading placeholder
                    st.session_state[chat_history_key].append({
                        "question": question,
                        "answer": "Thinking...",
                        "response_time": "Loading..."
                    })
                    st.rerun()
                
                # Show suggested questions below chat input if no chat history
                if not st.session_state[chat_history_key]:
                    suggestions = [
                        "What is this video about?",
                        "Who are the speakers?", 
                        "What happens at 2:30?"
                    ]
                    
                    for suggestion in suggestions:
                        if st.button(f"{suggestion}", key=f"suggest_{suggestion}", use_container_width=True):
                            # Set the suggestion to be processed
                            st.session_state.temp_question = suggestion
                            st.rerun()
            
            # Check for suggested question
            if hasattr(st.session_state, 'temp_question') and st.session_state.temp_question:
                question_to_process = st.session_state.temp_question
                st.session_state.temp_question = None  # Clear it
                
                # Add question to chat immediately with loading placeholder
                st.session_state[chat_history_key].append({
                    "question": question_to_process,
                    "answer": "Thinking...",
                    "response_time": "Loading..."
                })
                st.rerun()
            
            # Process pending question (if last message has loading placeholder)
            if (st.session_state[chat_history_key] and 
                st.session_state[chat_history_key][-1]["answer"] == "Thinking..."):
                
                pending_question = st.session_state[chat_history_key][-1]["question"]
                
                with st.spinner("Analyzing video and generating answer..."):
                    try:
                        start_time = time.time()
                        result = client.analyze(
                            video_id=selected_video.id,
                            prompt=pending_question
                        )
                        response_time = time.time() - start_time
                        
                        # Extract answer
                        if hasattr(result, 'answer'):
                            answer = result.answer
                        elif hasattr(result, 'data') and result.data:
                            answer = str(result.data)
                        else:
                            answer = str(result)
                        
                        # Update the last message with the real answer
                        st.session_state[chat_history_key][-1] = {
                            "question": pending_question,
                            "answer": answer,
                            "response_time": f"{response_time:.1f}s"
                        }
                        
                        # Rerun to show the answer
                        st.rerun()
                        
                    except Exception as e:
                        # Update with error message
                        st.session_state[chat_history_key][-1] = {
                            "question": pending_question,
                            "answer": f"Error: {str(e)}",
                            "response_time": "Error"
                        }
                        st.rerun()
            
            # Clear chat button
            if st.button("Clear Chat History", use_container_width=True):
                st.session_state[chat_history_key] = []
                st.rerun()



def full_app_with_sidebar(index_id: str, index_name: str):
    """Full app with sidebar when index is selected"""
    
    # Sidebar with logo
    st.sidebar.markdown(f"""<div style="text-align: center; margin-bottom: 15px;"><a href="http://localhost:8501/"><img src="https://raw.githubusercontent.com/erickfm/assets/main/images/snip.png" style="padding-right: 10px;" width="100%" height="60%"></a></div>""", unsafe_allow_html=True)
    
    # Get current page from query params
    current_page = st.query_params.get("page", "search")
    
    # Page navigation buttons
    
    # Search button
    search_clicked = st.sidebar.button("Search", use_container_width=True, type="primary" if current_page == "search" else "secondary")
    if search_clicked and current_page != "search":
        st.query_params["page"] = "search"
        # Clear video_id when navigating away from video-specific pages
        if "video_id" in st.query_params:
            del st.query_params["video_id"]
        st.rerun()
    
    # Summary button  
    summary_clicked = st.sidebar.button("Summarize", use_container_width=True, type="primary" if current_page == "summary" else "secondary")
    if summary_clicked and current_page != "summary":
        st.query_params["page"] = "summary"
        # Clear video_id when navigating to summary overview
        if "video_id" in st.query_params:
            del st.query_params["video_id"]
        st.rerun()
    
    # Q&A button
    qa_clicked = st.sidebar.button("Chat", use_container_width=True, type="primary" if current_page == "qa" else "secondary")
    if qa_clicked and current_page != "qa":
        st.query_params["page"] = "qa"
        # Clear video_id when navigating to qa overview
        if "video_id" in st.query_params:
            del st.query_params["video_id"]
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