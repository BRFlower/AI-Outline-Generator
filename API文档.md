# AI Outline Generator API 文档

本项目提供了文档内容提取、结构识别、会话管理等核心API，便于开发者集成和二次开发。

## 1. 文本提取相关

### extract_text_from_file

- **位置**：`app/text_extractor.py`
- **功能**：通过大模型接口提取文件主要内容，支持多种格式。
- **参数**：
  - `filepath` (str)：文件路径
  - `api_key` (str, 可选)：API密钥，默认内置
  - `user` (str, 可选)：用户名，默认 "noob"
- **返回**：`List[str]`，提取出的文本内容（流式输出）
- **示例**：
  ```python
  from app.text_extractor import extract_text_from_file
  result = extract_text_from_file("example.docx")
  print("".join(result))
  ```

### extract_text_traditional

- **位置**：`app/text_extractor.py`
- **功能**：使用传统方法提取文件文本内容，支持 txt, md, docx, pptx, pdf 等格式。
- **参数**：
  - `filepath` (str)：文件路径
- **返回**：`List[str]`，提取出的文本内容
- **示例**：
  ```python
  from app.text_extractor import extract_text_traditional
  result = extract_text_traditional("example.txt")
  print("".join(result))
  ```
---

## 2. 结构识别相关

### identify_structure

- **位置**：`app/structure_identifier_prompt.py`
- **功能**：对输入文本生成知识点大纲（流式输出）。
- **参数**：
  - `text` (str)：输入文本
  - `api_key` (str, 可选)：API密钥
  - `user` (str, 可选)：用户名
- **返回**：`List[str]`，大纲内容（流式输出）
- **示例**：
  ```python
  from app.structure_identifier import identify_structure
  outline = identify_structure("输入的文档内容")
  print("".join(outline))
  ```

### modify_structure

- **位置**：`app/structure_identifier_prompt.py`
- **功能**：根据用户需求修改已生成的大纲。
- **参数**：
  - `text` (str)：原始文本
  - `structure` (str)：原大纲
  - `requirement` (str)：用户修改需求
  - `api_key` (str, 可选)：API密钥
  - `user` (str, 可选)：用户名
- **返回**：`List[str]`，修改后的大纲
- **示例**：
  ```python
  from app.structure_identifier_prompt import modify_structure
  new_outline = modify_structure("原文", "原大纲", "请加一节总结")
  print("".join(new_outline))
  ```

---

## 3. 会话管理相关

### new_conversation

- **位置**：`app/data_tracer.py`
- **功能**：新建空白会话，包括分配LLM接口编号
- **参数**：
  - `name` (str, 可选)：会话名称，默认“新会话”
- **返回**：`dict`，新会话信息

### function_initialize

- **位置**：`app/data_tracer.py`
- **功能**：初始化，读取所有历史会话
- **参数**：无
- **返回**：`list`，所有会话信息

### update_conversation_history

- **位置**：`app/data_tracer.py`
- **功能**：更新会话信息并同步到log目录
- **参数**：
  - `conversation_list` (list)：所有会话
  - `new_item` (dict)：要更新的会话
- **返回**：`list`，更新后的会话列表

### delete_conversation_history

- **位置**：`app/data_tracer.py`
- **功能**：删除指定会话
- **参数**：
  - `conversation_list` (list)：所有会话
  - `uuid_` (str)：要删除的会话ID
- **返回**：`list`，更新后的会话列表

### get_conversation_history

- **位置**：`app/data_tracer.py`
- **功能**：获取指定会话的全部信息
- **参数**：
  - `conversation_list` (list)：所有会话
  - `uuid_` (str)：会话ID
- **返回**：`dict`，会话信息

---

## 4. AI对话相关

### AssistantChat 类

- **位置**：`app/chatting.py`
- **功能**：管理AI对话会话
- **主要方法**：
  - `input_material(material, structure, user="noob")`：上传资料
  - `communicate(message, api_key=API_KEY)`：与AI对话，返回流式输出
  - `close_conversation(api_key=API_KEY)`：关闭会话

---

## 5. 依赖环境

- Python 3.8+
- 主要依赖见 requirements.txt
