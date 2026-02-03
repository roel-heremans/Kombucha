# Instagram Content Generation Engine

Automated Instagram content generator for Real Health Kombucha, creating Reels and Feed posts from organized local assets.

**Repository**: [https://github.com/roel-heremans/Kombucha](https://github.com/roel-heremans/Kombucha)

## Features

- **Theme-based Asset Organization**: Organize photos, videos, and PDFs by themes (e.g., "Kombucha Benefits", "Kombucha Research")
- **AI-Powered Captions**: Generate engaging captions and hashtags using AI from PDF content
- **Brand Consistency**: Automatically extracts and applies brand colors and fonts from realhealthkombucha.com
- **Image Posts**: Create Instagram feed posts with text overlays and brand styling
- **Video Reels**: Generate Instagram Reels with clips, music, transitions, and text overlays
- **Ready-to-Post**: Outputs final content files with captions ready for manual posting

## Installation

1. Install Python 3.9 or higher

2. Install FFmpeg (required for video processing):
   - **Linux**: `sudo apt-get install ffmpeg` or `sudo yum install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download from https://ffmpeg.org/download.html

3. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (create `.env` file in project root):
```bash
OPENAI_API_KEY=your_api_key_here
```
   Get your OpenAI API key from: https://platform.openai.com/api-keys

4. Extract brand information from your website (optional but recommended):
```bash
python main.py extract-brand
```
   This will scrape realhealthkombucha.com and update your brand colors and fonts in the config.

## Project Structure

```
Kombucha/
├── assets/              # Your content assets organized by theme
│   ├── kombucha_benefits/
│   │   ├── images/
│   │   ├── videos/
│   │   └── pdfs/
│   └── kombucha_research/
│       ├── images/
│       ├── videos/
│       └── pdfs/
├── output/              # Generated content ready for posting
│   ├── reels/
│   └── feed_posts/
├── config/              # Configuration files
│   └── settings.yaml
└── src/                 # Source code
```

## Usage

1. Organize your assets in theme directories under `assets/`
   - Place images in `assets/[theme]/images/`
   - Place videos in `assets/[theme]/videos/`
   - Place PDFs in `assets/[theme]/pdfs/`

2. Extract brand information (if not done during installation):
```bash
python main.py extract-brand
```

3. List available themes:
```bash
python main.py themes
```

4. Generate content:
```bash
# Generate a feed post
python main.py generate --theme kombucha_benefits --type feed

# Generate a reel
python main.py generate --theme kombucha_research --type reel

# Use specific image/video
python main.py generate --theme kombucha_benefits --type feed --image path/to/image.jpg
python main.py generate --theme kombucha_research --type reel --videos path/to/video1.mp4 --videos path/to/video2.mp4

# Add background music to reel
python main.py generate --theme kombucha_benefits --type reel --music path/to/music.mp3
```

5. View statistics:
```bash
python main.py stats
python main.py stats --theme kombucha_benefits
```

6. Check configuration:
```bash
python main.py config
```

## Configuration

Edit `config/settings.yaml` to customize:
- Brand colors and fonts (auto-extracted from website)
- Theme settings and hashtags
- AI provider and model settings
- Target audiences

## License

Private project for Real Health Kombucha
