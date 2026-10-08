#!/usr/bin/env python3
"""
Stanford Vibe Coding 课程资料翻译管线脚本
用法: python translate_pipeline.py --input source/cs146s-syllabus.md --output translated/cs146s-syllabus-zh.md

功能:
  1. 读取英文原文，按章节切分（分段处理长文本）
  2. 加载术语表，生成翻译 prompt 模板
  3. 输出待翻译的分段文件 + 翻译指令（供 AI 批量处理）
  4. 翻译完成后做术语一致性校验

注意: 本脚本不直接调用 AI API，而是生成结构化的翻译任务包，
      配合 AI 工具（如 Claude / ChatGPT / 豆包）批量执行翻译。
"""

import argparse
import json
import os
import re
from pathlib import Path


# ============================================================
# 术语表加载
# ============================================================

def load_glossary(glossary_path: str) -> dict:
    """从 glossary.md 提取术语对照表，返回 {英文: 中文} 字典"""
    glossary = {}
    if not os.path.exists(glossary_path):
        return glossary

    with open(glossary_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 匹配 Markdown 表格行: | 英文 | 中文 | ...
    # 跳过表头和分隔线
    for line in content.split("\n"):
        line = line.strip()
        if not line.startswith("|"):
            continue
        if "---" in line or "英文" in line and "中文" in line:
            continue

        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) >= 2 and cells[0] and cells[1]:
            eng = cells[0]
            chn = cells[1]
            # 跳过工具名表（第二列是"说明"而非翻译）
            if eng and chn and not chn.startswith("AI") and "IDE" not in chn:
                glossary[eng] = chn

    return glossary


# ============================================================
# 分段逻辑
# ============================================================

def split_by_sections(text: str, max_chars: int = 3000) -> list:
    """
    按章节标题切分长文本为若干段。
    若某段超过 max_chars，进一步按段落切分。
    """
    # 按 ## 二级标题切分
    sections = re.split(r"\n(?=## )", text)

    chunks = []
    current_chunk = ""

    for section in sections:
        if len(section) > max_chars:
            # 超大段再按 ### 三级标题切分
            subsections = re.split(r"\n(?=### )", section)
            for sub in subsections:
                if len(current_chunk) + len(sub) > max_chars and current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = sub
                else:
                    current_chunk += sub
        else:
            if len(current_chunk) + len(section) > max_chars and current_chunk:
                chunks.append(current_chunk)
                current_chunk = section
            else:
                current_chunk += section

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


# ============================================================
# 翻译 prompt 生成
# ============================================================

def build_translation_prompt(chunk: str, glossary: dict, chunk_index: int, total_chunks: int) -> str:
    """为每个分段生成翻译指令 prompt"""

    # 术语表 Top 20 高频术语
    glossary_lines = []
    for eng, chn in list(glossary.items())[:25]:
        glossary_lines.append(f"  - {eng} → {chn}")
    glossary_text = "\n".join(glossary_lines)

    prompt = f"""你是一位专业的技术翻译。请将以下英文内容翻译为简体中文。

## 翻译规则（必须严格遵守）

1. **术语一致性**：以下术语必须使用指定译法，不得自创：
{glossary_text}

2. **保留原文**：
   - 工具/产品名（如 Cursor, Claude Code, GitHub, Warp, v0, Bolt.new 等）保留英文
   - 代码块、命令行、配置文件内容保持英文，不翻译
   - URL 链接保持原文
   - 缩写（如 LLM, MCP, RAG, SAST, DAST, API, SDK, PRD, MVP）保留英文，首次出现可附中文全称

3. **格式保持**：
   - 标题层级（# / ## / ###）与原文保持一致
   - 列表、表格结构完整保留
   - 不添加原文没有的内容，不省略原文内容

4. **风格要求**：
   - 技术文档风格，准确、简洁、专业
   - 符合中文技术社区的表达习惯
   - 不使用机器翻译腔

## 待翻译内容（第 {chunk_index}/{total_chunks} 段）：

---

{chunk}

---

请直接输出翻译后的中文内容，不要添加额外说明。
"""
    return prompt


