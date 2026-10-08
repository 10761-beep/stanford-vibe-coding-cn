#!/usr/bin/env python3
"""
Stanford Vibe Coding 课程资料批量抓取脚本
用法: python fetch_course.py --config config/sources.yaml --output source/

功能:
  1. 按配置批量抓取课程页面
  2. 提取正文内容并保存为 Markdown
  3. 记录抓取日志（时间、URL、字数、状态）
  4. 支持断点续跑（已抓取的跳过）
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("请先安装依赖: pip install requests beautifulsoup4 pyyaml")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("请先安装 pyyaml: pip install pyyaml")
    sys.exit(1)


# ============================================================
# 配置加载
# ============================================================

DEFAULT_CONFIG = {
    "sources": [
        {
            "id": "cs146s-syllabus",
            "name": "CS146S The Modern Software Developer - 官方课程页",
            "url": "https://themodernsoftware.dev/",
            "type": "course_homepage",
            "output": "cs146s-syllabus.md",
        },
        {
            "id": "tech36b-syllabus",
            "name": "TECH 36 B Vibe Coding - 教学大纲 (Google Docs)",
            "url": "https://docs.google.com/document/d/1EzHq_IB7g06ToeBW399ZE7j-ECGq-dE3P7sMuYOpTEA/mobilebasic",
            "type": "google_doc",
            "output": "tech36b-syllabus.md",
        },
        {
            "id": "tech42-course-info",
            "name": "TECH 42 Vibe Coding - 课程介绍页",
            "url": "https://continuingstudies.stanford.edu/courses/detail/20261_TECH-42",
            "type": "course_detail",
            "output": "tech42-course-info.md",
        },
    ],
    "github_repos": [
        {
            "id": "cs146s-assignments",
            "name": "CS146S GitHub Assignments",
            "url": "https://github.com/mihail911/modern-software-dev-assignments",
            "description": "Weekly programming assignments for CS146S",
        }
    ],
    "request_delay_seconds": 2,
    "user_agent": "Mozilla/5.0 (compatible; CourseFetcher/1.0; Educational Use)",
}


def load_config(config_path: str = None) -> dict:
    """加载配置文件，若不存在则使用默认配置"""
    if config_path and os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return DEFAULT_CONFIG


# ============================================================
# 抓取逻辑
# ============================================================

def fetch_url(url: str, user_agent: str) -> str:
    """抓取 URL 内容，返回 HTML"""
    headers = {"User-Agent": user_agent}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def extract_text(html: str, source_type: str) -> str:
    """从 HTML 中提取正文，返回 Markdown 格式"""
    soup = BeautifulSoup(html, "html.parser")

    # 移除不需要的元素
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # 根据页面类型选择提取策略
    if source_type == "google_doc":
        # Google Docs mobilebasic 页面：直接取正文
        main = soup.find("div", {"id": "docs-primary"}) or soup.body
    elif source_type == "course_homepage":
        main = soup.find("main") or soup.body
    else:
        main = soup.find("main") or soup.find("article") or soup.body

    if not main:
        main = soup.body

    lines = []
    for elem in main.descendants:
        if elem.name == "h1":
            lines.append(f"\n# {elem.get_text(strip=True)}\n")
        elif elem.name == "h2":
            lines.append(f"\n## {elem.get_text(strip=True)}\n")
        elif elem.name == "h3":
            lines.append(f"\n### {elem.get_text(strip=True)}\n")
        elif elem.name == "li":
            lines.append(f"- {elem.get_text(strip=True)}")
        elif elem.name == "p":
            text = elem.get_text(strip=True)
            if text:
                lines.append(text)

    # 去重（descendants 会重复）
    seen = set()
    unique_lines = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)

    return "\n\n".join(unique_lines)


def save_markdown(content: str, output_path: str, source_url: str, source_id: str):
    """保存为 Markdown 文件，附带元信息头"""
    header = f"""# {source_id}

Source: {source_url}
Fetched at: {datetime.now().isoformat()}

---

"""
    full_content = header + content

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_content)


# ============================================================
# 主流程
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Stanford Vibe Coding 课程资料批量抓取")
    parser.add_argument("--config", default=None, help="配置文件路径 (YAML)")
    parser.add_argument("--output", default="source", help="输出目录")
    parser.add_argument("--force", action="store_true", help="强制重新抓取（跳过缓存）")
    args = parser.parse_args()

    config = load_config(args.config)
    sources = config["sources"]
    delay = config.get("request_delay_seconds", 2)
    ua = config.get("user_agent", "Mozilla/5.0")

    log = []
    success = 0
    skipped = 0
    failed = 0

    print(f"=== 开始抓取 {len(sources)} 个来源 ===\n")

    for i, source in enumerate(sources, 1):
        output_path = os.path.join(args.output, source["output"])

        # 断点续跑：已存在且非强制则跳过
        if os.path.exists(output_path) and not args.force:
            print(f"[{i}/{len(sources)}] 跳过（已存在）: {source['name']}")
            skipped += 1
            log.append({"id": source["id"], "status": "skipped", "output": output_path})
            continue

        print(f"[{i}/{len(sources)}] 抓取中: {source['name']}")
        print(f"  URL: {source['url']}")

        try:
            html = fetch_url(source["url"], ua)
            text = extract_text(html, source["type"])
            save_markdown(text, output_path, source["url"], source["id"])

            char_count = len(text)
            print(f"  ✅ 完成，{char_count} 字符 → {output_path}")
            success += 1
            log.append({
                "id": source["id"],
                "status": "success",
                "output": output_path,
                "chars": char_count,
            })
        except Exception as e:
            print(f"  ❌ 失败: {e}")
            failed += 1
            log.append({"id": source["id"], "status": "failed", "error": str(e)})

        # 请求间隔，礼貌抓取
        if i < len(sources):
            time.sleep(delay)

    # 输出抓取报告
    print(f"\n=== 抓取完成 ===")
    print(f"成功: {success} | 跳过: {skipped} | 失败: {failed}")
    print(f"输出目录: {os.path.abspath(args.output)}")

    # 保存抓取日志
    log_path = os.path.join(args.output, "_fetch_log.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump({
            "fetched_at": datetime.now().isoformat(),
            "summary": {"success": success, "skipped": skipped, "failed": failed},
            "details": log,
        }, f, ensure_ascii=False, indent=2)
    print(f"抓取日志: {log_path}")


if __name__ == "__main__":
    main()
