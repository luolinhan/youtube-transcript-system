#!/usr/bin/env python3
"""
processor.py - 高质量 VTT 清洗器
目标：输出干净、连贯、适合 LLM 阅读的纯文本
"""

import re
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

class VTTProcessor:
    
    def clean_vtt(self, vtt_path: Path) -> str:
        """
        将 VTT 转为干净文本
        """
        content = vtt_path.read_text(encoding='utf-8', errors='ignore')
        
        # 1. 移除 WEBVTT 头
        content = re.sub(r'^WEBVTT.*?\n\n', '', content, flags=re.DOTALL)
        
        # 2. 移除时间戳行
        content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}.*\n', '', content)
        
        # 3. 移除序号行
        content = re.sub(r'^\d+\n', '', content, flags=re.MULTILINE)
        
        # 4. 移除 HTML 标签
        content = re.sub(r'<[^>]+>', '', content)
        
        # 5. 移除时间内嵌标记
        content = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', content)
        
        # 6. 按行处理，去除空行和重复
        lines = []
        seen = set()
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
            # 去重
            if line in seen:
                continue
            recent = lines[-5:] if len(lines) >= 5 else lines
            if line in recent:
                continue
            lines.append(line)
            seen.add(line)
        
        # 7. 合并成段落
        paragraphs = []
        current = []
        for line in lines:
            current.append(line)
            if line.endswith(('.', '?', '!', '。', '？', '！')) and len(' '.join(current)) > 200:
                paragraphs.append(' '.join(current))
                current = []
        if current:
            paragraphs.append(' '.join(current))
        
        return '\n\n'.join(paragraphs)
    
    def process_all_pending(self):
        """处理所有已抓取但未处理的字幕"""
        db_path = BASE_DIR / "data/index.db"
        if not db_path.exists():
            print("数据库不存在，请先运行 fetch.py")
            return
        
        db = sqlite3.connect(str(db_path))
        rows = db.execute(
            "SELECT video_id, title, channel, upload_date, file_path FROM videos WHERE status = 'fetched'"
        ).fetchall()
        
        print(f"找到 {len(rows)} 个待处理视频")
        
        for video_id, title, channel, upload_date, vtt_path_str in rows:
            vtt_path = Path(vtt_path_str)
            if not vtt_path.exists():
                print(f"文件不存在: {vtt_path}")
                continue
            
            out_dir = BASE_DIR / "data/processed" / channel.replace(' ', '_')
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{video_id}.txt"
            
            print(f"🔧 处理: {title[:60]}")
            clean_text = self.clean_vtt(vtt_path)
            
            # 写入带元数据头的文本
            header = f"""---
title: {title}
video_id: {video_id}
channel: {channel}
upload_date: {upload_date}
source_url: https://www.youtube.com/watch?v={video_id}
---

"""
            out_path.write_text(header + clean_text, encoding='utf-8')
            
            db.execute(
                "UPDATE videos SET status = 'processed', file_path = ? WHERE video_id = ?",
                (str(out_path), video_id)
            )
            db.commit()
            print(f"   ✅ 已保存: {out_path}")

def main():
    VTTProcessor().process_all_pending()

if __name__ == "__main__":
    main()