#!/usr/bin/env python3
"""
indexing.py
===========
CLI tool for creating TwelveLabs indexes and uploading videos.
Uses task.create() for efficient video processing.

Usage:
    python indexing.py create-index "My Index" --engines marengo2.6
    python indexing.py upload-video <index_id> <video_path>
    python indexing.py list-indexes
    python indexing.py list-videos <index_id>
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from tl_utils import get_client


def create_index(name: str, engines: List[str]) -> str:
    """
    Create a new TwelveLabs index.
    
    Args:
        name: Name for the new index
        engines: List of engine names to use
        
    Returns:
        str: The created index ID
    """
    client = get_client()
    
    print(f"🔧 Creating index '{name}' with engines: {', '.join(engines)}")
    
    try:
        index = client.index.create(
            name=name,
            engines=[{"name": engine} for engine in engines],
            addons=["thumbnail"]  # Enable thumbnail generation
        )
        print(f"✅ Index created successfully!")
        print(f"   ID: {index.id}")
        print(f"   Name: {index.name}")
        return index.id
        
    except Exception as exc:
        sys.exit(f"❌ Failed to create index: {exc!r}")


def upload_video(index_id: str, video_path: str, language: str = "en") -> str:
    """
    Upload a video to an existing index using task.create().
    
    Args:
        index_id: Target index ID
        video_path: Path to video file
        language: Video language code (default: "en")
        
    Returns:
        str: The created task ID
    """
    client = get_client()
    video_file = Path(video_path)
    
    if not video_file.exists():
        sys.exit(f"❌ Video file not found: {video_path}")
    
    print(f"📹 Uploading video: {video_file.name}")
    print(f"   Target index: {index_id}")
    
    try:
        # Create upload task
        task = client.task.create(
            index_id=index_id,
            file=video_path,
            language=language
        )
        
        print(f"✅ Upload task created!")
        print(f"   Task ID: {task.id}")
        print(f"   Status: {task.status}")
        
        # Wait for processing to complete
        print("⏳ Processing video...")
        
        def print_status(task):
            print(f"   Status: {task.status}")
            if hasattr(task, 'metadata') and task.metadata:
                if hasattr(task.metadata, 'duration'):
                    print(f"   Duration: {task.metadata.duration}s")
        
        # Wait for task completion with status updates
        task.wait_for_done(
            sleep_interval=5,
            callback=print_status
        )
        
        if task.status == "ready":
            print(f"🎉 Video processing completed successfully!")
            print(f"   Video ID: {task.video_id}")
        else:
            print(f"⚠️  Task finished with status: {task.status}")
            
        return task.id
        
    except Exception as exc:
        sys.exit(f"❌ Failed to upload video: {exc!r}")


def list_indexes() -> None:
    """List all indexes in the account."""
    client = get_client()
    
    try:
        indexes = list(client.index.list())
        
        if not indexes:
            print("⚠️  No indexes found in your account.")
            return
            
        print(f"📂 Found {len(indexes)} index(es):")
        print()
        
        for idx in indexes:
            print(f"  • {idx.name}")
            print(f"    ID: {idx.id}")
            print(f"    Created: {idx.created_at}")
            if hasattr(idx, 'engines') and idx.engines:
                engine_names = [engine.name for engine in idx.engines]
                print(f"    Engines: {', '.join(engine_names)}")
            print()
            
    except Exception as exc:
        sys.exit(f"❌ Failed to list indexes: {exc!r}")


def list_videos(index_id: str) -> None:
    """
    List all videos in a specific index.
    
    Args:
        index_id: The index ID to query
    """
    client = get_client()
    
    try:
        # Get index info first
        index_info = client.index.retrieve(index_id)
        print(f"📂 Videos in index: {index_info.name} ({index_id})")
        print()
        
        videos = list(client.index.video.list(index_id=index_id, page_limit=20))
        
        if not videos:
            print("⚠️  No videos found in this index.")
            return
            
        print(f"🎬 Found {len(videos)} video(s):")
        print()
        
        for i, video in enumerate(videos, 1):
            print(f"  {i:>3}. {video.system_metadata.filename}")
            print(f"       ID: {video.id}")
            if hasattr(video, 'metadata') and video.metadata:
                if hasattr(video.metadata, 'duration'):
                    print(f"       Duration: {video.metadata.duration}s")
            print()
            
    except Exception as exc:
        sys.exit(f"❌ Failed to list videos: {exc!r}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="TwelveLabs indexing and video upload CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create index command
    create_parser = subparsers.add_parser("create-index", help="Create a new index")
    create_parser.add_argument("name", help="Index name")
    create_parser.add_argument(
        "--engines", 
        nargs="+", 
        default=["marengo2.6"],
        help="Engine names to use (default: marengo2.6)"
    )
    
    # Upload video command
    upload_parser = subparsers.add_parser("upload-video", help="Upload video to index")
    upload_parser.add_argument("index_id", help="Target index ID")
    upload_parser.add_argument("video_path", help="Path to video file")
    upload_parser.add_argument(
        "--language", 
        default="en",
        help="Video language code (default: en)"
    )
    
    # List indexes command
    subparsers.add_parser("list-indexes", help="List all indexes")
    
    # List videos command
    videos_parser = subparsers.add_parser("list-videos", help="List videos in index")
    videos_parser.add_argument("index_id", help="Index ID to query")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    # Execute commands
    if args.command == "create-index":
        create_index(args.name, args.engines)
        
    elif args.command == "upload-video":
        upload_video(args.index_id, args.video_path, args.language)
        
    elif args.command == "list-indexes":
        list_indexes()
        
    elif args.command == "list-videos":
        list_videos(args.index_id)


if __name__ == "__main__":
    main() 