import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import gradio as gr
from app_chat import create_chat_panel
from app.data_tracer import function_initialize, new_conversation, update_conversation_history
from app.chatting import AssistantChat
from app.text_extractor import extract_text_traditional
from app.structure_identifier_prompt import identify_structure, modify_structure

# 1. 在应用启动时加载所有会话数据，并将其反转，这样最新的就在最前面
conversation_list = list(function_initialize())
# print(conversation_list)
# 移除硬编码的ID
# id = "123e4567-e89b-12d3-a456-426614174000" 

def format_chat_for_display(chat_history):
    """将data_tracer格式的聊天记录转换为Gradio.Chatbot能显示的格式。"""
    if not chat_history:
        return []

    gradio_history = []
    # 按照 user -> assistant 的配对来组合聊天记录
    for i in range(0, len(chat_history), 2):
        if chat_history[i]['role'] == 'user':
            user_msg = chat_history[i]['content']

        if i < len(chat_history) - 1 and chat_history[i+1]['role'] == 'assistant':
            assistant_msg = chat_history[i+1]['content']
        else:
            assistant_msg = ""
        
        gradio_history.append((user_msg, assistant_msg))
            
    return gradio_history

# 创建新任务逻辑
def create_new_task(all_convs):
    from app.data_tracer import new_conversation, update_conversation_history
    # 创建新会话
    new_conv = new_conversation()
    # 插入到会话列表最前面
    all_convs.insert(0, new_conv)
    # 同步到本地存储
    all_convs = update_conversation_history(all_convs, new_conv)
    # 返回新会话内容，刷新界面
    return (
        new_conv['material'],
        new_conv['structure'],
        format_chat_for_display(new_conv['chat_history']),
        new_conv['id'],
        all_convs,
        gr.update(choices=[(c['name'], c['id']) for c in all_convs], value=new_conv['id'])
    )


