#!/usr/bin/env python3
"""
YouTube Transcript System - 核心检索脚本
支持按频道、关键词、主题检索视频并提取字幕
"""

import json
import os
import subprocess
import sys
from datetime import datetime

class YouTubeScraper:
    def __init__(self, config_dir="config", data_dir="data"):
        self.config_dir = config_dir
        self.data_dir = data_dir
        self.channels_config = self.load_config("channels.json")
        self.keywords_config = self.load_config("search_keywords.json")
        self.settings = self.load_config("system_settings.json")
        
    def load_config(self, filename):
        """加载配置文件"""
        config_path = os.path.join(self.config_dir, filename)
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def search_videos(self, query, max_results=10):
        """搜索YouTube视频"""
        try:
            cmd = [
                sys.executable, "-m", "yt_dlp",
                "--flat-playlist",
                "--print", "id,title,upload_date",
                f"ytsearch{max_results}:{query}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            videos = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        videos.append({
                            'id': parts[0],
                            'title': parts[1],
                            'upload_date': parts[2]
                        })
            return videos
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
    
    def extract_subtitle(self, video_id, output_dir):
        """提取单个视频字幕"""
        try:
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 提取VTT字幕
            cmd = [
                sys.executable, "-m", "yt_dlp",
                "--write-subs",
                "--sub-lang", self.settings.get("subtitle_preferences", {}).get("language", "en"),
                "--sub-format", "vtt",
                "--output", f"{output_dir}/{video_id}.%(ext)s",
                f"https://www.youtube.com/watch?v={video_id}"
            ]
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            vtt_file = os.path.join(output_dir, f"{video_id}.en.vtt")
            if os.path.exists(vtt_file):
                return vtt_file
            return None
            
        except Exception as e:
            print(f"提取字幕失败 {video_id}: {e}")
            return None
    
    def process_personality(self, personality_name):
        """处理特定人物的所有相关内容"""
        print(f"处理 {personality_name} 的内容...")
        
        # 构建搜索查询
        queries = []
        base_query = personality_name
        
        # 添加主题关键词
        topics = self.keywords_config.get("topics", {})
        for topic_name, keywords in topics.items():
            for keyword in keywords:
                queries.append(f"{base_query} {keyword}")
        
        # 添加内容类型关键词
        content_types = self.keywords_config.get("content_types", [])
        for content_type in content_types:
            queries.append(f"{base_query} {content_type}")
        
        # 执行搜索和字幕提取
        all_videos = []
        for query in queries[:5]:  # 限制查询数量避免重复
            videos = self.search_videos(query, max_results=5)
            all_videos.extend(videos)
        
        # 去重
        seen_ids = set()
        unique_videos = []
        for video in all_videos:
            if video['id'] not in seen_ids:
                seen_ids.add(video['id'])
                unique_videos.append(video)
        
        # 提取字幕
        raw_subtitles_dir = os.path.join(self.data_dir, "raw", "vtt_subtitles")
        processed_dir = os.path.join(self.data_dir, "processed", "clean_text")
        
        for video in unique_videos[:self.settings.get("auto_update", {}).get("max_videos_per_run", 10)]:
            print(f"提取字幕: {video['title']}")
            vtt_file = self.extract_subtitle(video['id'], raw_subtitles_dir)
            if vtt_file:
                # 转换为纯文本
                self.convert_vtt_to_txt(vtt_file, processed_dir, video)
    
    def convert_vtt_to_txt(self, vtt_file, output_dir, video_info):
        """将VTT转换为纯文本"""
        try:
            with open(vtt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单的VTT清理（实际项目中需要更复杂的处理）
            lines = content.split('\n')
            clean_lines = []
            for line in lines:
                if not line.strip().startswith(('WEBVTT', 'Kind:', 'Language:', '-->')) and line.strip():
                    # 移除时间戳和格式标记
                    if '-->' not in line and not line.replace(' ', '').replace('\t', '').isdigit():
                        clean_lines.append(line.strip())
            
            # 保存纯文本
            txt_filename = f"{video_info['id']}.txt"
            txt_path = os.path.join(output_dir, txt_filename)
            os.makedirs(output_dir, exist_ok=True)
            
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f"# {video_info['title']}\n")
                f.write(f"Video ID: {video_info['id']}\n")
                f.write(f"Upload Date: {video_info['upload_date']}\n\n")
                f.write('\n'.join(clean_lines))
            
            print(f"已保存纯文本: {txt_path}")
            
        except Exception as e:
            print(f"转换失败 {vtt_file}: {e}")

def main():
    scraper = YouTubeScraper()
    
    # 处理配置中的人物
    personalities = scraper.keywords_config.get("personalities", [])
    for personality in personalities:
        scraper.process_personality(personality)
    
    print("字幕提取完成！")

if __name__ == "__main__":
    main()