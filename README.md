# 电子信息学院华为产业学院智能顾问

成都锦城学院电子信息学院 RAG 智能问答系统，基于华为产业学院官方文档构建知识库。

## 在线体验

https://cdjcc-eie-advisor.streamlit.app

## 功能

- 基于 RAG 架构的智能问答（检索增强生成）
- 知识库涵盖：华为产业学院概况、师资队伍、实验室、优秀校友、获奖荣誉
- 莫兰迪蓝色系界面，吉祥物"小锦"对话体验
- 支持按需查看参考来源

## 技术栈

| 组件 | 技术 |
|------|------|
| 大模型 | DeepSeek (deepseek-chat) |
| 向量化 | 智谱 AI (embedding-3) |
| 向量数据库 | ChromaDB |
| 前端 | Streamlit |
| PDF解析 | pdfplumber |

## 项目结构

```
llm-lab/
├── data/              # 知识库源文件（PDF + TXT）
├── p1_rag/
│   ├── load_pdf.py    # 解析 PDF 和 TXT 文件
│   ├── splitter.py    # 文本分块
│   ├── store.py       # 向量化 + 存入 ChromaDB
│   ├── rag.py         # RAG 核心逻辑（CLI版）
│   ├── app.py         # Streamlit 网页应用
│   └── mascot.png     # 小锦头像
├── requirements.txt
└── .env               # API 密钥（不提交）
```

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量（创建 .env 文件）
# DEEPSEEK_API_KEY=your_key
# ZHIPU_API_KEY=your_key

# 构建知识库
python p1_rag/load_pdf.py
python p1_rag/store.py

# 启动应用
streamlit run p1_rag/app.py
```

## 作者

成都锦城学院 电子信息学院 智能科学与技术专业
