from tkinter import *
from ttkbootstrap import Style
import ttkbootstrap as ttk
from  ttkbootstrap.constants import *
import os

from ttkbootstrap.dialogs import Messagebox

root = Tk()
root.title("欢迎使用听歌识曲系统！")
# style = Style(theme='lumen')
# 加载图片
image1 = PhotoImage(file='drawable/intro_pic.gif')

# 显示图片
label1 = Label(root, image=image1)
label1.pack()

lab_1 = Label(root, text="选择所需功能", font=("微软雅黑", 20))
lab_1.pack()

def button1():
    os.system("python UI.py")

def button2():
    os.system("python search.py")

def button3():
    # os.system("python pachong.py")
    os.system("python paQu.py")
    os.system("python pachong.py")
    print("ok: ", Messagebox.ok(
        message="爬取成功！",
        title="提示",
        alert=False,  # 指定是否响铃，默认False
    ))


but_dr3 = ttk.Button(root, text="热歌爬取",bootstyle="DARK", command=button3)
but_dr3.pack(side=LEFT, padx=5, pady=10)
but_dr = ttk.Button(root, text="听歌识曲",bootstyle="DARK", command=button1)
but_dr.pack(side=LEFT, padx=5, pady=10)
but_dr2 = ttk.Button(root, text="歌曲查询",bootstyle="DARK", command=button2)
but_dr2.pack(side=LEFT, padx=5, pady=10)
root.mainloop()

