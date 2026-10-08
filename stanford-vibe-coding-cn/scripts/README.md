# 管线脚本使用说明

本目录包含信息获取与翻译管线的自动化脚本，可复跑、可复用。

## 目录结构

```
scripts/
├── fetch_course.py        # 课程资料批量抓取脚本
└── translate_pipeline.py  # 翻译管线工具（分段 + prompt 生成 + 术语校验）

config/
└── sources.yaml           # 抓取源配置（URL 列表、GitHub 仓库）
```

## 快速开始

### 1. 安装依赖

```bash
pip install requests beautifulsoup4 pyyaml
```

### 2. 批量抓取课程资料

```bash
# 使用默认配置抓取
python scripts/fetch_course.py --output source/

# 使用自定义配置
python scripts/fetch_course.py --config config/sources.yaml --output source/

# 强制重新抓取（覆盖已有文件）
python scripts/fetch_course.py --force --output source/
```

**输出：**
- `source/` 目录下生成每个来源的 Markdown 文件
- `source/_fetch_log.json` 抓取日志（成功/跳过/失败统计）

### 3. 生成翻译任务包

```bash
# 对一篇英文原文生成分段翻译任务
python scripts/translate_pipeline.py \
  --input source/cs146s-syllabus.md \
  --output translated/cs146s-syllabus-zh.md \
  --glossary glossary.md
```

**输出：**
- `translation_tasks/cs146s-syllabus_chunk_01.md` 等分段翻译指令
- `translation_tasks/cs146s-syllabus_manifest.json` 任务清单

### 4. 执行翻译

将每个 chunk 文件的内容（包含 prompt + 待翻译原文）发给 AI 工具（豆包/Claude/ChatGPT），获取翻译结果。

### 5. 合并 + 校验

```bash
# 合并所有翻译片段为完整中文文档（手动或脚本辅助）
# 然后做术语一致性校验：
python scripts/translate_pipeline.py \
  --input source/cs146s-syllabus.md \
  --output translated/cs146s-syllabus-zh.md \
  --check-only
```

## 管线流程图

```
config/sources.yaml
       ↓
 fetch_course.py ──→ source/*.md（英文原文归档）
       ↓
 translate_pipeline.py ──→ translation_tasks/*.md（分段翻译任务包）
       ↓
   AI 批量翻译（人工/AI 执行）
       ↓
 合并 + --check-only 校验
       ↓
 translated/*-zh.md（中文翻译终稿）
```

## 复用到其他课程

1. 复制 `config/sources.yaml`，替换为新课程的 URL 列表
2. 运行 `fetch_course.py` 抓取
3. 运行 `translate_pipeline.py` 生成分段任务
4. 翻译 → 合并 → 校验
5. 完成

整个管线不需要修改脚本本身，只需要改配置文件。

---

## 真实运行记录

以下是在本机实际运行的输出记录（非虚构）：

### translate_pipeline.py 生成任务包

```
$ python3 scripts/translate_pipeline.py --input source/cs146s-syllabus.md --output translated/cs146s-syllabus-zh.md --glossary glossary.md --task-dir translation_tasks

术语表加载: 46 条术语
分段完成: 3 段
  段 1: 2739 字符
  段 2: 2659 字符
  段 3: 1002 字符
  生成任务: translation_tasks/cs146s-syllabus_chunk_01.md
  生成任务: translation_tasks/cs146s-syllabus_chunk_02.md
  生成任务: translation_tasks/cs146s-syllabus_chunk_03.md

=== 翻译任务包已生成 ===
任务目录: translation_tasks
任务清单: translation_tasks/cs146s-syllabus_manifest.json
```

### translate_pipeline.py 术语校验

```
$ python3 scripts/translate_pipeline.py --input source/cs146s-syllabus.md --output translated/cs146s-syllabus-zh.md --glossary glossary.md --check-only

术语表加载: 46 条术语
⚠️ 发现 4 个术语一致性问题:
  - 术语 'SAST' 未翻译为 '静态应用安全测试'，出现 2 次
  - 术语 'DAST' 未翻译为 '动态应用安全测试'，出现 2 次
  - 术语 'DevOps' 未翻译为 '开发运维一体化'，出现 1 次
  - 术语 'GitHub Copilot' 未翻译为 'GitHub 的 AI 编程助手'，出现 2 次
```

> 注：这些"问题"实际上是翻译时有意保留了英文缩写（技术文档惯例），
> 校验脚本的作用是提醒人工复核，而不是强制要求全部翻译。
