# YouTube Transcript System v2

高质量 YouTube 访谈/播客字幕提取系统，专为 Notebook LLM 知识库构建。

## 🎯 核心特性

- **精选信源** - 直接订阅顶级频道（Lex Fridman、YC、All-In 等），非关键词搜索
- **质量过滤** - 自动过滤短视频、低播放量、无字幕内容
- **人工字幕优先** - 优先下载人工校对字幕，自动字幕作为备选
- **智能去重** - SQLite 数据库追踪状态，避免重复抓取
- **VTT 清洗** - 去除时间戳、HTML 标签、重复行，输出干净文本
- **Notebook 就绪** - 导出 Markdown 格式，直接拖入 Notebook LLM

## 📁 项目结构

```
youtube-transcript-system/
├── config/
│   ├── sources.json          # 精选频道配置
│   ├── targets.json          # 目标人物
│   └── settings.json         # 系统设置
├── scripts/
│   ├── fetch.py              # 主抓取器
│   ├── processor.py          # VTT 清洗器
│   └── exporter.py           # 导出器
├── data/
│   ├── raw/                  # 原始 VTT 字幕
│   ├── processed/            # 清洗后文本
│   ├── exports/              # Notebook-ready 导出
│   └── index.db              # SQLite 状态数据库
└── README.md
```

## ⚙️ 安装

```bash
pip3 install yt-dlp webvtt-py tqdm
```

## 🚀 使用

### 1. 配置信源
编辑 `config/sources.json` 添加目标频道。

### 2. 抓取字幕
```bash
cd youtube-transcript-system
python3 scripts/fetch.py
```

### 3. 处理字幕
```bash
python3 scripts/processor.py
```

### 4. 导出 Notebook 文件
```bash
python3 scripts/exporter.py
```

输出文件位于 `data/exports/`。

## 📊 质量过滤规则

- 视频时长：20分钟 ~ 5小时
- 最低播放量：5,000
- 字幕类型：人工字幕优先，自动字幕备选
- 去重：已抓取视频自动跳过

## 📝 License

MIT