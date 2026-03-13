# YouTube 字幕提取系统使用指南

## 🎯 系统目标
自动化提取指定人物（如孙宇晨）的YouTube视频字幕，提供纯净文本格式供notebook LLM进行价值提炼。

## 📁 目录结构说明

### 配置文件 (`config/`)
- `channels.json`: 定义要监控的YouTube频道
- `search_keywords.json`: 定义搜索关键词和分类
- `system_settings.json`: 系统运行参数

### 数据存储 (`data/`)
- `raw/`: 原始VTT字幕和元数据
- `processed/`: 处理后的纯文本字幕
- `exports/`: 导出的notebook就绪文件

### 核心脚本 (`scripts/`)
- `youtube_scraper.py`: 主要的检索和提取脚本
- 其他辅助脚本（待开发）

## 🚀 快速开始

### 1. 配置目标人物
编辑 `config/channels.json` 添加要监控的频道ID或用户名。

### 2. 运行字幕提取
```bash
cd /Users/lhluo/.openclaw/workspace/youtube_transcript_system
python3 scripts/youtube_scraper.py --personality "孙宇晨" --max-videos 5
```

### 3. 获取导出文件
处理完成的文件位于：
- `data/exports/notebook_ready/` - 可直接导入notebook LLM的文件
- 支持多种格式：`.txt`, `.json`, `.md`

## 🔧 高级功能

### 自动更新
系统支持定期自动检查新视频并提取字幕。

### 智能分类
字幕会按主题自动分类，便于针对性分析。

### 增量处理
只处理新内容，避免重复工作。

## 📊 输出格式说明

### 纯文本格式 (`.txt`)
- 无时间戳、无格式标记
- 保留完整对话内容
- 可直接拖拽到notebook LLM

### JSON格式 (`.json`)
- 包含视频标题、URL、发布时间等元数据
- 结构化的内容数据
- 适合程序化处理

### Markdown格式 (`.md`)
- 带标题和分类的格式
- 适合人工阅读和整理