from time import time
from fastapi import FastAPI, __version__,Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import requests

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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

templates = Jinja2Templates(directory="templates")

@app.get("/hello1/", response_class=HTMLResponse)
async def hello1(request: Request):
   return templates.TemplateResponse("hello1.html", {"request": request})

@app.get("/test/", response_class=HTMLResponse)
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

@app.get("/api/ai")
def ai_function(img: str):

    # OCR API 的密钥
    api_key = "K88294794488957"
    #image_url = "https://img-blog.csdnimg.cn/img_convert/9e12ef54e34d401db3e084404e7205bd.png"
    language = "chs"

    # 构造请求参数
    data = {
        "isOverlayRequired": "true",
        "url": img,
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

@app.get("/api/ocr")
def ocr(img: str):
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