# AI文档大纲生成系统

本项目是一个基于Gradio+Dify的AI文档大纲/知识图谱生成工具，支持上传资料、自动提取文本、AI生成/修改大纲、对话问答、历史会话管理等功能。适用于学习资料整理、知识梳理、文档结构化等场景。

## 主要功能

- 支持多种格式文件上传并自动提取文本
- AI自动生成资料大纲，支持自然语言修改
- 聊天对话，结合资料内容智能问答
- 会话历史自动保存，支持多会话切换与管理
- 大纲和资料可手动编辑并应用
- 支持刷新页面后自动加载最新历史记录

## 安装与运行

### 1. 克隆项目

```bash
git clone <仓库地址>
cd Mind Map Generator
```
### 2. 建立环境

为了避免依赖冲突，可以设置独立的虚拟环境

```
python -m venv venv
# Windows 激活
venv\Scripts\activate
# macOS/Linux 激活
source venv/bin/activate
```

### 3. 安装依赖

建议使用 Python 3.8+，推荐虚拟环境。

```bash
pip install -r requirements.txt
```

### 4. 启动服务

```bash
python web/app.py
```

默认会在 `http://localhost:7861` 启动Web界面。

## 目录结构

```
Mind Map Generator/
├── app/                # 核心后端逻辑
│   ├── chatting.py     # AI对话逻辑
│   ├── data_tracer.py  # 会话与历史管理
│   ├── structure_identifier_prompt.py # 大纲生成/修改
│   └── ...
├── web/                # Web界面与交互
│   ├── app.py          # Gradio主入口
│   └── ...
├── log/                # 会话历史与数据存储
├── requirements.txt    # Python依赖
└── README.md
```

## 常见问题

- **Q: 上传文件后没有内容？**  
  A: 请确认文件格式支持，或检查提取文本功能是否报错。

- **Q: 刷新页面后历史记录丢失？**  
  A: 已修复，刷新会自动加载最新历史。

- **Q: AI大纲生成失败？**  
  A: 检查网络连接，或API Key是否有效。

## known issue

前端显示问题：

1. 仅有一次历史会话时左侧的按钮宽度错误
2. 聊天框高度错误

后端处理缺陷：

1. 只能识别文字，支持pptx,doc,md,pdf
2. 询问耗时高
