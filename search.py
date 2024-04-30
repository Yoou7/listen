import pymysql
# 打开数据库连接
# db = pymysql.connect("localhost", "root", "123456", "user")

from playsound import playsound

# -*- coding: utf-8 -*-

import tkinter as tk
# playsound('E:\桌面文件管理\LisM\music_mp3\紫荆花盛开.mp3')

# 第1步，建立窗口window
window = tk.Tk()  # 建立窗口window
# 第2步，给窗口起名称
window.title('示例1')  # 窗口名称
# 第3步，设定窗口的大小(长＊宽)
window.geometry("400x240")  # 窗口大小(长＊宽)
# 第4步，在图形化界面上设定一个文本框
textExample = tk.Text(window, height=10)  # 创建文本输入框
# 第5步，安置文本框
textExample.pack()  # 把Text放在window上面，显示Text这个控件
# 第6步，获取文本框输入
def getTextInput():
    result = textExample.get("1.0", "end")  # 获取文本输入框的内容
    print(result)  # 输出结果
    db = pymysql.connect(host='localhost', user='root', password='123456', database='user')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    # 使用 execute()  方法执行 SQL
    result=result.strip('\n')
    print(result)
    cursor.execute("select url from music where title='%s'" % result)
    # 使用 fetchone() 方法获取单条数据.
    data = cursor.fetchone()
    print('%s' % data)
    # 播放
    # playsound('E:\桌面文件管理\LisM\music_mp3\紫荆花盛开.mp3')
    playsound('%s' % data)
    # 关闭数据库连接
    db.close()

# Tkinter 文本框控件中第一个字符的位置是 1.0，可以用数字 1.0 或字符串"1.0"来表示。
# "end"表示它将读取直到文本框的结尾的输入。我们也可以在这里使用 tk.END 代替字符串"end"。
# 第7步，在图形化界面上设定一个button按钮（#command绑定获取文本框内容的方法）
btnRead = tk.Button(window, height=1, width=10, text="Read", command=getTextInput)  # command绑定获取文本框内容的方法
# 第8步，安置按钮
btnRead.pack()  # 显示按钮
# 第9步，
window.mainloop()  # 显示窗口
