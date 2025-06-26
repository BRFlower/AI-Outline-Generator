"""
    该模块实现了函数identify_structure，其接受一串文本，并输出一串文本，是输入文本的大纲，且采用了流式输出
    identify_structure:
        input:
            text: str #输入文本
            *api_key: str
            *user: str
        output: [str] #输出的大纲，采取流式输出，列表所有字符串加起来就是输出的文本
"""
import requests
import json

API_KEY = "app-YcJxcYWJ0II3ERqvPhw6VbUu"

def identify_structure(text, api_key=API_KEY, user="noob"):
    url = 'https://api.dify.ai/v1/workflows/run'
    headers = {'Authorization': f'Bearer {api_key}'}
    payload = {
        'inputs': {'text': text},
        'response_mode': 'streaming',
        'user': user
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("知识点大纲生成完成")
        stream = []
        for line in response.iter_lines():
            if line and line[:6] == b'data: ':
                line = line[6:]
                data = json.loads(line)
                content = data.get('data', {}).get('text', None)
                if content:
                    stream.append(content)
        return stream
    else :
        print("知识点大纲生成失败")
        return [response.text]