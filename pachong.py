
import requests
from lxml import etree
import os
from pydub import AudioSegment
import wave
import pymysql
def trans_mp3_to_wav(filepath, hz):
    song = AudioSegment.from_mp3(filepath)
    song.export("Python研究者." + str(hz), format=str(hz))
# 热歌榜首页网址
url = 'https://music.163.com/discover/toplist?id=3778678'
# 歌曲下载链接前半部分
url_base = 'https://music.163.com/song/media/outer/url?id='
# U-A伪装，模拟浏览器
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'}
# 抓取网站信息并使用etree预处理数据
response = requests.get(url=url, headers=headers)
html = etree.HTML(response.text)
# 原始id、name列表（包含无关信息）
raw_id_list = html.xpath('//a[contains(@href, "song?")]/@href')
raw_name_list = html.xpath('//a[contains(@href, "song?")]/text()')
id_list = []
name_list = []
# 过滤无关信息，得到纯净列表
for id in raw_id_list:
    music_id = id.split('=')[1]
    if '$' not in music_id:
        id_list.append(music_id)
for music_name in raw_name_list:
    if '{' not in music_name:
        name_list.append(music_name)
 # 遍历所有歌曲
path = 'E:\\桌面文件管理\\LisM\\music_mp3'

# for i in range(len(id_list)):

for i in range(200):
    # 完整下载链接
    flag = 0
    music_url = url_base + id_list[i]
    # 对应歌曲名称
    music_name = name_list[i]
    separator = ' '

    music_name = music_name.split(separator, 1)[0]
    # print(music_name)  # 👉️ 'fql'

    filenames = os.listdir(path)
    for name in filenames:
        name = name.split(".")[0]  # 去后缀名
        if(name==music_name or music_name=='5:20AM'):
            flag=1
    # print(music_name+".mp3")
    if(flag==0):
        music = requests.get(url=music_url, headers=headers)
        # 以二进制形式写入到本文件夹的（具体保存路径可自己修改）
        with open('E:\\桌面文件管理\\LisM\\music_mp3/%s.mp3' % music_name, 'wb') as file:
            file.write(music.content)
            print('<%s>下载成功...' % music_name)
            # 保存到数据库
            db = pymysql.connect(host='localhost', user='root', password='123456', database='user')

            # 使用 cursor() 方法创建一个游标对象 cursor
            cursor = db.cursor()
            # 使用 execute()  方法执行 SQL 查询
            # print('%s' % music_name)
            insert_sql = "insert into music(title,url) values ('%s','E:\\\桌面文件管理\\\LisM\\\music_mp3\\\%s.mp3') " % (
            music_name, music_name)
            try:
                cursor.execute(insert_sql)
                db.commit()
                # cursor.execute("select *from music")
                # data=cursor.fetchall()
                # print(data)
            except:
                print("insert erro！")
                db.close()
            #
            # #转为wav保存
            # ### 参数1：音频路径， 参数2：转换后的格式
            # try:
            #     song = AudioSegment.from_mp3("E:\\桌面文件管理\\LisM\\music_mp3/%s.mp3" % music_name)
            #     song.export("E:\\桌面文件管理\\LisM\\music_wav/%s." % music_name + str("wav"), format=str("wav"))
            # except:
            #     print("Error:%s .mp3转化出错" % music_name)#判断出错，删去最后一首记录？重新执行？
            #     song.export("E:\\桌面文件管理\\LisM\\music_wav/%s." % music_name + str("wav"), format=str("wav"))
            #

        file.close()






