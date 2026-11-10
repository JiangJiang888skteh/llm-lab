# 🎓 电子信息学院华为产业学院智能顾问

> 一个基于 RAG（检索增强生成）技术的校园智能问答系统，让华为产业学院的学生随时随地了解学院信息。

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://cdjcc-eie-advisor.streamlit.app)

**👉 点击上面的按钮即可在线体验，无需安装任何东西！**

---

## 项目简介

本系统由成都锦城学院电子信息学院学生独立开发，将华为产业学院的官方文档（PDF、网页内容）构建成向量知识库，结合 DeepSeek 大语言模型实现智能问答。

**解决的问题**：学生想了解学院专业、师资、实验室、校友等信息时，不需要翻遍官网和文档，直接问"小锦"就行。

## 核心功能

- 📚 **智能问答**：基于学院真实文档回答，不编造信息
- 🎯 **知识库丰富**：涵盖华为创新班、5大实验室、54位教师、66+校友、67项获奖
- 💬 **自然对话**：吉祥物"小锦"以学长学姐口吻回答
- 🔍 **来源追溯**：问"依据是什么"时展示原文引用
- 🌐 **在线部署**：Streamlit Cloud 免费托管，手机电脑都能访问

## 技术架构

```
PDF/TXT 文档 → 文本分块 → 向量化(智谱embedding-3) → ChromaDB存储
                                                          ↓
用户提问 → 向量化 → 相似度检索 → 拼接上下文 → DeepSeek生成回答 → 展示
```

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| 大模型 | DeepSeek-chat | 生成自然语言回答 |
| 向量化 | 智谱 embedding-3 | 中文语义理解 |
| 向量数据库 | ChromaDB | 本地持久化存储 |
| Web 前端 | Streamlit | 快速搭建交互界面 |
| 文档解析 | pdfplumber | PDF → 纯文本 |
| 部署 | Streamlit Cloud | 免费在线托管 |

## 知识库内容

| 文档 | 内容 |
|------|------|
| 华为产业学院详情 | 学院概况、华为创新班、多功能中心九大区域、认证服务中心 |
| 师资队伍详情 | 54位教师详细资料（课程、研究方向、企业背景） |
| 实验室与获奖荣誉 | 5大建制实验室、10大专业实验室、67项竞赛获奖 |
| 优秀校友详情 | 66+位校友故事（华为/爱立信/移动/创业/读博） |
| 华为产业学院概况.pdf | 官方介绍文档 |
| 多功能中心.pdf | 九大功能区详细说明 |

## 项目结构

```
llm-lab/
├── data/                    # 知识库源文件
│   ├── *.pdf                # 官方PDF文档
│   ├── *.txt                # 网页抓取整理内容
│   └── chroma_db/           # 向量数据库（本地生成）
├── p1_rag/                  # RAG 核心代码
│   ├── load_pdf.py          # Step 1: 解析文档 → pages.json
│   ├── splitter.py          # Step 2: 文本分块
│   ├── store.py             # Step 3: 向量化 + 存入数据库
│   ├── rag.py               # Step 4: 检索 + 生成（命令行版）
│   ├── app.py               # Streamlit 网页应用
│   └── mascot.png           # 小锦头像
├── requirements.txt         # Python 依赖
├── .env                     # API 密钥（已 gitignore）
└── README.md
```

## 本地运行

```bash
# 1. 克隆项目
git clone https://github.com/JiangJiang888skteh/llm-lab.git
cd llm-lab

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API 密钥（在项目根目录创建 .env 文件）
#    DEEPSEEK_API_KEY=sk-xxx
#    ZHIPU_API_KEY=xxx

# 4. 构建知识库
python p1_rag/load_pdf.py
python p1_rag/store.py

# 5. 启动应用
streamlit run p1_rag/app.py
```

## 作者

**成都锦城学院 · 电子信息学院 · 智能科学与技术专业**

本项目为华为产业学院实验室申请作品。
