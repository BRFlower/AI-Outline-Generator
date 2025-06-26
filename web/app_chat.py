import gradio as gr
import time

# 创建聊天面板的函数
def create_chat_panel(initial_history=None):
    """创建并返回聊天界面的Gradio组件。它只负责UI的"样子"。"""
    with gr.Column(scale=1, elem_id="chat_container"):
        # gr.Markdown("## 对话")
        chatbot = gr.Chatbot(
            value=initial_history if initial_history else [],
            elem_id="chatbot",
            # label="对话历史",
            bubble_full_width=False,
            show_copy_button=False,
            # show_delete_button=False
        )
        
        chat_input = gr.Textbox(
            show_label=False,
            placeholder="在这里输入你的问题...开头加上\"/structure \" 以生成大纲",
            container=False,
            lines=3,
            elem_id="chat_input"
        )
        with gr.Row(elem_id="send_bar"):
            gr.HTML("<p style='color:grey; font-size:0.8rem; margin:0; line-height:1.5;'>Ctrl+Enter to send</p>")
            send_btn = gr.Button("发送", variant="primary", elem_id="send_button", size="sm")
        
        # 具体的聊天逻辑（输入、发送、接收）应该由主应用(app.py)通过事件来控制
        
        return chatbot, chat_input, send_btn
