"""
    该模块意在结合外部存储实现历史查询功能，通过在log文件夹下内容的读写实现
    function_initialize: #在程序启动时运行，读取历史数据
        output: #返回所有会话列表
    new_conversation: #新建空白对话
        input: #会话标题（就是名称），默认为"新会话"
        output: #新会话uuid以及其他全部信息
    update_conversation_history: #在更换会话时运行，更新原会话数据，若不存在uuid则新建一个会话，数据同步到log文件夹
        input: #会话列表，更新的会话信息
        output: #更新后的会话列表
    delete_conversation_history: #删除会话，数据同步到log文件夹，同时会删除dify上chatflow的对应会话
        input: #要删除的会话uuid
        output: #更新后的会话列表
    get_conversation_history: #获取会话信息
        input: #会话uuid
        output：#对应会话的全部信息，内容同上

    **所谓的会话信息，完整格式为：
    {
        'id': 会话的uuid（唯一标识符，uuid模块生成，需转为str）,
        'name': 会话名称（需可修改）,
        'bot': 该会话对应的AssistantChat实例,
        'material': 该会话已有的学习文本,
        'structure': 该会话已有的资料大纲,
        'chat_history': 该会话中的AI聊天内容 [
            {
                'role': 'user'/'assistant' 用户发送的聊天/AI回答内容,
                'content': <对话内容>
            }, 此为一条信息
            ...
        ]
    },会话列表指的是多个会话信息构成的list

    **外部储存格式为：
    ../log (与data_traver.py在同一目录下)
    - conversation_list （储存所有会话的uuid）
    - /{uuid} （一个会话）
      - name (同上)
      - material (同上)
      - structure (同上)
      - bot_id （该会话的bot的conversation_id）
      - chat（储存AI聊天的信息，将信息列表转为字符串，每条信息的开头以<role>#$%@标识，因为聊天信息中可能存在换行符，标识后的内容均为<role>对应的聊天信息）
    - /...
"""
import os
import uuid
from app.chatting import AssistantChat

LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'log'))

def new_conversation(name = '新会话'):
    uuid_ = uuid.uuid1()
    return {
        'id': str(uuid_),
        'bot': AssistantChat(),
        'name': name,
        'material': '',
        'structure': '',
        'chat_history': []
    }

def function_initialize():
    print("retrieving data...")
    list_file_path = os.path.join(LOG_DIR, "conversation_list")

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    if not os.path.exists(list_file_path):
        open(list_file_path, 'a').close()

    conversation_list = []
    with open(list_file_path, "r", encoding='utf-8') as list_file:
        for line in list_file.readlines():
            id = line.strip()
            if not id:
                continue

            conv_dir = os.path.join(LOG_DIR, id)
            bot_id_path = os.path.join(conv_dir, "bot_id")
            # if not os.path.exists(bot_id_path):
            #     print(f"Warning: bot_id missing for {id}, skipping.")
            #     continue

            # 只要bot_id存在，其他文件缺失用空内容
            def safe_read(path):
                return open(path, encoding='utf-8').read() if os.path.exists(path) else ""

            name = safe_read(os.path.join(conv_dir, "name"))
            bot_id = safe_read(bot_id_path)
            material = safe_read(os.path.join(conv_dir, "material"))
            structure = safe_read(os.path.join(conv_dir, "structure"))

            chat_history = []
            chat_path = os.path.join(conv_dir, "chat")
            if os.path.exists(chat_path):
                with open(chat_path, encoding='utf-8') as f:
                    current_message = None
                    for chat_line in f.readlines():
                        if chat_line.startswith('user#$%@'):
                            if current_message: chat_history.append(current_message)
                            current_message = {'role': 'user', 'content': chat_line[8:]}
                        elif chat_line.startswith('assistant#$%@'):
                            if current_message: chat_history.append(current_message)
                            current_message = {'role': 'assistant', 'content': chat_line[13:]}
                        elif current_message:
                            current_message['content'] += chat_line
                    if current_message: chat_history.append(current_message)

            conversation_list.append({
                'id': id,
                'bot': AssistantChat(bot_id),
                'name': name,
                'material': material,
                'structure': structure,
                'chat_history': chat_history
            })
    return conversation_list

def update_conversation_history(conversation_list, new_item):
    id = new_item['id']
    new_conversation_list = []
    for item in conversation_list:
        if item['id'] != id:
            new_conversation_list.append(item)
        # new_conversation_list.append(new_item)
        # with open("log/conversation_list", "a") as list_file:
        #     list_file.write(new_item['id'] + '\n')
    new_conversation_list = [new_item] + new_conversation_list
    
    list_file_path = os.path.join(LOG_DIR, "conversation_list")
    conv_dir = os.path.join(LOG_DIR, id)

    with open(list_file_path, "w") as list_file:
        for item in new_conversation_list:
            list_file.write(item['id'] + '\n')
    
    if not os.path.exists(conv_dir):
        os.mkdir(conv_dir)

    with open(os.path.join(conv_dir, "bot_id"), "w", encoding='utf-8') as bot_file:
        bot_file.write(new_item['bot'].conversation_id)
    with open(os.path.join(conv_dir, "name"), "w", encoding='utf-8') as name_file:
        name_file.write(new_item['name'])
    with open(os.path.join(conv_dir, "material"), "w", encoding='utf-8') as material_file:
        material_file.write(new_item['material'])
    with open(os.path.join(conv_dir, "structure"), "w", encoding='utf-8') as structure_file:
        structure_file.write(new_item['structure'])
    with open(os.path.join(conv_dir, "chat"), "w", encoding='utf-8') as chat_file:
        for chat_log in new_item['chat_history']:
            chat_file.write(f'{chat_log["role"]}#$%@{chat_log["content"]}\n')
    return new_conversation_list

def delete_conversation_history(conversation_list, uuid_):
    id = str(uuid_)
    list_file_path = os.path.join(LOG_DIR, "conversation_list")
    conv_dir = os.path.join(LOG_DIR, id)
    
    with open(list_file_path, "w") as list_file:
        new_conversation_list = []
        for item in conversation_list:
            if item['id'] != id:
                new_conversation_list.append(item)
                list_file.write(item['id'] + '\n')
            else :
                item['bot'].close_conversation()
                os.remove(os.path.join(conv_dir, "bot_id"))
                os.remove(os.path.join(conv_dir, "name"))
                os.remove(os.path.join(conv_dir, "material"))
                os.remove(os.path.join(conv_dir, "structure"))
                os.remove(os.path.join(conv_dir, "chat"))
                os.rmdir(conv_dir)
    return new_conversation_list

def get_conversation_history(conversation_list, uuid_):
    id = str(uuid_)
    for item in conversation_list:
        if item['id'] == id:
            return item
