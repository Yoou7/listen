# -*- coding:utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import websocket
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
# 该模块为客户端和服务器端的网络套接字提供对传输层安全性(通常称为“安全套接字层”)
# 的加密和对等身份验证功能的访问。
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
import pyaudio

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识


class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"domain": "iat", "language": "zh_cn", "accent": "mandarin", "vinfo": 1, "vad_eos": 10000}

    # 生成url
    def create_url(self):
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url


# 收到websocket消息的处理
def on_message(ws, message):
    try:
        code = json.loads(message)["code"]
        sid = json.loads(message)["sid"]
        if code != 0:
            errMsg = json.loads(message)["message"]
            print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))

        else:
            data = json.loads(message)["data"]["result"]["ws"]
            result = ""
            for i in data:
                for w in i["cw"]:
                    result += w["w"]

            if result == '。' or result == '.。' or result == ' .。' or result == ' 。':
                pass
            else:
                t.insert(END, result)  # 把上边的标点插入到result的最后
                print("翻译结果: %s。" % (result))

    except Exception as e:
        print("receive msg,but parse exception:", e)


# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws):
    pass
    # print("### closed ###")


# 收到websocket连接建立的处理
def on_open(ws):
    def run(*args):
        status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧
        CHUNK = 520  # 定义数据流块
        FORMAT = pyaudio.paInt16  # 16bit编码格式
        CHANNELS = 1  # 单声道
        RATE = 16000  # 16000采样频率
        # 实例化pyaudio对象
        p = pyaudio.PyAudio()  # 录音
        # 创建音频流
        # 使用这个对象去打开声卡，设置采样深度、通道数、采样率、输入和采样点缓存数量
        stream = p.open(format=FORMAT,  # 音频流wav格式
                        channels=CHANNELS,  # 单声道
                        rate=RATE,  # 采样率16000
                        input=True,
                        frames_per_buffer=CHUNK)

        print("- - - - - - - Start Recording ...- - - - - - - ")

        for i in range(0, int(RATE / CHUNK * 60)):
            # # 读出声卡缓冲区的音频数据
            buf = stream.read(CHUNK)
            if not buf:
                status = STATUS_LAST_FRAME
            if status == STATUS_FIRST_FRAME:

                d = {"common": wsParam.CommonArgs,
                     "business": wsParam.BusinessArgs,
                     "data": {"status": 0, "format": "audio/L16;rate=16000",
                              "audio": str(base64.b64encode(buf), 'utf-8'),
                              "encoding": "raw"}}
                d = json.dumps(d)
                ws.send(d)
                status = STATUS_CONTINUE_FRAME
                # 中间帧处理
            elif status == STATUS_CONTINUE_FRAME:
                d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                              "audio": str(base64.b64encode(buf), 'utf-8'),
                              "encoding": "raw"}}
                ws.send(json.dumps(d))

            # 最后一帧处理
            elif status == STATUS_LAST_FRAME:
                d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                              "audio": str(base64.b64encode(buf), 'utf-8'),
                              "encoding": "raw"}}
                ws.send(json.dumps(d))
                time.sleep(1)
                break

        stream.stop_stream()  # 暂停录制
        stream.close()  # 终止流
        p.terminate()  # 终止pyaudio会话
        ws.close()

    thread.start_new_thread(run, ())


def run():
    global wsParam
    # 讯飞接口
    wsParam = Ws_Param(APPID='60f58ebf',
                       APIKey='97914720395de683d5c88b86d7c51b8f',
                       APISecret='ZTM3NWFmMTE2Y2FmNDZiYWNhZDE5ZjI4')
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}, ping_timeout=2)


#

from tkinter import *
import threading  # 多线程
import tkinter

"""
setDaemon()方法
我们在程序运行中，执行一个主线程，如果主线程又创建一个子线程，
主线程和子线程就分兵两路，分别运行，那么当主线程完成想退出时，会检验子线程是否完成。
如果子线程未完成，则主线程会等待子线程完成后再退出。
但是有时候我们需要的是，只要主线程完成了，不管子线程是否完成，
都要和主线程一起退出，这时就可以用setDaemon方法啦
"""


# t = threading.Thread(target=run)


def thread_it(func, *args):
    t = threading.Thread(target=func, args=args)
    t.setDaemon(True)
    t.start()



# lambda匿名函数
"""
def thread_it(run,):
    t=threading.Thread(target=run,args=)
    t.setDaemon(True)
    t.start()
"""


from tkinter import *

import pymysql
from playsound import playsound
from ttkbootstrap import Style
import ttkbootstrap as ttk
from  ttkbootstrap.constants import *
import os

import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk

root = Tk()

root.title("歌曲查询")
root.geometry("300x300")
# 输入框
# text = tk.Text(root)
# text.configure(height=2,width=30)
#
# text.place(x=30,y=0)

# 语音按钮点击——开始识别



# 加载图片
photo = Image.open("drawable/语音.png")  # 括号里为需要显示在图形化界面里的图片
photo = photo.resize((20, 20))  # 规定图片大小
img0 = ImageTk.PhotoImage(photo)



#图片点击事件
button=tk.Button(root, image=img0, command=lambda: thread_it(run, ))
button.place(x=250, y=15)

# import ttkbootstrap as ttk
# from ttkbootstrap.constants import *
# e2 = ttk.Entry(root,width=30,bootstyle=PRIMARY)
# e2.grid(row=10, column=1, sticky=ttk.W, padx=10, pady=10)
#
# # 文字处理——去除符号、空格
# def remove_special_characters(text):
#     # 使用列表推导式删除特殊字符和标点符号
#     special_chars = [char for char in text if char.isalnum() or char.isspace()]
#     # 拼接列表中的字符并返回处理后的字符串
#     clean_text = ''.join(special_chars)
#     return clean_text
#
# def remove_spaces(text):
#     # 使用replace函数将空格替换为空字符串
#     text = text.replace(' ', '')
#     return text
#
#
# def get_entry_contetn():
#     # 调用函数删除特殊字符和标点符号
#     clean_string = remove_special_characters(e2.get())
#     # 调用函数删除空格
#     clean_string = remove_spaces(clean_string)
#     print("e2: ",clean_string)
#
#     # 连接数据库查询歌曲
#     db = pymysql.connect(host='localhost', user='root', password='123456', database='user')
#     # 使用 cursor() 方法创建一个游标对象 cursor
#     cursor = db.cursor()
#     # 使用 execute()  方法执行 SQL
#     result = clean_string.strip('\n')
#     print(result)
#     cursor.execute("select url from music where title='%s'" % result)
#     # 使用 fetchone() 方法获取单条数据.
#     data = cursor.fetchone()
#     print('%s' % data)
#     # 播放
#     # playsound('E:\桌面文件管理\LisM\music_mp3\紫荆花盛开.mp3')
#     playsound('%s' % data)
#     # 关闭数据库连接
#     db.close()
#
#
# button1=ttk.Button(root,text="查询", bootstyle=(PRIMARY, "outline-toolbutton"),command=get_entry_contetn).grid(row=20, column=1, sticky=ttk.W, padx=10, pady=10)
#
#
# # #分割线
# # text1="------------------------------"
# # # 显示图片
# # label1 = Label(root, text=text1)
# # label1.place(x=0,y=50)

root.mainloop()


# #强行停止
while(1):
    pass