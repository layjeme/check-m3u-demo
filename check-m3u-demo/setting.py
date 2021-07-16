import os
import time
def sleeptime(hour, min, sec):
    return hour * 3600 + min * 60 + sec

url_suffix_tuple = (".m3u", ",m3u8", ".txt")  # 定义资源文件后缀元组
default_processes = os.cpu_count()
customize_processes = 24
sleep_time = sleeptime(0, 0, 5) # 程序循环运行间隔，分别对应（时，分，秒），修改对应数字即可