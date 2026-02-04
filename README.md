# Instagram Content Generation Engine

Automated Instagram content generator for Real Health Kombucha, creating Reels and Feed posts from organized local assets.

**Repository**: [https://github.com/roel-heremans/Kombucha](https://github.com/roel-heremans/Kombucha)

## Features

- **Theme-based Asset Organization**: Organize photos, videos, and PDFs by themes (e.g., "Kombucha Benefits", "Kombucha Research")
- **AI-Powered Captions**: Generate engaging captions and hashtags using AI from PDF content
- **Brand Consistency**: Automatically extracts and applies brand colors and fonts from realhealthkombucha.com
- **Image Posts**: Create Instagram feed posts with text overlays and brand styling
- **Video Reels**: Generate Instagram Reels with clips, music, transitions, and text overlays
- **Batch Generation**: Generate multiple feed posts and reels in one command
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

4. Set up environment variables (create `.env` file in project root):
```bash
OPENAI_API_KEY=your_api_key_here
```
   Get your OpenAI API key from: https://platform.openai.com/api-keys

5. Extract brand information from your website (optional but recommended):
```bash
python3 main.py extract-brand
```
   This will scrape realhealthkombucha.com and update your brand colors and fonts in the config.

## Project Structure

```
Kombucha/
├── assets/                      # Your content assets
│   ├── 00_music/                # Background music files (optional, for reels)
│   ├── 01_images/               # Shared images (used by all themes)
│   ├── 02_videos/               # Shared videos (used by all themes)
│   ├── 03_kombucha_quotes/      # Quotes collection (.txt files)
│   ├── 04_immune_system/
│   │   └── pdfs/                # Theme-specific PDFs
│   ├── 05_kombucha_benefits/
│   │   └── pdfs/
│   ├── 06_digestive_health/
│   │   └── pdfs/
│   ├── 07_kombucha_research/
│   │   └── pdfs/
│   ├── madeira_local/
│   │   └── pdfs/
│   ├── yoga_retreats/
│   │   └── pdfs/
│   └── yoga_wellness/
│       └── pdfs/
├── output/                      # Generated content ready for posting
│   ├── reels/                   # Generated reel videos (.mp4)
│   └── feed_posts/              # Generated feed post images (.jpg)
├── config/                      # Configuration files
│   └── settings.yaml            # Brand colors, fonts, themes, AI settings
└── src/                         # Source code
```

## Usage

### 1. Organize Your Assets

Organize your content assets in the following structure:
- **Music files**: Place in `assets/00_music/` (optional, for background music in reels)
- **Images**: Place in `assets/01_images/` (shared across all themes, used for feed posts)
- **Videos**: Place in `assets/02_videos/` (shared across all themes, used for reels)
- **Quotes**: Place `.txt` files in `assets/03_kombucha_quotes/` (one quote per file)
- **PDFs**: Place in `assets/[theme_name]/pdfs/` (theme-specific research/content)

### 2. Extract Brand Information

Extract brand colors and fonts from your website (optional but recommended):
```bash
python3 main.py extract-brand
```

### 3. List Available Themes

View all available themes and their asset counts:
```bash
python3 main.py themes
```

### 4. Generate Feed Posts

Generate Instagram feed posts (square images with text overlays):

```bash
# Generate feed post with random image and AI-generated caption from PDFs
python3 main.py generate --theme 05_kombucha_benefits --type feed

# Generate feed post with specific image
python3 main.py generate --theme 06_digestive_health --type feed --image assets/01_images/my_image.jpg

# Generate feed post with quote card (creates quote card image)
python3 main.py generate --theme 04_immune_system --type feed --use-quote

# Generate feed post without PDF content (uses default caption)
python3 main.py generate --theme 07_kombucha_research --type feed --no-pdf
```

### 5. Generate Reels

Generate Instagram Reels (vertical videos):

```bash
# Generate reel with random videos and AI-generated caption
python3 main.py generate --theme 05_kombucha_benefits --type reel

# Generate reel with specific videos
python3 main.py generate --theme 06_digestive_health --type reel --videos assets/02_videos/video1.mp4 --videos assets/02_videos/video2.mp4

# Generate reel with background music
python3 main.py generate --theme 07_kombucha_research --type reel --music assets/00_music/Evening.mp3

# Generate combined reel (video + image + quote + health benefit overlay)
python3 main.py generate --theme 05_kombucha_benefits --type reel --combined --music assets/00_music/Evening.mp3

# Generate combined reel with specific image and videos
python3 main.py generate --theme 06_digestive_health --type reel --combined --image assets/01_images/photo.jpg --videos assets/02_videos/clip1.mp4 --music assets/00_music/Evening.mp3
```

### 6. Batch Generation (Generate Multiple Content at Once)

Generate multiple feed posts and reels in one command - perfect for creating content in bulk:

```bash
# Generate 3 feed posts and 3 reels (default)
python3 main.py batch-generate

# Generate specific numbers
python3 main.py batch-generate --feeds 5 --reels 5

# Generate only feeds (no reels)
python3 main.py batch-generate --feeds 5 --reels 0

# Generate only reels (no feeds)
python3 main.py batch-generate --feeds 0 --reels 5

# Use specific themes only
python3 main.py batch-generate --themes 05_kombucha_benefits --themes 06_digestive_health

# Use specific music for all reels
python3 main.py batch-generate --music assets/00_music/Morning.mp3

# All batch generations use quotes and LLM refinement by default
# (quotes and LLM refinement are enabled automatically)
python3 main.py batch-generate --feeds 3 --reels 3
```

**Batch Generation Features:**
- **Random Selection**: Automatically picks themes, images, videos, and music from your assets
- **Progress Tracking**: Shows real-time progress for each item being generated
- **Error Handling**: Continues generating even if one item fails, shows detailed summary at the end
- **Smart Defaults**: Uses quotes and LLM refinement by default for best quality content
- **Organized Output**: All content saved to `output/feed_posts/` and `output/reels/` with timestamps

**Example Output:**
```
============================================================
Batch Content Generation
============================================================
Themes: 04_immune_system, 05_kombucha_benefits, 06_digestive_health
Feed posts: 3
Reels: 3
Use quotes: True
LLM refinement: True
============================================================

Generating 3 feed post(s)...
[1/3] Generating feed post for theme: 05_kombucha_benefits
  ✓ Success!
  Image: 05_kombucha_benefits_20260204_010040.jpg
...

============================================================
Batch Generation Summary
============================================================
Feed posts: 3/3 successful
Reels: 3/3 successful

Generated content saved to:
  Feed posts: output/feed_posts/
  Reels: output/reels/
```

### 7. Generate Quote Cards

Generate standalone quote card images:

```bash
# Generate quote card with random quote
python3 generate_quote_card.py

# Generate quote card with custom quote
python3 generate_quote_card.py "Your custom quote text here"
```

### 8. View Statistics

View statistics about your assets:

```bash
# View overall statistics
python3 main.py stats

# View statistics for a specific theme
python3 main.py stats --theme 05_kombucha_benefits
```

### 9. Check Configuration

View current configuration settings:
```bash
python3 main.py config
```

## Output

All generated content is saved in the `output/` directory:
- **Feed posts**: `output/feed_posts/[theme]_[timestamp].jpg` + caption file
- **Reels**: `output/reels/[theme]_[timestamp].mp4` + caption file
- **Quote cards**: `output/feed_posts/quote_[timestamp].jpg`

Each generated post includes:
- The final image/video file ready for Instagram
- A caption file with hashtags and metadata
- JSON metadata file with generation details

## Configuration

Edit `config/settings.yaml` to customize:
- Brand colors and fonts (auto-extracted from website)
- Theme settings and hashtags
- AI provider and model settings
- Target audiences

## License

Private project for Real Health Kombucha
