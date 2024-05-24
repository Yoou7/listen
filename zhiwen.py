# -*- coding: utf-8 -*-
import os

import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from playsound import playsound
from pydub import AudioSegment
import numpy as np
import hashlib
from scipy.ndimage import (binary_erosion,generate_binary_structure,iterate_structure)
from scipy.ndimage import maximum_filter
# from scipy.ndimage.morphology import (binary_erosion, generate_binary_structure, iterate_structure)
# from scipy.ndimage.filters import maximum_filter

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ttkbootstrap.dialogs import Messagebox

from ku import Songs, Fingerprints
import matplotlib
import pyaudio
import wave


def start_audio(time=15, save_file="recorder.wav"):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 48000
    RECORD_SECONDS = time  # 需要录制的时间
    WAVE_OUTPUT_FILENAME = save_file  # 保存的文件名
    p = pyaudio.PyAudio()  # 初始化
    print("开始录音")
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)  # 创建录音文件
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)  # 开始录音
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("停止")

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')  # 保存
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


# 55s

start_audio()

matplotlib.use('TkAgg')


# from fft.orm import Songs, fingerprints


def readMp3AndCovertWav(filename):
    song = AudioSegment.from_mp3(filename)
    song.export(filename + ".wav", format="wav")


def print2DArrLen(arr):
    print(len(arr))
    print(len(arr[0]))


def print2DArr(arr):
    for i in range(len(arr)):  # 控制行，0~2
        for j in range(len(arr[i])):  # 控制列
            num = int(arr[i][j])
            if (num < 0):
                print(0, end="")
            elif (num < 10):
                print(1, end="")
            elif (num < 20):
                print(5, end="")
            else:
                print(9, end="")
        print()


def getMD5_SHA256(filename_or_string, md5_sha256="sha256"):
    d = hashlib.md5() if md5_sha256 == "md5" else hashlib.sha256()
    # d = hashlib.md5("asfd".encode("utf-8")) if md5_sha256=="md5" else hashlib.sha256("asfd".encode("utf-8"))#加盐
    if os.path.isfile(filename_or_string):
        with open(filename_or_string, 'rb') as f:
            while True:
                buf = f.read(4096)
                if not buf:
                    break
                d.update(buf)
        return d.hexdigest()
    else:
        d.update(filename_or_string.encode('utf-8'))
        return d.hexdigest()


# 参数可以调整
def generateFingerprint(peaks):
    hashes = []
    for i in range(len(peaks) - 20):
        for j in range(20):
            t1 = peaks[i][0]
            t2 = peaks[i + j][0]
            freq1 = peaks[i][1]
            freq2 = peaks[i + j][1]
            t_delta = t2 - t1
            if t_delta >= 9 and t_delta <= 200:
                h = hashlib.sha256(("%s_%s_%s" % (str(freq1), str(freq2), str(t_delta))).encode())
                hashes.append((h.hexdigest()[0:32], t1))
    return hashes


# filename = "E:\\桌面文件管理\\LisM\\music_mp3\\小美满.mp3"
# filename="E:\\桌面文件管理\\LisM\\music_mp3\\紫荆花盛开.mp3"
# filename = "E:\桌面文件管理\LisM\music_mp3\苦茶子.mp3"
# filename="E:\桌面文件管理\LisM\music_mp3\如果爱忘了.mp3"
# filename="E:\桌面文件管理\LisM\music_mp3\向云端.mp3"
filename = "recorder.wav"
# filename="try.wav"
# op="save"
op = "match"
# readMp3AndCovertWav(filename)
# samplerate, data = wavfile.read(filename + ".wav")

audiofile = AudioSegment.from_file(filename)
data = np.fromstring(audiofile.raw_data, np.int16)
channels = []
for chn in range(audiofile.channels):
    channels.append(data[chn::audiofile.channels])
fs = audiofile.frame_rate
print(fs)

