import os

import pymysql
import ttkbootstrap as ttk
from playsound import playsound
from ttkbootstrap.dialogs import Querybox
root = ttk.Window()

result=Querybox.get_string(
    prompt="请输入歌曲名称：",
    title="歌曲查询： ",
)


def getTextInput(result):

    print(result)  # 输出结果
    db = pymysql.connect(host='localhost', user='root', password='123456', database='user')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    # 使用 execute()  方法执行 SQL
    result=result.strip('\n')
    result_='%'+result+'%'
    print(result)
    cursor.execute("select url from music where title like '%s'" % result_)
    # 使用 fetchone() 方法获取单条数据.
    data = cursor.fetchone()
    print('%s' % data)
    # 播放

    # 直接播放，不可停止，不方便演示
    # playsound('%s' % data)

    # 调用音乐播放器，名字里带符号的会出错
    os.system('%s' % data)

    # 加按钮用
    # import pygame
    # pygame.mixer.init()
    #
    # track = pygame.mixer.music.load('%s' % data)
    # pygame.mixer.music.play()
    #
    # pygame.mixer.music.pause()  # 暂停
    # pygame.mixer.music.unpause()  # 取消暂停
    # 成功播放音乐，并有暂停，取消暂停功能。

    # 关闭数据库连接
    if(db.close()):
        quit()


getTextInput(result)
root.mainloop()