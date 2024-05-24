from tkinter import *
from ttkbootstrap import Style
import ttkbootstrap as ttk
from  ttkbootstrap.constants import *
import os

from librosa_main import tiqu
# 创建窗口
from ttkbootstrap.dialogs import Messagebox


#听歌识曲界面
root2 = Tk()
root2.title("听歌识曲")
# 设置样式
style = Style(theme='minty')

# 加载图片
image = PhotoImage(file='drawable/music4.png')

# 显示图片
label = Label(root2, image=image)
label.pack()

# 标签文字
ttk.Label(root2, text="录音中......",bootstyle=DARK,font=("微软雅黑",20)).pack(padx=5,pady=10)


#实施爬取

# 指纹提取按钮
def button1():
    os.system("python librosa_music.py")
    print("retrycancel: ", Messagebox.yesno(message="提取完成！"))

ttk.Button(root2, text="音频指纹提取",bootstyle="info-solid",command=button1).pack(side=LEFT, padx=5,pady=10)

def button():
    os.system("python zhiwen.py")
ttk.Button(root2,text="点击识别",bootstyle=SUCCESS,command=button).pack(side=LEFT,padx=5,pady=10)


# 运行窗口
root2.mainloop()