with gr.Blocks(title="AI文档大纲生成", theme=gr.themes.Soft(), fill_height=True ) as demo:
    # 2. 用State来管理会话列表和当前激活的会话ID
    conv_list_state = gr.State(conversation_list)
    active_conv_id = gr.State(conversation_list[0]['id'] if conversation_list else None)
    
    with gr.Row(height="100%") as main_row:
        # 左侧边栏 25%
        with gr.Column(scale=25, min_width=0, elem_id="sidebar") as sidebar:
            new_task_btn = gr.Button("新建", variant="primary")
            
            # 新增：上传材料按钮
            upload_file = gr.File(
                # label="点击/拖动上传材料",
                file_types=[
                    ".txt", ".md", ".markdown", ".rst", ".tex", ".html", ".htm",
                    ".xml", ".json", ".csv", ".tsv", ".log", ".ini", ".cfg", ".conf",
                    ".py", ".js", ".ts", ".jsx", ".tsx", ".vue", ".java", ".cpp", ".c",
                    ".h", ".hpp", ".cs", ".php", ".rb", ".go", ".rs", ".swift", ".kt",
                    ".scala", ".sql", ".sh", ".bat", ".ps1", ".yaml", ".yml", ".toml",
                    ".properties", ".env", ".gitignore", ".dockerfile", ".makefile",
                    ".cmake", ".sass", ".scss", ".less", ".css", ".styl", ".coffee",
                    ".lua", ".pl", ".pm", ".r", ".m", ".f", ".f90", ".f95", ".f03",
                    ".ada", ".pas", ".d", ".nim", ".zig", ".v", ".sv", ".vhd", ".vhdl",
                    ".docx", ".pptx", ".pdf"
                ],
                file_count="single",
                height=80
            )
            upload_btn = gr.Button("提取文本", variant="secondary")
            
            # 移除多余的标题间距，直接贴紧按钮
            # gr.Markdown("### 历史记录", elem_id="history_title")
            # 新增：删除会话按钮
            delete_btn = gr.Button("删除所选会话", variant="stop")
            # 3. 用Radio组件来显示和选择会话，竖直排列并可滚动
            history_radio = gr.Radio(
                choices=[(c['name'], c['id']) for c in conversation_list],
                value=conversation_list[0]['id'] if conversation_list else None,
                label="会话列表",
                elem_id="history_radio",
                container=True,
                show_label=True,
                scale=1
            )
        
        # 中间和右侧内容
        with gr.Column(scale=75, min_width=0, elem_id="main-content") :
            with gr.Row(height="100%",):
                # 中间资料区 35%
                with gr.Column(scale=35, min_width=0, elem_id="main-content-middle") :
                    # 会话标题可编辑
                    with gr.Row(height=50,scale=1) :
                        title_box = gr.Textbox(
                            label="会话标题",
                            value=conversation_list[0]['name'] if conversation_list else "",
                            lines=1,
                            max_lines=1,
                            interactive=True
                        )
                    # gr.Markdown("## 中间区域")
                    
                    # 定义初始值
                    initial_material = conversation_list[0]['material'] if conversation_list else ""
                    initial_structure = conversation_list[0]['structure'] if conversation_list else ""
                    
                    # 新增：为material和structure添加应用和回退按钮及状态
                    material_applied_state = gr.State(initial_material)
                    structure_applied_state = gr.State(initial_structure)                    
                    with gr.Row(scale=5) :
                        material_content = gr.Textbox(
                            label="学习资料", 
                            value=initial_material,
                            lines=12,
                            placeholder="这里是学习资料内容...",
                            interactive=True,
                            elem_id="material_content",
                            max_lines=20  # 可选，防止内容撑开太多
                        )
                    with gr.Row(height=30):
                        material_apply_btn = gr.Button("应用", variant="primary")
                        material_undo_btn = gr.Button("回退", variant="secondary")
                    with gr.Row(scale=5) :                
                        structure_content = gr.Textbox(
                            label="资料大纲", 
                            value=initial_structure,
                            lines=12,
                            placeholder="这里是资料大纲内容...",
                            interactive=True,
                            elem_id="structure_content",
                            max_lines=20  # 可选，防止内容撑开太多                      
                        )
                    with gr.Row(height=30):
                        structure_apply_btn = gr.Button("应用", variant="primary")
                        structure_undo_btn = gr.Button("回退", variant="secondary")
                
                # 聊天框 40%
                with gr.Column(scale=40, min_width=0, elem_id="main-content-Right") :
                    # 4. 嵌入聊天面板，并传入初始聊天记录
                    initial_chat_history = []
                    if conversation_list:
                        initial_chat_history = format_chat_for_display(conversation_list[0]['chat_history'])
                    chatbot, chat_input, send_btn = create_chat_panel(initial_history=initial_chat_history)

    # --- 事件处理 ---
    
    # 聊天响应函数
    def respond_and_update(message, chat_history, active_id, all_convs):
        """流式输出：先显示用户输入，再流式显示AI回复"""
        if not message or not message.strip():
            yield gr.update(), gr.update(), gr.update(), gr.update()
            return
        # chat_history.append((message, ""))
        # 检查是否是/structure命令
        if message.strip().startswith('/structure'):
            chat_history = list(chat_history)
            chat_history.append((message, ""))  # 先显示用户输入
            yield "", chat_history, all_convs, gr.update()

            # 先判定 material 是否存在
            this_chat = next((c for c in all_convs if c['id'] == active_id), None)
            if not this_chat or not this_chat['material']:
                chat_history[-1] = (message, "请先上传学习资料或提供要生成大纲的文本内容。")
                yield "", chat_history, all_convs, gr.update()
                return

            # 取 requirement
            requirement = message[10:].strip()
            # 如果原大纲为空，传入"当前无大纲"
            structure_input = this_chat['structure'] if this_chat['structure'] else '当前无大纲'
            ai_reply = ""
            try:
                structure_stream = modify_structure(
                    this_chat['material'],
                    structure_input,
                    requirement
                )
                for chunk in structure_stream:
                    chunk = str(chunk) if chunk is not None else ""
                    ai_reply += chunk
                    chat_history[-1] = (message, ai_reply)
                    yield "", chat_history, all_convs, gr.update()
                # 保存大纲和对话历史
                this_chat['structure'] = ai_reply
                this_chat['chat_history'].append({'role': 'user', 'content': message})
                this_chat['chat_history'].append({'role': 'assistant', 'content': ai_reply})
                from app.data_tracer import update_conversation_history
                all_convs = update_conversation_history(all_convs, this_chat)
                this_chat['bot'].input_material(this_chat['material'], this_chat['structure'])
                yield "", chat_history, all_convs, ai_reply
                return
            except Exception as e:
                chat_history[-1] = (message, f"生成大纲时出现错误: {str(e)}")
                yield "", chat_history, all_convs, gr.update()
                return
                
        else:
            # 正常的聊天对话
            # 先把用户输入显示到页面
            chat_history = list(chat_history)  # 确保是可变的
            chat_history.append((message, ""))  # 先显示用户输入，AI回复为空
            yield "", chat_history, all_convs, gr.update()

            this_chat = next((c for c in all_convs if c['id'] == active_id), None)
            if this_chat:
                # 每次对话前都同步最新资料和大纲到 bot
                this_chat['bot'].input_material(this_chat['material'], this_chat['structure'])
            ai_reply = ""
            for chunk in this_chat['bot'].communicate(message):  # 假设这是个生成器
                ai_reply += chunk
                chat_history[-1] = (message, ai_reply)  # 更新最后一条
                yield "", chat_history, all_convs, gr.update()

            # 最后，更新后端数据
            if this_chat:
                this_chat['chat_history'].append({'role': 'user', 'content': message})
                this_chat['chat_history'].append({'role': 'assistant', 'content': ai_reply})
                from app.data_tracer import update_conversation_history
                all_convs = update_conversation_history(all_convs, this_chat)
                if this_chat:
                    this_chat['bot'].input_material(this_chat['material'], this_chat['structure'])
                yield "", chat_history, all_convs, gr.update()

    # 绑定发送按钮的点击事件
    send_btn.click(
        fn=respond_and_update,
        inputs=[chat_input, chatbot, active_conv_id, conv_list_state],
        outputs=[chat_input, chatbot, conv_list_state, structure_content]
    )
    
    # 移除输入框的回车提交事件
    # chat_input.submit(...)

    def switch_conversation(conv_id, all_convs):
        """切换会话时的处理函数"""
        this_chat = next((c for c in all_convs if c['id'] == conv_id), None)
        if not this_chat:
            return None, None, [], None # Return updates for all outputs
        formatted_history = format_chat_for_display(this_chat['chat_history'])        
        # 返回更新后的聊天记录、资料、大纲和新的激活ID
        return this_chat['material'], this_chat['structure'], formatted_history, this_chat['id']

    # 5. 当选择新会话时，更新所有相关模块和激活ID
    history_radio.change(
        fn=switch_conversation,
        inputs=[history_radio, conv_list_state],
        outputs=[material_content, structure_content, chatbot, active_conv_id],
        queue=True
    )

    def reload_conversations():
        conversation_list = list(function_initialize())
        # 选中第一个会话
        if conversation_list:
            first = conversation_list[0]
            return (
                first['material'],
                first['structure'],
                format_chat_for_display(first['chat_history']),
                first['id'],
                conversation_list,
                gr.update(choices=[(c['name'], c['id']) for c in conversation_list], value=first['id'])
            )
        else:
            return "", "", [], None, [], gr.update(choices=[], value=None)

    demo.load(
        fn=reload_conversations,
        inputs=None,
        outputs=[material_content, structure_content, chatbot, active_conv_id, conv_list_state, history_radio],
        js="""
        () => {
            // 等待Gradio渲染完成
            setTimeout(() => {
                const chatInput = document.querySelector('#chat_input textarea');
                if (chatInput) {
                    chatInput.addEventListener('keydown', (e) => {
                        // 检查是否按下了Ctrl+Enter
                        if (e.key === 'Enter' && e.ctrlKey) {
                            // 客户端校验：如果输入为空或只包含空白，则不执行任何操作
                            if (chatInput.value.trim() === '') {
                                e.preventDefault(); // 依然阻止默认的换行行为
                                return;
                            }
                            // 阻止默认的回车换行行为
                            e.preventDefault();
                            // 找到发送按钮并模拟点击
                            const sendButton = document.querySelector('#send_button');
                            if (sendButton) {
                                sendButton.click();
                            }
                        }
                    });
                }
            }, 200);
        }
        """
    )

    # 新增会话标题修改事件
    def update_title(new_title, all_convs, active_id):
        this_chat = next((c for c in all_convs if c['id'] == active_id), None)
        if this_chat:
            this_chat['name'] = new_title
            from app.data_tracer import update_conversation_history
            all_convs = update_conversation_history(all_convs, this_chat)
        # 更新左侧会话列表
        return gr.update(choices=[(c['name'], c['id']) for c in all_convs], value=active_id), all_convs

    title_box.change(
        fn=update_title,
        inputs=[title_box, conv_list_state, active_conv_id],
        outputs=[history_radio, conv_list_state]
    )

    new_task_btn.click(
        fn=create_new_task,
        inputs=[conv_list_state],
        outputs=[material_content, structure_content, chatbot, active_conv_id, conv_list_state, history_radio]
    )

    # 新增删除会话逻辑
    def delete_conversation(selected_id, all_convs):
        from app.data_tracer import delete_conversation_history
        if not selected_id:
            return gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
        # 删除会话
        new_convs = delete_conversation_history(all_convs, selected_id)
        # 选中第一个会话
        if new_convs:
            first = new_convs[0]
            return (
                first['material'],
                first['structure'],
                format_chat_for_display(first['chat_history']),
                first['id'],
                new_convs,
                gr.update(choices=[(c['name'], c['id']) for c in new_convs], value=first['id'])
            )
        else:
            # 没有会话了，全部清空
            return "", "", [], None, [], gr.update(choices=[], value=None)

    # 新增：文件上传和文本提取功能
    def upload_and_extract_text(file, all_convs, active_id):
        """上传文件并提取文本内容到当前会话的material部分"""
        if not file or not active_id:
            gr.Warning("请先选择文件或会话")
            return gr.update(), gr.update()
        
        try:
            # 获取文件路径
            file_path = file.name
            
            # 使用text_extractor提取文本
            extracted_text_stream = extract_text_traditional(file_path)
            
            # 将流式输出合并为完整文本
            extracted_text = "".join(extracted_text_stream)
            
            # 更新当前会话的material内容
            this_chat = next((c for c in all_convs if c['id'] == active_id), None)
            if this_chat:
                this_chat['material'] = extracted_text
                from app.data_tracer import update_conversation_history
                all_convs = update_conversation_history(all_convs, this_chat)
                gr.Info(f"文件 {os.path.basename(file_path)} 文本提取完成")
            else:
                gr.Warning("未找到当前会话")
                return gr.update(), gr.update()
            
            return extracted_text, all_convs
            
        except Exception as e:
            gr.Error(f"文件处理失败: {str(e)}")
            return gr.update(), gr.update()

    delete_btn.click(
        fn=delete_conversation,
        inputs=[history_radio, conv_list_state],
        outputs=[material_content, structure_content, chatbot, active_conv_id, conv_list_state, history_radio]
    )

    # 新增：绑定文件上传和文本提取事件
    upload_btn.click(
        fn=upload_and_extract_text,
        inputs=[upload_file, conv_list_state, active_conv_id],
        outputs=[material_content, conv_list_state]
    )

    # 修改：只有点击"应用修改"才会保存
    def apply_material(new_material, all_convs, active_id, last_applied):
        this_chat = next((c for c in all_convs if c['id'] == active_id), None)
        changed = new_material != last_applied
        if changed and this_chat:
            this_chat['material'] = new_material
            from app.data_tracer import update_conversation_history
            all_convs = update_conversation_history(all_convs, this_chat)
            this_chat['bot'].input_material(this_chat['material'], this_chat['structure'])
            gr.Info("修改资料")
        return new_material, all_convs

    def undo_material(applied_material):
        return applied_material

    def apply_structure(new_structure, all_convs, active_id, last_applied):
        this_chat = next((c for c in all_convs if c['id'] == active_id), None)
        changed = new_structure != last_applied
        if changed and this_chat:
            this_chat['structure'] = new_structure
            from app.data_tracer import update_conversation_history
            all_convs = update_conversation_history(all_convs, this_chat)
            this_chat['bot'].input_material(this_chat['material'], this_chat['structure'])
            gr.Info("修改大纲")
        return new_structure, all_convs

    def undo_structure(applied_structure):
        return applied_structure

    # 绑定按钮事件
    material_apply_btn.click(
        fn=apply_material,
        inputs=[material_content, conv_list_state, active_conv_id, material_applied_state],
        outputs=[material_applied_state, conv_list_state]
    )
    material_undo_btn.click(
        fn=undo_material,
        inputs=[material_applied_state],
        outputs=[material_content]
    )
    structure_apply_btn.click(
        fn=apply_structure,
        inputs=[structure_content, conv_list_state, active_conv_id, structure_applied_state],
        outputs=[structure_applied_state, conv_list_state]
    )
    structure_undo_btn.click(
        fn=undo_structure,
        inputs=[structure_applied_state],
        outputs=[structure_content]
    )

    # 自定义CSS
    custom_css = """
    /* 全局缩放和紧凑布局 */
    * {
        font-size: 0.9em !important;
    }
    
    /* 缩小按钮 */
    button {
        padding: 6px 12px !important;
        font-size: 0.85em !important;
        height: auto !important;
        min-height: 28px !important;
    }
    
    /* 缩小输入框 */
    textarea, input[type="text"] {
        font-size: 0.85em !important;
        padding: 4px 8px !important;
        line-height: 1.3 !important;
    }
    
    /* 缩小标签 */
    label {
        font-size: 0.8em !important;
        margin-bottom: 2px !important;
    }
    
    /* 缩小标题 */
    .gr-text {
        font-size: 0.9em !important;
    }
    
    /* 缩小聊天消息 */
    .message {
        font-size: 0.85em !important;
        padding: 6px 8px !important;
    }
    
    /* 缩小文件上传组件 */
    .file-upload {
        font-size: 0.8em !important;
    }
    
    /* 缩小Radio组件 */
    .gr-radio {
        font-size: 0.8em !important;
    }
    
    /* 缩小聊天机器人组件 */
    .chatbot {
        font-size: 0.85em !important;
    }
    
    /* 减少间距 */
    .gr-form {
        gap: 8px !important;
    }
    
    .gr-row {
        gap: 8px !important;
        margin-bottom: 8px !important;
    }
    
    .gr-column {
        gap: 8px !important;
    }
    
    /* 缩小容器高度 */
    .gr-container {
        padding: 8px !important;
    }
    
    /* 缩小边框和圆角 */
    .gr-box {
        border-radius: 4px !important;
        border-width: 1px !important;
    }
    
    html, body, .gradio-container, #main-row {
        height: 100% !important;
        min-height: 100%  !important;
        overflow: auto;
    }
    #container, .gradio-row, .gradio-column {
        height: 100% !important;
        min-height: 0 !important;
        overflow: visible;
    }
    #chatbot, #chat_input_box, #send_btn {
        box-sizing: border-box;
        width: 100%;
        min-width: 0;
        height: 100%;
        border-radius: 8px;
    }
    #chatbot {        
        min-width: 180px; /* 减小最小宽度 */
        overflow-y: auto;
        display: flex;
        font-size: 0.8em !important; /* 减小字体 */
        min-height: 320px; /* 增加最小高度，原本没有或较小 */
        height: 50vh;      /* 增加整体高度，原本没有或较小 */
        max-height: 60vh;  /* 可选，防止撑满整个页面 */
    }
    #chat_input_box {
        border: 1.5px solid #e0e0e0;
        margin-bottom: 8px;
    }
    #send_btn {
        border: 1.5px solid #e0e0e0;
        margin-bottom: 0;
        height: 32px; /* 减小按钮高度 */
        /* 让按钮和输入框高度对齐 */
    }
    #sidebar {
        height: 100% !important;
        min-height: 0 !important;
        flex-direction: column;
        overflow-y: auto;
        border: 1.5px solid #e0e0e0;
    }

    #chat_container {
        display: flex;
        flex-direction: column;
        height: 100%;
        max-height: 100%; /* 确保它不会超出父容器 */
    }

    /* 可调整大小的分隔线 */
    .gradio-container {
        height: 100vh;
        overflow: hidden;
    }

    #sidebar {
        transition: all 0.3s ease;
        border-right: 1px solid #e0e0e0;
        display: flex;
        flex-direction: column;
        padding: 6px; /* 减少内边距 */
    }

    #toggle-btn {
        margin-bottom: 6px; /* 减少间距 */
        width: 100%;
        min-width: 50px; /* 减小最小宽度 */
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 14px; /* 减小字体 */
    }
    
    #sidebar button {
        width: 100% !important;
        margin-bottom: 6px; /* 减少间距 */
        height: 28px !important; /* 减小按钮高度 */
        font-size: 0.8em !important;
        box-sizing: border-box;
        min-width: 0;
        max-width: 100%;
        display: block;
    }
    
    #send_bar {
        justify-content: space-between;
        align-items: center;
    }

    /* 可调整大小的列 */
    .gradio-row {
        position: relative;
    }

    .resizer {
        position: absolute;
        top: 0;
        bottom: 0;
        width: 5px;
        background-color: #e0e0e0;
        cursor: col-resize;
        z-index: 10;
    }

    .resizer:hover {
        background-color: #a0a0a0;
    }

    /* 垂直分隔线 */
    .vertical-resizer {
        position: absolute;
        left: 0;
        right: 0;
        height: 5px;
        background-color: #e0e0e0;
        cursor: row-resize;
        z-index: 10;
    }

    .vertical-resizer:hover {
        background-color: #a0a0a0;
    }

    /* 应用分隔线 */
    .gradio-row:nth-child(1) > .gradio-column:nth-child(1) {
        position: relative;
    }

    .gradio-row:nth-child(1) > .gradio-column:nth-child(1)::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 0;
        right: 0;
        height: 5px;
        background-color: #e0e0e0;
        cursor: row-resize;
        transform: translateY(-50%);
        z-index: 10;
    }

    /* 右侧分隔线 */
    .gradio-row:nth-child(1) {
        position: relative;
    }

    .gradio-row:nth-child(1)::before {
        content: '';
        position: absolute;
        top: 0;
        bottom: 0;
        left: calc(75% - 2.5px);
        width: 5px;
        background-color: #e0e0e0;
        cursor: col-resize;
        z-index: 10;
    }

    #history_radio {
        display: flex;
        flex-direction: column;
        align-items: flex-start; /* 靠上对齐 */
        height: 100%;
        overflow-y: auto;
        gap: 0px;
    }
    #history_radio .gr-radio {
        width: 100%;
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: column;
    }
    #history_radio label {
        width: 100%;
        display: block;
        margin: 0;
        padding: 2px 0 2px 0; /* 减少内边距 */
        text-align: left;
        font-size: 0.75em !important; /* 减小字体 */
    }
    #sidebar {
        min-width: 160px; /* 减小最小宽度 */
        max-width: 25vw;
        width: 25vw;
    }
    #main-content {
        width: 75vw;
        display: flex;
        flex-direction: row;
        height: 100%;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
    }
    #main-content-middle, #main-content-Right {
        height: 100%;
        display: flex;
    }
    #material_content, #structure_content textarea {        
        min-height: 120px; /* 减小最小高度 */
        height: 100%;
        max-height: 35vh; /* 减小最大高度 */
        overflow-y: auto;
        font-size: 0.8em !important; /* 减小字体 */
        line-height: 1.2 !important; /* 减小行高 */
    }
    #chatbot {        
        min-width: 180px; /* 减小最小宽度 */
        overflow-y: auto;
        display: flex;
        font-size: 0.8em !important; /* 减小字体 */
        height: 80%;
    }
    #chat_header {
        height: 100%;
        display: flex;
    }
    #chat_input_row {
        height: 60px; /* 减小高度 */
    }
    #sidebar > .gr-column > * {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    #new_task_btn, #history_title, #history_radio {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    #history_title {
        margin-bottom: 1px !important; /* 减少间距 */
        margin-top: 4px !important; /* 减少间距 */
    }
    #history_radio {
        margin-top: 1px !important; /* 减少间距 */
    }
    
    /* 缩小标题框 */
    #title_box {
        height: 50px !important; /* 减小高度 */
        font-size: 0.85em !important;
    }
    
    /* 缩小应用和回退按钮行 */
    .gr-row[height="40"] {
        height: 30px !important; /* 减小高度 */
    }
    
    /* 缩小文件上传组件 */
    .file-upload {
        height: 80px !important; /* 减小高度 */
    }
    
    /* 缩小聊天输入框 */
    #chat_input textarea {
        font-size: 0.8em !important;
        padding: 4px 6px !important;
        line-height: 1.2 !important;
    }
    
    /* 缩小所有图标 */
    svg, .gr-icon {
        transform: scale(0.8) !important;
    }
    
    /* 缩小所有间距 */
    .gr-form, .gr-box, .gr-container {
        gap: 4px !important;
        margin: 2px !important;
        padding: 4px !important;
    }
    """

    # 应用自定义CSS
    demo.css = custom_css

# 启动应用
demo.launch(server_port=7861)