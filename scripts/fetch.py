#!/usr/bin/env python3
"""
fetch.py - 高质量字幕抓取器
策略：精选信源 + 质量过滤 + 人工字幕优先
"""

import json
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Tuple

BASE_DIR = Path(__file__).parent.parent

@dataclass
class VideoMeta:
    video_id: str
    title: str
    channel: str
    channel_id: str
    upload_date: str
    duration: int
    view_count: int
    has_manual_sub: bool
    has_auto_sub: bool
    sub_langs: list
    url: str

class QualityFilter:
    """视频质量过滤器"""
    
    def __init__(self, settings: dict):
        self.min_duration = settings.get("min_duration_seconds", 1200)
        self.max_duration = settings.get("max_duration_seconds", 18000)
        self.min_views = settings.get("min_view_count", 5000)
        self.prefer_manual = settings.get("prefer_manual_sub", True)
    
    def is_quality(self, meta: VideoMeta) -> Tuple[bool, str]:
        """返回 (通过, 原因)"""
        if meta.duration < self.min_duration:
            return False, f"视频太短 {meta.duration//60}min < {self.min_duration//60}min"
        if meta.duration > self.max_duration:
            return False, f"视频太长 {meta.duration//60}min"
        if not meta.has_manual_sub and not meta.has_auto_sub:
            return False, "无字幕"
        if meta.view_count < self.min_views:
            return False, f"播放量太低 {meta.view_count:,}"
        return True, "通过"

class SubtitleFetcher:
    
    def __init__(self):
        self.config = self._load_config()
        self.db = self._init_db()
        self.filter = QualityFilter(self.config["settings"].get("quality_filter", {}))
    
    def _load_config(self):
        return {
            "sources": json.loads((BASE_DIR / "config/sources.json").read_text()),
            "targets": json.loads((BASE_DIR / "config/targets.json").read_text()),
            "settings": json.loads((BASE_DIR / "config/settings.json").read_text()),
        }
    
    def _init_db(self):
        """初始化 SQLite 元数据库"""
        db_path = BASE_DIR / "data/index.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                video_id TEXT PRIMARY KEY,
                title TEXT,
                channel TEXT,
                channel_id TEXT,
                upload_date TEXT,
                duration INTEGER,
                view_count INTEGER,
                has_manual_sub BOOLEAN,
                has_auto_sub BOOLEAN,
                sub_langs TEXT,
                status TEXT DEFAULT 'pending',
                reason TEXT,
                fetched_at TEXT,
                file_path TEXT,
                sub_type TEXT
            )
        """)
        conn.commit()
        return conn
    
    def is_already_fetched(self, video_id: str) -> bool:
        """检查是否已抓取（去重）"""
        row = self.db.execute(
            "SELECT status FROM videos WHERE video_id = ?", (video_id,)
        ).fetchone()
        return row is not None
    
    def get_channel_videos(self, channel_id: str, max_count: int = 50) -> list:
        """获取频道视频列表及元数据"""
        cmd = [
            "yt-dlp",
            "--flat-playlist",
            "--print", "%(id)s|%(title)s|%(upload_date)s|%(duration)s|%(view_count)s|%(subtitles)s|%(automatic_captions)s",
            "--playlist-end", str(max_count),
            f"https://www.youtube.com/channel/{channel_id}/videos"
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        videos = []
        for line in result.stdout.strip().split('\n'):
            if not line or '|' not in line:
                continue
            try:
                parts = line.split('|')
                if len(parts) < 7:
                    continue
                vid_id, title, date, duration, views, subs, auto_subs = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6]
                has_manual = subs != 'NA' and subs != '{}'
                has_auto = auto_subs != 'NA' and auto_subs != '{}'
                videos.append(VideoMeta(
                    video_id=vid_id,
                    title=title,
                    channel="",
                    channel_id=channel_id,
                    upload_date=date or "20200101",
                    duration=int(duration) if duration and duration.isdigit() else 0,
                    view_count=int(views) if views and views.isdigit() else 0,
                    has_manual_sub=has_manual,
                    has_auto_sub=has_auto,
                    sub_langs=[],
                    url=f"https://www.youtube.com/watch?v={vid_id}"
                ))
            except Exception as e:
                print(f"解析行失败: {e}, line: {line[:100]}")
                continue
        return videos
    
    def fetch_subtitle(self, meta: VideoMeta) -> Tuple[Optional[Path], Optional[str]]:
        """
        下载字幕，优先级：人工字幕(en) > 自动字幕(en)
        """
        out_dir = BASE_DIR / "data/raw" / meta.channel_id
        out_dir.mkdir(parents=True, exist_ok=True)
        out_tmpl = str(out_dir / f"{meta.video_id}.%(ext)s")
        
        # 优先人工字幕
        cmd = [
            "yt-dlp",
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs", "en,zh-Hans,zh-Hant,zh",
            "--sub-format", "vtt",
            "--skip-download",
            "--no-playlist",
            "--output", out_tmpl,
            meta.url
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        # 找到下载的字幕文件，优先人工字幕
        for lang in ["en", "zh-Hans", "zh-Hant", "zh"]:
            manual = out_dir / f"{meta.video_id}.{lang}.vtt"
            if manual.exists():
                return manual, "manual"
            auto = out_dir / f"{meta.video_id}.{lang}.auto.vtt"
            if auto.exists():
                return auto, "auto"
        
        return None, None
    
    def _save_status(self, meta: VideoMeta, status: str, reason: str, file_path: str = None, sub_type: str = None):
        self.db.execute("""
            INSERT OR REPLACE INTO videos 
            (video_id, title, channel, channel_id, upload_date, duration, 
             view_count, has_manual_sub, has_auto_sub, status, reason, fetched_at, file_path, sub_type)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            meta.video_id, meta.title, meta.channel, meta.channel_id,
            meta.upload_date, meta.duration, meta.view_count, meta.has_manual_sub, meta.has_auto_sub,
            status, reason, datetime.now().isoformat(), file_path, sub_type
        ))
        self.db.commit()
    
    def run(self):
        """主运行逻辑"""
        sources = self.config["sources"]
        settings = self.config["settings"]
        
        for channel in sources.get("channels", []):
            print(f"\n📺 处理频道: {channel['name']}")
            max_count = settings.get("fetch", {}).get("max_videos_per_channel", 30)
            
            videos = self.get_channel_videos(channel["id"], max_count)
            print(f"   获取到 {len(videos)} 个视频")
            
            fetched = 0
            for meta in videos:
                meta.channel = channel["name"]
                
                # 去重
                if self.is_already_fetched(meta.video_id):
                    print(f"   ⏭  已存在: {meta.title[:50]}")
                    continue
                
                # 质量过滤
                passed, reason = self.filter.is_quality(meta)
                if not passed:
                    print(f"   ❌ 过滤: {meta.title[:40]} ({reason})")
                    self._save_status(meta, "skipped", reason)
                    continue
                
                # 下载字幕
                print(f"   ⬇  下载: {meta.title[:50]}")
                vtt_path, sub_type = self.fetch_subtitle(meta)
                
                if vtt_path:
                    print(f"   ✅ 成功 [{sub_type}]: {vtt_path.name}")
                    self._save_status(meta, "fetched", sub_type, str(vtt_path), sub_type)
                    fetched += 1
                else:
                    print(f"   ⚠  无字幕: {meta.title[:50]}")
                    self._save_status(meta, "failed", "no_subtitle")
                
                time.sleep(1)  # 避免请求过快
            
            print(f"   本频道完成: {fetched} 个视频")

def main():
    SubtitleFetcher().run()

if __name__ == "__main__":
    main()