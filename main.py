from time import time
from fastapi import FastAPI, __version__,Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import requests

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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