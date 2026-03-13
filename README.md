# YouTube Transcript System

A systematic tool for extracting, processing, and organizing YouTube video subtitles for LLM analysis and knowledge extraction.

## 🎯 Purpose

This system helps you:
- Automatically extract subtitles from YouTube videos of entrepreneurs, investors, and thought leaders
- Process raw VTT subtitles into clean, LLM-ready text format
- Organize content by person, topic, and timeline
- Export data in multiple formats for notebook LLM analysis

## 📁 Project Structure

```
youtube_transcript_system/
├── config/                          # Configuration files
│   ├── channels.json               # Target channels/personalities
│   ├── search_keywords.json        # Search keywords by topic
│   └── system_settings.json        # System settings
├── data/                           # Data storage
│   ├── raw/                       # Raw data
│   │   ├── vtt_subtitles/         # Raw VTT subtitles
│   │   └── video_metadata/        # Video metadata
│   ├── processed/                 # Processed data
│   │   ├── clean_text/            # Clean text (LLM-ready)
│   │   └── indexed/               # Indexed and categorized data
│   └── exports/                   # Export files
│       └── notebook_ready/        # Notebook LLM ready format
├── scripts/                        # Core scripts
│   ├── youtube_scraper.py         # YouTube scraping script
│   ├── subtitle_processor.py      # Subtitle processing script
│   ├── export_manager.py          # Export management script
│   └── update_scheduler.py        # Auto-update scheduler
├── logs/                          # Log files
├── docs/                          # Documentation
│   └── usage_guide.md             # Usage guide
└── README.md                      # This file
```

## ⚙️ Setup

### Prerequisites
```bash
pip install yt-dlp
```

### Configuration
1. Edit `config/channels.json` to add target personalities
2. Customize `config/search_keywords.json` for your topics of interest
3. Adjust `config/system_settings.json` for your preferences

### Usage
```bash
cd scripts
python3 youtube_scraper.py --update
```

## 📤 Output Formats

All processed files are LLM-ready:

- **Pure Text** (`data/processed/clean_text/`): Clean text without timestamps or formatting
- **JSON Format** (`data/exports/notebook_ready/`): Structured data with metadata
- **Markdown** (`data/exports/notebook_ready/`): Formatted with headers and categories

## 🌍 Network Considerations

If you're experiencing network issues with YouTube access:
1. Use this system on a server with better YouTube connectivity (like your Silicon Valley server)
2. The system is designed to be portable - just clone and run anywhere
3. All configuration is in JSON files, making it easy to customize per environment

## 🔄 Automatic Updates

The system supports:
- Scheduled updates (via cron jobs)
- Incremental processing (only new content)
- Error recovery and retry logic
- Data retention policies

## 📝 License

MIT License - feel free to modify and extend for your needs.

## 🚀 Getting Started

1. Clone this repository
2. Install dependencies: `pip install yt-dlp`
3. Configure your targets in `config/` directory
4. Run the scraper: `cd scripts && python3 youtube_scraper.py --update`
5. Find your LLM-ready content in `data/processed/clean_text/`

Happy analyzing! 🧠