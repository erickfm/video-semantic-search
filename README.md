# Video Semantic Search

🎬 Search video clips using natural language queries powered by TwelveLabs AI

## Features

- **🔍 Semantic Search**: Find video content using natural language, images, or both
- **📝 Video Summarization**: Generate comprehensive summaries with one click
- **💬 Q&A Chat**: Ask questions about video content and get intelligent answers
- **📊 Multiple Index Support**: Manage multiple video indexes
- **🖼️ Multimodal Search**: Combine text and image queries for precise results

## Quick Start

### 1. Prerequisites

- Python 3.13+ (or 3.8+)
- TwelveLabs API key ([Get yours here](https://playground.twelvelabs.io/))

### 2. Installation

Clone the repository:
```bash
git clone <your-repo-url>
cd video-semantic-search
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configuration

Copy the environment template:
```bash
cp .env.example .env
```

Edit `.env` and add your API key:
```
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

## Usage Guide

### 🔍 Search Videos

Navigate to the Search page to:
- **Text Search**: Use natural language queries like "person walking in the park"
- **Image Search**: Upload an image to find visually similar content
- **Multimodal Search**: Combine text and images for precise results

**Example Queries:**
- "red car driving on highway"
- "person giving a presentation" 
- "sunset over mountains"
- "dog playing in the yard"

### 📝 Video Summary

Generate summaries by:
1. Selecting an index and video
2. Choosing summary type (comprehensive, brief, detailed, key_points)
3. Adding custom instructions (optional)
4. Clicking "Generate Summary"

**Custom Instructions Examples:**
- "Focus on technical specifications"
- "Highlight key decisions made"
- "Extract action items and next steps"

### 💬 Q&A Chat

Ask questions about video content:
1. Select an index and video
2. Ask natural language questions
3. Follow up with additional questions
4. Export chat history when done

**Example Questions:**
- "What is this video about?"
- "Who are the main speakers?"
- "What products are mentioned?"
- "What happens at the 2-minute mark?"

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

- `marengo2.6` - Latest multimodal engine (recommended)
- `marengo2.5` - Previous version
- `pegasus1.1` - Conversation and text analysis

## Project Structure

```
video-semantic-search/
├── app.py           # Streamlit entry point & navigation
├── tl_utils.py      # TwelveLabs client utilities
├── indexing.py      # CLI for index/video management
├── pages/           # Streamlit pages
│   ├── search.py    # Search functionality
│   ├── summary.py   # Video summarization
│   └── qa.py        # Q&A chat interface
├── .env.example     # Environment template
├── requirements.txt # Python dependencies
└── README.md        # This file
```

## Development

### Adding Dependencies

When using Poetry (recommended):
```bash
poetry add package-name
poetry export -f requirements.txt --output requirements.txt
```

Or manually edit `requirements.txt` and reinstall:
```bash
pip install -r requirements.txt
```

### Environment Variables

Required:
- `TWELVE_LABS_API_KEY` - Your TwelveLabs API key

Optional:
- `STREAMLIT_SERVER_PORT` - Custom port (default: 8501)

## Troubleshooting

### Common Issues

**"No indexes found"**
- Create an index first: `python indexing.py create-index "My Index"`

**"API key not found"** 
- Ensure `.env` file exists with correct `TWELVE_LABS_API_KEY`
- Check API key format (should start with `tlk_`)

**"Video processing failed"**
- Ensure video format is supported (MP4, MOV, AVI, etc.)
- Check video file size limits
- Wait for processing to complete before searching

**Slow search results**
- Use more specific queries
- Adjust confidence threshold in advanced options
- Ensure videos are fully processed

### Getting Help

1. Check the [TwelveLabs Documentation](https://docs.twelvelabs.io/)
2. Review your API usage at [TwelveLabs Playground](https://playground.twelvelabs.io/)
3. Ensure your API key has sufficient credits

## License

[Your license here]

## Contributing

[Contributing guidelines here]
