import os

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
root = ttk.Window()
from ttkbootstrap import Style
root.title("请选择查询方式")
root.geometry("500x500")


cbo = ttk.Combobox(
            master=root,
            bootstyle = 'minty',
            font = ("微软雅黑",12),
            values=['语音识别', '文字输入'],
        )
cbo.current(0) #首先展示values里面索引的对应的值
cbo.pack()
# cbo.set('set other')
def ensure(event):
    print(cbo.get())
    if (cbo.get() == "语音识别"):
        os.system("python search.py")
    else:
        os.system("python wenZi.py")
cbo.bind('<<ComboboxSelected>>', ensure)
root.mainloop()