# ============================================================
# 术语校验
# ============================================================

def check_glossary_consistency(translated_text: str, glossary: dict) -> list:
    """检查译文中的术语一致性，返回问题列表"""
    issues = []

    for eng, expected_chn in glossary.items():
        # 如果英文术语还出现在译文中（应该被翻译的地方），标记为问题
        # 排除：代码块内、工具名表
        # 简单检查：英文术语是否单独出现（不在代码块、不在URL中）
        pattern = r"\b" + re.escape(eng) + r"\b"
        matches = re.findall(pattern, translated_text)
        if matches and len(matches) > 0:
            # 检查这个术语是不是工具名（应该保留英文的）
            tool_names = {"Cursor", "Claude Code", "GitHub", "Warp", "v0", "Bolt.new",
                         "Lovable", "Replit", "Semgrep", "Graphite", "Devin", "Ollama",
                         "MVPunk", "VibeIt", "Google AI Studio", "Cognition"}
            if eng not in tool_names and expected_chn not in translated_text:
                issues.append(f"术语 '{eng}' 未翻译为 '{expected_chn}'，出现 {len(matches)} 次")

    return issues


# ============================================================
# 主流程
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Stanford Vibe Coding 翻译管线工具")
    parser.add_argument("--input", required=True, help="输入英文 Markdown 文件路径")
    parser.add_argument("--output", required=True, help="输出中文 Markdown 文件路径")
    parser.add_argument("--glossary", default="glossary.md", help="术语表路径")
    parser.add_argument("--max-chars", type=int, default=3000, help="每段最大字符数")
    parser.add_argument("--task-dir", default="translation_tasks", help="翻译任务输出目录")
    parser.add_argument("--check-only", action="store_true", help="仅做术语一致性校验")
    args = parser.parse_args()

    # 加载原文
    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    # 加载术语表
    glossary = load_glossary(args.glossary)
    print(f"术语表加载: {len(glossary)} 条术语")

    if args.check_only:
        # 校验模式
        with open(args.output, "r", encoding="utf-8") as f:
            translated = f.read()
        issues = check_glossary_consistency(translated, glossary)
        if issues:
            print(f"⚠️ 发现 {len(issues)} 个术语一致性问题:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ 术语一致性检查通过")
        return

    # 分段
    chunks = split_by_sections(text, args.max_chars)
    print(f"分段完成: {len(chunks)} 段")
    for i, chunk in enumerate(chunks, 1):
        print(f"  段 {i}: {len(chunk)} 字符")

    # 生成翻译任务包
    os.makedirs(args.task_dir, exist_ok=True)
    base_name = Path(args.input).stem

    task_manifest = {
        "input_file": args.input,
        "output_file": args.output,
        "total_chunks": len(chunks),
        "chunks": [],
    }

    for i, chunk in enumerate(chunks, 1):
        prompt = build_translation_prompt(chunk, glossary, i, len(chunks))
        task_file = os.path.join(args.task_dir, f"{base_name}_chunk_{i:02d}.md")

        with open(task_file, "w", encoding="utf-8") as f:
            f.write(prompt)

        task_manifest["chunks"].append({
            "index": i,
            "file": task_file,
            "chars": len(chunk),
            "status": "pending",
        })
        print(f"  生成任务: {task_file}")

    # 保存任务清单
    manifest_path = os.path.join(args.task_dir, f"{base_name}_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(task_manifest, f, ensure_ascii=False, indent=2)

    print(f"\n=== 翻译任务包已生成 ===")
    print(f"任务目录: {os.path.abspath(args.task_dir)}")
    print(f"任务清单: {manifest_path}")
    print(f"\n下一步: 用 AI 工具逐个处理 chunk 文件，翻译完成后合并为 {args.output}")
    print(f"校验: python translate_pipeline.py --input {args.input} --output {args.output} --check-only")


if __name__ == "__main__":
    main()
