# Video Semantic Search (Snippetropolis)

🎬 Search through your video content using natural language queries and images, powered by TwelveLabs AI

## Features

- **🔍 Semantic Search**: Find video content using natural language queries or image uploads
- **📺 Video Management**: Browse and manage videos across multiple indexes with thumbnail previews
- **📝 Auto-Generated Summaries**: Get concise summaries of your videos automatically
- **💬 Q&A Chat**: Ask questions about specific videos and get intelligent answers
- **📊 Multiple Index Support**: Organize videos into different indexes
- **🎯 Segment-Level Results**: Jump directly to relevant video segments with precise timestamps

## Quick Start

### 1. Prerequisites

- Python 3.13+ (specified in pyproject.toml)
- TwelveLabs API key ([Get yours here](https://playground.twelvelabs.io/))

### 2. Installation

Clone the repository:
```bash
git clone <your-repo-url>
cd video-semantic-search
```

Install dependencies using Poetry (recommended):
```bash
poetry install
poetry shell
```

Or using pip:
```bash
pip install -r requirements.txt
```

### 3. Configuration

Set your TwelveLabs API key as an environment variable:
```bash
export TWELVE_LABS_API_KEY=tlk_your_actual_api_key_here
```

Or create a `.env` file in the project root:
```bash
# .env
TWELVE_LABS_API_KEY=tlk_your_actual_api_key_here
```

### 4. Index Management (CLI)

Create a new index:
```bash
python indexing.py create-index "My Videos" --engines marengo2.6
```

Upload videos to your index:
```bash
python indexing.py upload-video <index_id> path/to/video.mp4
```

List all indexes:
```bash
python indexing.py list-indexes
```

List videos in an index:
```bash
python indexing.py list-videos <index_id>
```

### 5. Launch the Web App

Start the Streamlit application:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## How to Use

### 🏠 Getting Started

1. **Select an Index**: Choose from your existing video indexes or create a new one using the CLI
2. **Navigate**: Use the sidebar to switch between Search and Videos pages

### 🔍 Search Videos

**Text Search**:
- Enter natural language queries like "person walking in the park"
- View results with confidence scores and precise timestamps
- Click video segments to jump directly to relevant moments

**Image Search**:
- Upload an image to find visually similar content in your videos
- Perfect for finding specific objects, scenes, or visual patterns

**Example Text Queries**:
- "red car driving on highway"
- "person giving a presentation" 
- "sunset over mountains"
- "dog playing in the yard"

### 📺 Videos Page

**Video Grid**:
- Browse all videos in your index with thumbnail previews
- See video duration and file information
- Click "View Video" to access detailed view

**Individual Video View**:
- Watch full videos with native video player
- View auto-generated summaries in a scrollable panel
- Chat with the video using natural language questions

### 💬 Video Q&A Chat

Ask questions about any video:
- "What is this video about?"
- "Who are the main speakers?"
- "What happens at the 2-minute mark?"
- "What products are mentioned?"

The chat maintains conversation history and provides response times for each query.

## CLI Reference

### `indexing.py` Commands

```bash
# Create a new index
python indexing.py create-index "Index Name" [--engines engine1 engine2]

# Upload video to index  
python indexing.py upload-video <index_id> <video_path> [--language en]

# List all indexes
python indexing.py list-indexes

# List videos in specific index
python indexing.py list-videos <index_id>
```

### Available Engines

- `marengo2.6` - Latest multimodal engine (recommended, default)
- `marengo2.5` - Previous version
- `pegasus1.1` - Conversation and text analysis

## Project Structure

```
video-semantic-search/
├── app.py              # Single-file Streamlit app with all pages
├── indexing.py         # CLI for index/video management  
├── tl_utils.py         # TwelveLabs client utilities
├── pyproject.toml      # Poetry dependencies and metadata
├── requirements.txt    # pip-compatible dependencies
├── poetry.lock         # Locked dependency versions
└── README.md           # This file
```

## Development

### Package Management

This project uses Poetry as the primary package manager. The `requirements.txt` file is maintained for compatibility.

Adding dependencies:
```bash
poetry add package-name
```

Updating requirements.txt:
```bash
poetry export -f requirements.txt --output requirements.txt
```

### Running in Development

Using Poetry (recommended):
```bash
poetry shell
streamlit run app.py
```

Using pip:
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Environment Variables

**Required**:
- `TWELVE_LABS_API_KEY` - Your TwelveLabs API key

**Optional**:
- `STREAMLIT_SERVER_PORT` - Custom port (default: 8501)

## Architecture

The application is built as a single-file multi-page Streamlit app with:

- **Index Selection**: Entry point for choosing or creating video indexes
- **Search Page**: Text and image-based semantic search functionality  
- **Videos Page**: Video grid view and individual video player with chat
- **Sidebar Navigation**: Seamless page switching with persistent state

All video processing, search, and AI features are powered by the TwelveLabs API.

## Troubleshooting

### Common Issues

**"No indexes found"**
- Create an index first: `python indexing.py create-index "My Index"`

**"API key not found"** 
- Ensure your API key is set as an environment variable or in a `.env` file
- Check API key format (should start with `tlk_`)

**"Video processing failed"**
- Ensure video format is supported (MP4, MOV, AVI, etc.)
- Check video file size limits in TwelveLabs documentation
- Wait for processing to complete before searching

**Slow search results**
- Use more specific queries for better performance
- Ensure videos are fully processed (check via CLI)

### Getting Help

1. Check the [TwelveLabs Documentation](https://docs.twelvelabs.io/)
2. Review your API usage at [TwelveLabs Playground](https://playground.twelvelabs.io/)
3. Ensure your API key has sufficient credits

## Dependencies

Core dependencies defined in `pyproject.toml`:
- `twelvelabs` (>=0.4.11,<0.5.0) - TwelveLabs Python SDK
- `streamlit` (>=1.47.1,<2.0.0) - Web app framework
- `python-dotenv` (>=1.1.1,<2.0.0) - Environment variable loading
- `pillow` (>=11.3.0,<12.0.0) - Image processing
- `pandas` (>=2.3.1,<3.0.0) - Data manipulation
