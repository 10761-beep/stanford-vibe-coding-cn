
# Stanford Vibe Coding 课程中文翻译站

> 斯坦福大学"氛围编程"（Vibe Coding）系列课程资料的全量中文翻译与归档项目

---

## 项目简介

本项目致力于系统获取、翻译并发布斯坦福大学开设的"氛围编程"（Vibe Coding）相关课程资料，面向中文学习者提供高质量的中译版本。

**覆盖课程：**

| 课程编号 | 课程名称 | 性质 | 学期 | 讲师 |
|----------|----------|------|------|------|
| CS146S | 现代软件开发者（The Modern Software Developer） | 斯坦福本科学分课 | 2025 秋 | Mihail Eric |
| TECH 36 B | 氛围编程：用 AI 学编程 | 继续教育学院 | 2026 秋 | Ray Villalobos |
| TECH 42 | 氛围编程：与 AI 对话构建软件 | 继续教育学院 | 2026 秋 | Elliott Adams |
| CS193V | 高效氛围编程（Effective Vibecoding） | 斯坦福本科学分课 | 秋季 | K. Schwarz |

---

## 目录结构

```
stanford-vibe-coding-cn/
├── README.md                   # 本文件：项目总览
├── glossary.md                 # 术语表（翻译一致性基准）
├── AI_LOG.md                   # AI 处理全流程日志（含 prompt 模板库）
├── AAR.md                      # 事后复盘（After Action Review，含量化自评）
├── USAGE.md                    # 拿来说明：下一批同学复用指南
├── source/                     # 原始英文资料归档
│   ├── cs146s-syllabus.md      # CS146S 官方教学大纲（英文原文）
│   ├── tech36b-syllabus.md     # TECH 36 B 教学大纲（英文原文）
│   └── tech42-course-info.md   # TECH 42 课程介绍（英文原文）
├── translated/                 # 中文翻译版本
│   ├── cs146s-syllabus-zh.md   # CS146S 教学大纲（中文翻译）
│   ├── tech36b-syllabus-zh.md  # TECH 36 B 教学大纲（中文翻译）
│   ├── tech42-course-info-zh.md # TECH 42 课程介绍（中文翻译）
│   ├── cs193t-overview-zh.md   # CS193T 课程概览（中文整理）
│   └── key-concepts-zh.md      # 核心概念深度解读（中文）
├── scripts/                    # 管线自动化脚本
│   ├── README.md               # 脚本使用说明
│   ├── fetch_course.py         # 课程资料批量抓取脚本
│   └── translate_pipeline.py   # 翻译管线工具（分段+prompt生成+术语校验）
├── config/                     # 管线配置
│   └── sources.yaml            # 抓取源配置（URL列表、GitHub仓库）
└── assets/                     # 图片、附件等资源
```

---

## 翻译流程

本项目采用 **"机器翻译 + 术语表 + 人工校对"** 的三段式管线，确保翻译质量可控：

```
原始资料抓取 → 分段处理 → AI 初译 → 术语对齐 → 人工抽检 → 终稿发布
     ↓              ↓          ↓          ↓          ↓          ↓
  source/        按章节     机器翻译   glossary   抽样校对   translated/
  归档保存       切分       生成初稿   统一校验   修正问题   中文发布
```

### 质量控制机制

1. **术语表前置**：翻译前先建立 `glossary.md`，统一核心术语译法
2. **分段处理**：长文档按周/章节切分，避免上下文丢失
3. **格式保持**：代码块、链接、表格结构完整保留，不破坏原文格式
4. **术语统一校验**：翻译完成后对照术语表检查一致性
5. **抽样人工校对**：每篇译文随机抽取 20% 内容进行人工复核

---

## 快速开始

### 在线阅读
直接浏览 `translated/` 目录下的中文翻译文档即可。

### 本地克隆
```bash
git clone https://github.com/your-org/stanford-vibe-coding-cn.git
cd stanford-vibe-coding-cn
```

### 继续翻译
参考 `USAGE.md`（拿来说明）了解如何贡献新的翻译内容。

---

## 核心概念速览

**Vibe Coding（氛围编程）**：一种以自然语言对话为主要编程方式的开发范式，开发者通过与 AI 对话来描述需求，由 AI 生成代码，人类负责引导方向和验证结果。

**Human-Agent Engineering（人-智能体工程）**：氛围编程的进阶形态——不是"随便说一句让 AI 写、出错了再让 AI 改"，而是像管理初级工程师一样管理 AI：提供清晰上下文、定义规范、验证产出、理解代码。

| | Vibe Coding | Human-Agent Engineering |
|---|---|---|
| 交互方式 | 粗略指令，结果照单全收 | 提供明确上下文与结构 |
| 错误处理 | 出错就重新提问 | 分析原因，定位问题，精准修正 |
| 代码理解 | 复制粘贴，不读代码 | 完全理解，能讲清每一行 |
| 适用场景 | 快速原型、个人项目 | 生产环境、团队协作 |

---

## 相关资源

- **CS146S 官网**：https://themodernsoftware.dev
- **CS146S GitHub 作业仓库**：https://github.com/mihail911/modern-software-dev-assignments
- **TECH 36 B 教学大纲**：Stanford Continuing Studies
- **TECH 42 课程页面**：https://continuingstudies.stanford.edu/courses/detail/20261_TECH-42

---

## 版权声明

本项目所有翻译内容仅供学习交流使用，原始课程资料版权归斯坦福大学及各位讲师所有。

如侵犯原作者权益，请联系删除。

---

## 参与贡献

欢迎提交 Issue 或 Pull Request 来改进翻译质量、补充遗漏内容。详见 `USAGE.md`。
