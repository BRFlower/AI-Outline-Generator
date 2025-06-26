"""
    该模块实现了函数identify_structure，其接受一串文本，并输出一串文本，是输入文本的大纲，且采用了流式输出
    identify_structure:
        input:
            text: str #输入文本
            *api_key: str
            *user: str
        output: [str] #输出的大纲，采取流式输出，列表所有字符串加起来就是输出的文本
    modify_structure:
        input:
            text: str #输入文本
            structure: str #之前生成的大纲
            requirement: str #用户修改需求
        output: [str] #修改后的大纲，采取流式输出，如果修改出现任何异常，则输出原大纲
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

def modify_structure(text, structure, requirement, api_key=API_KEY, user="noob"):
    url = 'https://api.dify.ai/v1/workflows/run'
    headers = {'Authorization': f'Bearer {api_key}'}
    payload = {
        'inputs': {
            'text': text,
            'structure': structure,
            'requirement': requirement
        },
        'response_mode': 'streaming',
        'user': user
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        stream = []
        info = ""
        for line in response.iter_lines():
            if line and line[:6] == b'data: ':
                line = line[6:]
                data = json.loads(line)
                content = data.get('data', {}).get('text', None)
                if content:
                    stream.append(content)
                    info = info + content
        if info == "大纲修改异常":
            print(info)
            return [structure]
        else:
            print(text, structure, requirement, stream)
            print("知识点大纲修改完成")
            return stream
    else:
        print("知识点大纲修改失败")
        return [structure]