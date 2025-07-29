"""
📝 Summary
==========
One-click video summarization functionality.
"""

import streamlit as st
from typing import Dict, Any, List
import time

from tl_utils import get_client


st.set_page_config(page_title="Summary - Video Semantic Search", page_icon="📝")


def display_summary(summary_result, video_info: Dict[str, Any]):
    """Display summary results in a structured format."""
    if not summary_result:
        st.warning("No summary generated.")
        return
    
    # Video information
    st.subheader("📹 Video Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Filename:** {video_info.get('filename', 'Unknown')}")
        st.write(f"**Video ID:** `{video_info.get('id', 'Unknown')}`")
    
    with col2:
        if 'duration' in video_info:
            minutes = int(video_info['duration'] // 60)
            seconds = int(video_info['duration'] % 60)
            st.write(f"**Duration:** {minutes}:{seconds:02d}")
        if 'created_at' in video_info:
            st.write(f"**Created:** {video_info['created_at']}")
    
    st.markdown("---")
    
    # Main summary
    st.subheader("📄 Summary")
    
    # Handle different summary response formats
    if hasattr(summary_result, 'summary') and summary_result.summary:
        st.write(summary_result.summary)
    elif hasattr(summary_result, 'data') and summary_result.data:
        # If data is a list, join summaries
        if isinstance(summary_result.data, list):
            for i, item in enumerate(summary_result.data):
                if hasattr(item, 'summary'):
                    st.write(item.summary)
                elif isinstance(item, str):
                    st.write(item)
        else:
            st.write(str(summary_result.data))
    else:
        st.write(str(summary_result))
    
    # Additional metadata if available
    if hasattr(summary_result, 'metadata') and summary_result.metadata:
        with st.expander("📊 Analysis Metadata"):
            st.json(summary_result.metadata, expanded=False)


def main():
    st.title("📝 Video Summary")
    st.markdown("Generate comprehensive summaries of your video content with one click!")
    
    # Initialize client
    try:
        client = get_client()
    except SystemExit as e:
        st.error(str(e))
        return
    
    # Index selection
    st.subheader("Select Index & Video")
    
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
    
    # Video selection
    with st.spinner("Loading videos..."):
        try:
            videos = list(client.index.video.list(index_id=selected_index_id, page_limit=50))
            if not videos:
                st.warning("No videos found in this index. Upload some videos first.")
                return
                
            video_options = {}
            for video in videos:
                filename = video.system_metadata.filename if hasattr(video, 'system_metadata') else video.id
                duration_info = ""
                if hasattr(video, 'metadata') and video.metadata and hasattr(video.metadata, 'duration'):
                    minutes = int(video.metadata.duration // 60)
                    seconds = int(video.metadata.duration % 60)
                    duration_info = f" ({minutes}:{seconds:02d})"
                
                video_options[f"{filename}{duration_info}"] = {
                    'id': video.id,
                    'filename': filename,
                    'duration': getattr(video.metadata, 'duration', None) if hasattr(video, 'metadata') and video.metadata else None,
                    'created_at': str(video.created_at) if hasattr(video, 'created_at') else None
                }
            
            selected_video_name = st.selectbox("Choose a video:", list(video_options.keys()))
            selected_video = video_options[selected_video_name]
            
        except Exception as e:
            st.error(f"Failed to load videos: {e}")
            return
    
    st.markdown("---")
    
    # Summary options
    st.subheader("Summary Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        summary_type = st.selectbox(
            "Summary Type:",
            [
                "comprehensive",
                "brief", 
                "detailed",
                "key_points"
            ],
            index=0,
            help="Choose the style and length of summary"
        )
    
    with col2:
        custom_prompt = st.text_input(
            "Custom Instructions (optional):",
            placeholder="e.g., 'Focus on technical details' or 'Highlight key decisions'",
            help="Provide specific instructions for the summary"
        )
    
    # Advanced options
    with st.expander("Advanced Options"):
        include_timestamps = st.checkbox(
            "Include Timestamps", 
            value=True,
            help="Include time markers in the summary"
        )
        
        include_speakers = st.checkbox(
            "Identify Speakers",
            value=False,
            help="Attempt to identify different speakers in the video"
        )
        
        language = st.selectbox(
            "Output Language:",
            ["en", "es", "fr", "de", "it", "pt", "zh", "ja", "ko"],
            index=0,
            help="Language for the generated summary"
        )
    
    # Generate summary
    st.markdown("---")
    
    if st.button("📝 Generate Summary", use_container_width=True):
        with st.spinner("Analyzing video and generating summary... This may take a moment."):
            try:
                # Prepare summary parameters
                summary_params = {
                    "video_id": selected_video['id'],
                    "type": summary_type
                }
                
                # Add custom prompt if provided
                if custom_prompt.strip():
                    summary_params["prompt"] = custom_prompt
                
                # Add advanced options
                if language != "en":
                    summary_params["language"] = language
                
                start_time = time.time()
                summary_result = client.analyze.summary(**summary_params)
                analysis_time = time.time() - start_time
                
                st.markdown("---")
                st.success(f"Summary generated in {analysis_time:.1f} seconds!")
                
                display_summary(summary_result, selected_video)
                
                # Download option
                st.markdown("---")
                summary_text = ""
                if hasattr(summary_result, 'summary'):
                    summary_text = summary_result.summary
                elif hasattr(summary_result, 'data'):
                    summary_text = str(summary_result.data)
                
                if summary_text:
                    st.download_button(
                        label="💾 Download Summary",
                        data=summary_text,
                        file_name=f"summary_{selected_video['filename']}.txt",
                        mime="text/plain"
                    )
                
            except Exception as e:
                st.error(f"Failed to generate summary: {e}")
                st.info("Please check that the video has been fully processed and try again.")
    
    # Tips and examples
    st.markdown("---")
    st.subheader("💡 Summary Tips")
    
    with st.expander("How to get better summaries"):
        st.markdown("""
        **Summary Types:**
        - **Comprehensive**: Detailed overview covering all major points
        - **Brief**: Quick overview with key highlights
        - **Detailed**: In-depth analysis with context and background
        - **Key Points**: Bullet-point style summary of main topics
        
        **Custom Instructions Examples:**
        - "Focus on technical specifications and product features"
        - "Highlight key decisions and their reasoning"
        - "Summarize the educational content and learning objectives"
        - "Extract action items and next steps mentioned"
        - "Focus on the financial and business aspects discussed"
        
        **Best Practices:**
        - Ensure videos have clear audio for better analysis
        - Longer videos may take more time to process
        - Custom prompts help tailor summaries to your specific needs
        """)


if __name__ == "__main__":
    main() 