# fft size
fft = 4096
# 重叠
nlap = fft * 0.5
# print(channels[0])
nlap = int(nlap)
# 第一个返回值是短时傅里叶变换之后的二维数组，数组说明下方
spectrum, f, t = mlab.specgram(channels[0], NFFT=fft, window=mlab.window_hanning, Fs=fs, noverlap=nlap)

# print(f)
# print(t)

# 值转换 转为以10为底的对数值，并乘以10，如果为0，保持为0
spectrum = 10 * np.log10(spectrum, out=np.zeros_like(spectrum), where=(spectrum != 0))

"""
spectrums是二维数组，每一列包含一个短期局部时间的频率成分估计，时间沿列增加，频率沿行增加
[[][]]
列指的是每个数组的第一位 第二位 第三位 ....
行指的是spectrums[0 1 2 ...]
第一列可以认为是开始，最后一列是结束
第一行，就相当于最低频，也就是0Hz
最后一行，就是最高频，可以认为是22050Hz
"""
# print(spectrum[0])
# 构造一个拓扑结构，第一个参数是维度，第二个参数是联通性
"""
generate_binary_structure 这个比较容易理解，
首先无论是几维，最终每个单元的元素个数都是3
二维可以想象是3*3平面 9个点 联通性是1，和中心点无对角线的，都可以认为是联通的
三维可以想象成3*3*3立方体 27个点 
四维呢 没办法想象怎么办，也比较简单
四维是三个三维数组
"""
struct = generate_binary_structure(2, 2)
"""
相当于往外扩了10层，扩一层相当于加2，所以最终变成了21 2d数组，注意，小于2相当于没变化
"""
neighborhood = iterate_structure(struct, 10)
"""
计算局部峰值，注意，后面 == ，所以返回的是bool二维数组
"""
local_max = maximum_filter(spectrum, footprint=neighborhood) == spectrum
# background是bool二维数组， 0为true 非0false
background = (spectrum == 0)
eroded_background = binary_erosion(background, structure=neighborhood, border_value=1)
detected_peaks = local_max != eroded_background
"""
上面三步没什么用，因为spectrum中等于0的没有
二维数组，传一个boolean数组，
"""
amps = spectrum[detected_peaks]
# print(amps)
"""
np where 只有一个参数，二维bool数组
np.where(detected_peaks)
看API应该用
np.asarray([[False,True],[False,False]]).nonzero()
(array([0], dtype=int64), array([1], dtype=int64))
np.asarray([[True,True],[False,False]]).nonzero()
(array([0, 0], dtype=int64), array([0, 1], dtype=int64))
np.asarray([[True,False],[False,False]]).nonzero()
(array([0], dtype=int64), array([0], dtype=int64))
np.asarray([[True,False],[False,True]]).nonzero()
(array([0, 1], dtype=int64), array([0, 1], dtype=int64))
np.asarray([[True,False],[True,True]]).nonzero()
(array([0, 1, 1], dtype=int64), array([0, 0, 1], dtype=int64))
"""
freqs, times = np.asarray(detected_peaks).nonzero()
# print(freqs)
# print(times)t'r
# 拉平，为何要拉平？无效操作，shit
amps1 = amps.flatten()

# print(amps1 == amps)
# 过滤，可以减少点数，30可以近似理解为音强，强度越高，抗噪越强
filter_idxs = np.where(amps > 10)
# filter_idxs = np.asarray(amps > 10).nonzero()


freqs_filter = freqs[filter_idxs]
times_filter = times[filter_idxs]
# print(freqs_filter)
# print(times_filter)
# 转为坐标，但是是乱序
# print(list(zip(times_filter,freqs_filter)))
'''
>>>a = [1,2,3]
>>> b = [4,5,6]
>>> c = [4,5,6,7,8]
>>> zipped = zip(a,b)     # 打包为元组的列表
[(1, 4), (2, 5), (3, 6)]
'''
peaks = list(zip(times_filter, freqs_filter))
peaks.sort(key=lambda x: x[0])
# print(peaks)
'''
点准备好了，开始生成指纹
'''
hashs = generateFingerprint(peaks)
# print(hashs)

