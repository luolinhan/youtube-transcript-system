#!/usr/bin/env python3
"""
exporter.py - 导出 Notebook LLM 就绪文件
"""

import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent

class Exporter:
    
    def export_by_channel(self):
        """按频道导出"""
        db_path = BASE_DIR / "data/index.db"
        if not db_path.exists():
            print("数据库不存在")
            return
        
        db = sqlite3.connect(str(db_path))
        channels = db.execute(
            "SELECT DISTINCT channel FROM videos WHERE status = 'processed'"
        ).fetchall()
        
        export_dir = BASE_DIR / "data/exports/by_channel"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        for (channel,) in channels:
            rows = db.execute(
                """SELECT title, upload_date, file_path 
                   FROM videos WHERE channel = ? AND status = 'processed'
                   ORDER BY upload_date DESC""",
                (channel,)
            ).fetchall()
            
            if not rows:
                continue
            
            out_path = export_dir / f"{channel.replace(' ', '_')}.md"
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(f"# {channel} - 访谈字幕合集\n")
                f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d')}\n")
                f.write(f"共 {len(rows)} 期\n\n---\n\n")
                
                for title, date, file_path in rows:
                    content = Path(file_path).read_text(encoding='utf-8')
                    content = content.split('---\n\n', 2)[-1]
                    f.write(f"## {title}\n")
                    f.write(f"*{date}*\n\n")
                    f.write(content)
                    f.write("\n\n---\n\n")
            
            print(f"✅ 导出: {out_path} ({len(rows)} 期)")
    
    def export_mega_file(self):
        """导出全量合并文件"""
        db_path = BASE_DIR / "data/index.db"
        if not db_path.exists():
            print("数据库不存在")
            return
        
        db = sqlite3.connect(str(db_path))
        rows = db.execute(
            """SELECT title, channel, upload_date, file_path 
               FROM videos WHERE status = 'processed'
               ORDER BY channel, upload_date DESC"""
        ).fetchall()
        
        if not rows:
            print("没有已处理的视频")
            return
        
        export_dir = BASE_DIR / "data/exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        out_path = export_dir / f"ALL_TRANSCRIPTS_{datetime.now().strftime('%Y%m%d')}.md"
        
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(f"# YouTube 访谈字幕全量合集\n")
            f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"共 {len(rows)} 个视频\n\n---\n\n")
            
            for title, channel, date, file_path in rows:
                content = Path(file_path).read_text(encoding='utf-8').split('---\n\n', 2)[-1]
                f.write(f"## [{channel}] {title}\n*{date}*\n\n{content}\n\n---\n\n")
        
        size_mb = out_path.stat().st_size / 1024 / 1024
        print(f"✅ 全量导出: {out_path} ({size_mb:.1f} MB, {len(rows)} 个视频)")

def main():
    exp = Exporter()
    exp.export_by_channel()
    exp.export_mega_file()

if __name__ == "__main__":
    main()