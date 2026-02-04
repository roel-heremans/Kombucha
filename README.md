# Instagram Content Generation Engine

Automated Instagram content generator for Real Health Kombucha, creating Reels and Feed posts from organized local assets.

**Repository**: [https://github.com/roel-heremans/Kombucha](https://github.com/roel-heremans/Kombucha)

## Features

- **Theme-based Asset Organization**: Organize photos, videos, and PDFs by themes (e.g., "Kombucha Benefits", "Kombucha Research")
- **AI-Powered Captions**: Generate engaging captions and hashtags using AI from PDF content
- **LLM-Refined Content**: PDF preprocessing uses AI to transform technical research into accessible, human-friendly key points
- **Brand Consistency**: Automatically extracts and applies brand colors and fonts from realhealthkombucha.com
- **Image Posts**: Create Instagram feed posts with text overlays and brand styling
- **Video Reels**: Generate Instagram Reels with clips, music, transitions, and text overlays using refined, accessible content
- **Batch Generation**: Generate multiple feed posts and reels in one command
- **Smart Content Selection**: Automatically uses refined key points from JSON files for better video content
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

### 3. Preprocess PDFs (Highly Recommended)

Preprocess PDFs to extract structured information and save to JSON files. **This step uses AI to transform technical research into accessible, human-friendly key points** that are perfect for social media content.

```bash
# Preprocess a specific theme
python3 main.py preprocess-pdfs --theme 05_kombucha_benefits

# Preprocess all themes (04-07)
python3 main.py preprocess-pdfs --all

# Reprocess even if JSON exists (useful after updating PDFs or refining prompts)
python3 main.py preprocess-pdfs --theme 06_digestive_health --force

# Customize pages per PDF (default: 10)
python3 main.py preprocess-pdfs --theme 05_kombucha_benefits --max-pages 15
```

**Benefits:**
- **AI-Refined Content**: Key points are automatically transformed from technical language into accessible, engaging takeaways
- **Faster Content Generation**: No PDF processing during video generation - uses pre-processed JSON
- **Better Video Content**: Refined key points are optimized for readability and engagement
- **Manual Curation**: Edit `assets/{theme}/content.json` to refine extracted information
- **Version Control Friendly**: JSON is text-based and easy to track
- **Reprocess Anytime**: Update JSON files when PDFs change or to improve refinement

**JSON File Structure:**
The preprocessing creates `assets/{theme}/content.json` with:

```json
{
  "theme": "05_kombucha_benefits",
  "processed_at": "2026-02-04T12:00:00",
  "pdfs": [
    {
      "filename": "research_paper.pdf",
      "key_points": [
        "Kombucha helps support your digestive system naturally.",
        "The probiotics in kombucha can boost your immune health."
      ],
      "word_count": 5000,
      "character_count": 25000,
      "pages_processed": 10
    }
  ],
  "summary": {
    "combined_key_points": [
      "Kombucha is a fermented drink that supports gut health.",
      "Regular consumption may boost your immune system."
    ],
    "total_word_count": 15000,
    "total_character_count": 75000,
    "total_pdfs": 3
  }
}
```

**Note**: Full PDF text is not stored in JSON (only refined key points) to keep files manageable and focused on actionable content.

**Manual Editing:**
You can manually edit the JSON file to:
- Refine or rewrite key points for your brand voice
- Remove irrelevant or less impactful points
- Add custom key points
- Adjust the tone and style
- Remove points that don't align with your messaging

**How Content Generation Uses JSON:**
- When generating videos, the system automatically uses refined key points from JSON (if available)
- Randomly selects from available key points for variety
- Falls back to PDF processing only if JSON doesn't exist
- Health benefit overlays use the accessible, refined language from JSON

### 4. List Available Themes

View all available themes and their asset counts:
```bash
python3 main.py themes
```

### 5. Generate Feed Posts

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

### 6. Generate Reels

Generate Instagram Reels (vertical videos):

```bash
# Generate reel with random videos and AI-generated caption
python3 main.py generate --theme 05_kombucha_benefits --type reel

# Generate reel with specific videos
python3 main.py generate --theme 06_digestive_health --type reel --videos assets/02_videos/video1.mp4 --videos assets/02_videos/video2.mp4

# Generate reel with background music
python3 main.py generate --theme 07_kombucha_research --type reel --music assets/00_music/Evening.mp3

# Generate combined reel (video + image + quote + health benefit overlay)
# Uses refined key points from JSON automatically for better content
python3 main.py generate --theme 05_kombucha_benefits --type reel --combined --music assets/00_music/Evening.mp3

# Generate combined reel with specific image and videos
python3 main.py generate --theme 06_digestive_health --type reel --combined --image assets/01_images/photo.jpg --videos assets/02_videos/clip1.mp4 --music assets/00_music/Evening.mp3

# Generate combined reel with additional LLM refinement (only if not using JSON)
python3 main.py generate --theme 07_kombucha_research --type reel --combined --llm-refine --music assets/00_music/Morning.mp3
```

### 7. Batch Generation (Generate Multiple Content at Once)

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
# Note: If JSON files exist, refined key points are used automatically (no additional LLM refinement needed)
python3 main.py batch-generate --feeds 3 --reels 3

# Disable quotes or LLM refinement if desired
python3 main.py batch-generate --feeds 3 --reels 3 --no-use-quote --no-llm-refine
```

**Batch Generation Features:**
- **Random Selection**: Automatically picks themes, images, videos, and music from your assets
- **Progress Tracking**: Shows real-time progress for each item being generated
- **Error Handling**: Continues generating even if one item fails, shows detailed summary at the end
- **Smart Content**: Automatically uses refined key points from JSON files when available (better than raw PDF extraction)
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

### 8. Generate Quote Cards

Generate standalone quote card images:

```bash
# Generate quote card with random quote
python3 generate_quote_card.py

# Generate quote card with custom quote
python3 generate_quote_card.py "Your custom quote text here"
```

### 9. View Statistics

View statistics about your assets:

```bash
# View overall statistics
python3 main.py stats

# View statistics for a specific theme
python3 main.py stats --theme 05_kombucha_benefits
```

### 10. Check Configuration

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
- Language settings (default: English)

## Workflow Recommendations

### Recommended Workflow:

1. **Organize Assets**: Place PDFs, images, videos, and music in the correct folders
2. **Preprocess PDFs**: Run `preprocess-pdfs --all` to create refined JSON files
3. **Review & Edit**: Manually review and edit `content.json` files to match your brand voice
4. **Generate Content**: Use `batch-generate` or individual `generate` commands
5. **Post**: Upload generated content to Instagram using the provided captions

### Best Practices:

- **Preprocess First**: Always preprocess PDFs before generating content for best results
- **Review JSON Files**: Take time to review and refine key points in JSON files
- **Use Combined Reels**: Combined reels (with quotes + health benefits) perform best
- **Batch Generation**: Use batch generation to create multiple pieces of content efficiently
- **Reprocess When Needed**: Use `--force` flag to reprocess PDFs after updates

## Troubleshooting

**Q: Videos don't use refined key points from JSON**
- A: Make sure you've run `preprocess-pdfs` first. Check that `content.json` exists in your theme folder.

**Q: Key points are too technical**
- A: Edit the JSON file manually, or reprocess with `--force` to regenerate with improved LLM refinement.

**Q: Content generation is slow**
- A: Preprocess PDFs first! JSON-based generation is much faster than on-the-fly PDF processing.

**Q: Want to use different key points**
- A: Edit `assets/{theme}/content.json` directly, or the system automatically uses random selection for variety.

## License

Private project for Real Health Kombucha
