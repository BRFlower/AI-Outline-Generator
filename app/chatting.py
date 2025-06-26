"""
    AssistantChat类：
    初始化：__init__: conversation_id(若为新建会话，还未指定，则不用传入)
    上传资料：input_material: material,structure(文本、大纲)
    AI对话: communicate: message(返回AI的回答，以流式输出)
    关闭会话：close_conversation: 关闭当前的会话

    ** 每个conversation_id对应一个独立的对话，而非每个不同的AssistantChat实例对应一个独立的对话，关闭对话后，对应的conversation_id不再可用
"""
from uuid import uuid1

import requests
import json

API_KEY = "app-DXSdoYfar1DpaxkGR7yuOWpv"

class AssistantChat:
    def __init__(self, conversation_id=''):
        self.material = ""
        self.structure = ""
        self.user = "noob"
        self.conversation_id = conversation_id
        
    def input_material(self, material, structure, user="noob"):
        self.material = material
        self.structure = structure
        self.user = user

    def communicate(self, message, api_key=API_KEY):
        url = 'https://api.dify.ai/v1/chat-messages'
        headers = {'Authorization': f'Bearer {api_key}'}
        payload = {
            'query': message,
            'user': self.user,
            'inputs': {
                'material': self.material,
                'structure': self.structure
            },
            'response_mode': 'streaming'
        }
        if self.conversation_id != '':
            payload['conversation_id'] = self.conversation_id
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            stream = []
            for line in response.iter_lines():
                if line and line[:6] == b'data: ':
                    line = line[6:]
                    data = json.loads(line)
                    content = data.get('answer', None)
                    if content:
                        stream.append(content)
                    if self.conversation_id == '':
                        print(f"new_conversation {self.conversation_id}")
                        self.conversation_id = data.get('conversation_id', None)
            return stream
        else :
            print(f"聊天异常，状态码:{response.status_code}，信息：{response.text}")
            return response.text
    def close_conversation(self, api_key=API_KEY):
        if self.conversation_id != '':
            print(f"delete conversation {self.conversation_id}")
            url = f'https://api.dify.ai/v1/conversations/{self.conversation_id}'
            headers = {'Authorization': f'Bearer {api_key}'}
            payload = {'user': self.user}
            response = requests.delete(url, headers=headers, json=payload)
            self.conversation_id, self.material, self.user, self.structure = None, '', 'noob', ''
            print(response.text)