from fastapi import FastAPI, __version__,Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import requests

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from bs4 import BeautifulSoup
import json
import time
from concurrent.futures import ThreadPoolExecutor

from pathlib import Path
from openai import OpenAI

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
# 允许所有来源的请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

executor = ThreadPoolExecutor(max_workers=20)

templates = Jinja2Templates(directory="templates")

@app.get("/hello1", response_class=HTMLResponse)
async def hello1(request: Request):
   return templates.TemplateResponse("hello1.html", {"request": request})

@app.get("/test", response_class=HTMLResponse)
async def test(request: Request):
   return templates.TemplateResponse("test.html", {"request": request})

@app.get("/hello", response_class=HTMLResponse)
async def hello(request: Request, name:str):
   return templates.TemplateResponse("hello.html", {"request": request, "name":name})

html = f"""
<!DOCTYPE html>
<html>
    <head>
        <title>FastAPI on Vercel</title>
        <link rel="icon" href="/static/favicon.ico" type="image/x-icon" />
    </head>
    <body>
        <div class="bg-gray-200 p-4 rounded-lg shadow-lg">
            <h1>Hello from FastAPI@{__version__}</h1>
            <ul>
                <li><a href="/docs">/docs</a></li>
                <li><a href="/redoc">/redoc</a></li>
            </ul>
            <p>Powered by <a href="https://vercel.com" target="_blank">Vercel</a></p>
        </div>
    </body>
</html>
"""

@app.get("/")
async def root():
    return HTMLResponse(html)

@app.get('/ping')
async def hello():
    return {'res': 'pong', 'version': __version__, "time": time()}

@app.get("/api/ocr")
def ocr(img: str):

    # OCR API 的密钥
    api_key = "K88294794488957"
    image_url = "https://img-blog.csdnimg.cn/img_convert/9e12ef54e34d401db3e084404e7205bd.png"
    language = "chs"

    # 构造请求参数
    data = {
        "isOverlayRequired": "true",
        "url": image_url,
        "language": language
    }

    # 发送 POST 请求
    headers = {"apikey": api_key}
    response = requests.post("https://api.ocr.space/Parse/Image", data=data, headers=headers)

    result=''
    # 检查响应状态码并打印响应内容
    if response.status_code == 200:
        result = response.json()  # 假设返回的是 JSON 格式的数据
        print(result)
    else:
        print(f"请求失败，状态码：{response.status_code}")
    return {"message": result}    

@app.get("/api/test")
def hello_world(name: str):
    return {"name": name}       


# xuanjie https://www.xiaoyuzhoufm.com/podcast/65cdec45a55e5c054bd9297b

@app.get("/api/xiaoyuzhou_result")
def xiaoyuzhou_result(title: str):
    return {"message": xiaoyuzhou_result[title]}

@app.get("/api/xiaoyuzhou")
async def xiaoyuzhou(url: str):
    # 2. 获取网页源代码并解析
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # 3. 获取音频文件的标题和下载地址
    title_tag = soup.find('meta', {'property': 'og:title'})
    audio_tag = soup.find('meta', {'property': 'og:audio'})
    title = title_tag['content']
    audio_url = audio_tag['content']
    # 4. 下载音频文件并保存到本地
    #response = requests.get(audio_url)
    #with open(f"{title}.mp3", "wb") as f:
    #    f.write(response.content)
    #print(f"音频文件 {title}.mp3 下载完成！")
    xiaoyuzhou_result[title]=None
    executor.submit(xiaoyuzhou_async, title,audio_url)
    return {"message": title}

API_KEY_ID = "IUl33ZlWbcDWelcS"
API_KEY_SECRET = "57vG6THCtRQRXx8m"

# The language code of the speech in media file.
# See more lang code: https://docs.speechflow.io/#/?id=ap-lang-list
LANG = "zh"
# The local path or remote path of media file.

# The translation result type.
# 1, the default result type, the json format for sentences and words with begin time and end time.
# 2, the json format for the generated subtitles with begin time and end time.
# 3, the srt format for the generated subtitles with begin time and end time.
# 4, the plain text format for transcription results without begin time and end time.
RESULT_TYPE = 1

headers = {"keyId": API_KEY_ID, "keySecret": API_KEY_SECRET}


