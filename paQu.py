import time,threading
import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
root = ttk.Window(size=(500,380))
root.title("爬取中...")
def _():
    f = ttk.Frame(root).pack(fill=BOTH, expand=YES)
    p1 = ttk.Progressbar(f, bootstyle=PRIMARY)
    p1.place(x=50, y=100, width=380, height=40)
    p1.start() #间隔默认为50毫秒（20步/秒）

    root.after(5000, root.destroy)

t = threading.Thread(target=_)
t.setDaemon(True)
t.start()

root.mainloop()