'''
生产hash，落库，此处要处理偏移量的问题
即歌曲的样本可能随机分布在整首歌曲的任何位置
我们把一首歌的指纹全部落库，需要记录指纹的偏移量
然后处理样本时，需要核对偏移量
'''

if op == "match":
    engine = create_engine('mysql+mysqlconnector://root:123456@localhost:3306/user')
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    ##匹配过程
    hash_map = {}
    for sample in hashs:
        fp = sample[0]
        sample_offset = int(sample[1])
        match_fps = session.query(Fingerprints).filter(Fingerprints.fingerprint == fp).all()
        for match_fp in match_fps:
            key = str(match_fp.song_id) + "_" + str(match_fp.offset - sample_offset)
            if key in hash_map.keys():
                hash_map[key] = hash_map[key] + 1
            else:
                hash_map[key] = 1;
    session.close()  # 字典按val排序
    # print(sorted(hash_map.items(), key=lambda kv: (kv[1], kv[0]), reverse=True))
    for k, v in sorted(hash_map.items(), key=lambda kv: (kv[1], kv[0]), reverse=True):
        print(f"第一组数据: 键={k}, 值={v}")
        my_str = k
        break
    # my_str = list(hash_map.keys())[0]
    print(my_str)
    separator = '_'
    result = my_str.split(separator, 1)[0]
    print(result)  # 👉️ 'fql'
    import pymysql

    # 连接数据库
    db = pymysql.connect(host='localhost', user='root', password='123456', database='user')
    cursor = db.cursor()
    # SQL 查询语句，查询user表
    sql = 'select title from music where (url=(select name from songs where id=%s))' % result

    # 执行sql语句查询
    cursor.execute(sql)

    # 这是获取表中第一个数据
    rest = cursor.fetchone()
    sql1 = 'select name from songs where id=%s' % result
    cursor.execute(sql1)
    data = cursor.fetchone()
    print('%s' % data)
    os.system('%s' % data)

    db.close()

    # 创建游标对象

    # print(session.query(Songs).filter_by(id==4).first())
    # dict_iter = iter(hash_map)
    # first_key = next(dict_iter)
    # first_value = hash_map[first_key]
    #
    # print("First element of the dictionary: ", (first_key, first_value))
    # print(hash_map.items())

else:
    engine = create_engine('mysql+mysqlconnector://root:123456@localhost:3306/user')
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    '''
    落库，mysql
    '''
    song = Songs(name=filename, filehash=getMD5_SHA256(filename), fingerprinted=True)
    # 创建DBSession类型:
    session.add(song)
    session.flush()
    new_song_id = song.id;
    # 保存本首歌的指纹
    for fp in hashs:
        fp_record = Fingerprints(song_id=new_song_id, fingerprint=fp[0], offset=int(fp[1]))
        session.add(fp_record)
    session.commit()
session.close()

# # 下面展示频谱图可以注掉，没什么用
#
# # print2DArrLen(spectrum)
# # scatter of the peaks
# fig, ax = plt.subplots()
# ax.imshow(spectrum)
# ax.scatter(times_filter, freqs_filter)
# ax.set_xlabel('Time')
# ax.set_ylabel('Frequency')
# ax.set_title("Spectrogram")
# plt.gca().invert_yaxis()
# plt.show()
# # print(freqs)
# # print(t)
# # spectrum2= plt.specgram(channels[0],NFFT=fft,window=mlab.window_hanning,Fs = fs,noverlap=nlap)
# # print(spectrum2)
# # plt.show()
rest = "".join(rest)
print(rest)
print("retrycancel: ", Messagebox.yesno(message="识别结果：" + rest))


# tiqu1()