def ai_result(title:str):
    client = OpenAI(
        api_key="sk-JOcsgByeEXwF2rndI4VEzUfIfpWL1agC2Q0uHjKM730edQPg",
        base_url="https://api.moonshot.cn/v1",
    )

    # xlnet.pdf 是一个示例文件, 我们支持 pdf, doc 以及图片等格式, 对于图片和 pdf 文件，提供 ocr 相关能力
    # xlnet.pdf 是一个示例文件, 我们支持 pdf, doc 以及图片等格式, 对于图片和 pdf 文件，提供 ocr 相关能力
    file_object = client.files.create(file=Path(title+".txt"), purpose="file-extract")

    # 获取结果
    # file_content = client.files.retrieve_content(file_id=file_object.id)
    # 注意，之前 retrieve_content api 在最新版本标记了 warning, 可以用下面这行代替
    # 如果是旧版本，可以用 retrieve_content
    file_content = client.files.content(file_id=file_object.id).text

    # 把它放进请求中
    messages=[
        {
            "role": "system",
            "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。",
        },
        {
            "role": "system",
            "content": file_content,
        },
        {"role": "user", "content": "总结下这篇文章按照如下格式输出:1.主题;2.摘要核心信息;3.金句;4.总结;5.标签;"},
    ]

    # 然后调用 chat-completion, 获取 kimi 的回答
    completion = client.chat.completions.create(
        model="moonshot-v1-32k",
        messages=messages,
        temperature=0.3,
    )
    print(completion.choices[0].message.content)
    xiaoyuzhou_result[title]=completion.choices[0].message.content


def create_task(FILE_PATH: str):
    create_data = {
        "lang": LANG,
    }
    files = {}
    create_url = "https://api.speechflow.io/asr/file/v1/create"
    if FILE_PATH.startswith('http'):
        create_data['remotePath'] = FILE_PATH
        print('submitting a remote file')
        response = requests.post(create_url, data=create_data, headers=headers)
    else:
        print('submitting a local file')
        create_url += "?lang=" + LANG
        files['file'] = open(FILE_PATH, "rb")
        response = requests.post(create_url, headers=headers, files=files)
    if response.status_code == 200:
        create_result = response.json()
        print(create_result)
        if create_result["code"] == 10000:
            task_id = create_result["taskId"]
        else:
            print("create error:")
            print(create_result["msg"])
            task_id = ""
    else:
        print('create request failed: ', response.status_code)
        task_id = ""
    return task_id

def query_task(title:str,task_id):
    query_url = "https://api.speechflow.io/asr/file/v1/query?taskId=" + task_id + "&resultType=" + str(RESULT_TYPE)
    print('querying transcription result')
    while (True):
        response = requests.get(query_url, headers=headers)
        if response.status_code == 200:
            query_result = response.json()
            if query_result["code"] == 11000:
                print('transcription result:')
                d = json.loads(query_result['result'])
                list= d['sentences']
                file = open(title+'.txt', 'a',encoding="utf-8")
                for i in list:
                    line= i['s'].replace("萱姐","轩姐").replace("搞前局","搞钱局")
                    file.write(line+"\n")
                file.close()
                ai_result(title)
                break
            elif query_result["code"] == 11001:
                print('waiting')
                time.sleep(3)
                continue
            else:
                print(query_result)
                print("transcription error:")
                print(query_result['msg'])
                break
        else:
            print('query request failed: ', response.status_code)

def xiaoyuzhou_async(title:str,FILE_PATH: str):
    print("title:"+title)
    print("url:"+FILE_PATH)
    task_id = create_task(FILE_PATH)
    if (task_id != ""):
        query_task(title,task_id)

@app.get("/api/async_result")
def async_result_function(id:str):
    if dict_result[id] is None:
        return {"message": "async"}
    else:
        return {"message": dict_result[id]}

xiaoyuzhou_result={}

dict_result={}

def do_some_time_consuming_work(id: str):
    print("do_some_time_consuming_work:"+id)
    time.sleep(30)
    dict_result[id]="123"

@app.get("/api/async")
async def async_function(id:str):
    dict_result[id]=None
    executor.submit(do_some_time_consuming_work, id)
    return {"message": id}

@app.get("/ai/ocr")
def ai_ocr(img: str):
    client = OpenAI(api_key="1yV6GcI2IoZtgBPSZUM3vYnKr54fYuiiSMREoPC81hfBfVcpwy6MINITZRqEA0ixl", base_url="https://api.stepfun.com/v1")

    completion = client.chat.completions.create(
        model="step-1v-32k",
        messages=[
            {
                "role": "system",
                "content": "你是由阶跃星辰提供的AI聊天助手，你除了擅长中文，英文，以及多种其他语言的对话以外，还能够根据用户提供的图片，对内容进行精准的内容文本描述。在保证用户数据安全的前提下，你能对用户的问题和请求，作出快速和精准的回答。同时，你的回答和建议应该拒绝黄赌毒，暴力恐怖主义的内容",
            },
            {"role": "user", "content": "你好呀!"},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "解析下这张图片里的文字,输出格式为:图片文字：java",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://img-blog.csdnimg.cn/img_convert/2393f6e16cfb4c8f826310799b534f7d.png"
                        },
                    },
                ],
            },
        ],
    )

    print(completion.choices[0].message)
    return {"ocr": completion.choices[0].message}   