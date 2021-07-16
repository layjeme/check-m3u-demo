import calendar

import setting
from m3u8integration import *
import multiprocessing
import pandas as pd
import time
import os
import shutil
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

#  m3u 的格式是名字一行，网址一行的
# 开头：每隔时间N，就自动进行一遍操作
# 1、判断资源文件夹是否存在，判断输出文件夹是否存在，是否存在文件result.m3u，如果存在则当作资源文件之一
# 2、从资源文件夹获取资源文件列表
# 3、遍历资源文件列表获取资源
# 4、利用pandas清洗资源
# 5、重新整理排序
# 6、 将最终结果输出result.m3u到指定文件夹（文件夹不存在则新建）
# 7、 将已识别的文件移到已识别文件夹
# 8、 将未识别的文件移到未识别文件夹


class M3u8CheckArrange:

    # 检测资源文件夹是否存在
    def check_resource_folder(self):  # OK

        #  判断资源文件夹是否存在，不存在则新建
        if not os.path.exists("source"):   # os.path.exists用于判断文件或者文件夹是否存在
            return False
        else:
            return True
    # 根据类型，移动到对应的文件夹，kind：1可用，0不可用
    def move_files(self, files_path, unknow_files_path):
        try:
            if files_path:
                # 判断资源文件夹是否存在
                if not os.path.exists("source_got"):
                    os.mkdir("source_got")
                # 获取source_got文件路径
                source_got_path = "source_got"
                # 移动操作
                for file_path in files_path:
                    shutil.move(file_path, source_got_path)
            if unknow_files_path:
                # 判断文件夹是否存在
                if not os.path.exists("source_unknow"):
                    os.mkdir("source_unknow")
                # 获取source_got文件路径
                source_unknow_path = "source_unknow"
                # 移动操作
                for unknow_file_path in unknow_files_path:
                    shutil.move(unknow_file_path, source_unknow_path)

        except Exception as e:
            print(e)




    # 将最终结果输出result.m3u到指定文件夹（文件夹不存在则新建）
    def check_export_folder(self,result):
        # 判断是否存在输出文件夹，不存在则创建
        if not os.path.exists("result"):
            os.mkdir("result")
        #  将m3u8链接内容保存到文件名为result_m3u文件
        try:
            ts = str(calendar.timegm(time.gmtime()))
            with open("result/result%s.m3u"% ts, "w", encoding="gbk", errors="ignore") as result_m3u:
                for resource_info in result:
                    result_m3u.write(resource_info + "\n")
            return True
        except Exception as e:
            print(e)
            return False



    # 获取资源文件名列表
    def get_resource_filename_lists(self):
        files_path = []
        unknow_files_path = []
        # 循环遍历资源文件夹，用os.walk()方法
        source_path = "source"
        for root, dirs, files in os.walk(source_path, False):  # False代表自下而上深度遍历；True代表自上而下深度遍历，默认True

            for file_name in files:
                file_path = os.path.join(root, file_name)

                # 判断文件扩展名，可以识别文件和无法识别文件，分类保存
                if file_path.endswith(setting.url_suffix_tuple):
                    files_path.append(file_path)
                else:
                    unknow_files_path.append(file_path)

        if files_path:
            all_files_path = (files_path, unknow_files_path)  # 将两个返回值封装成一个对象
            return all_files_path  # 返回可以识别和无法识别的文件路径列表
        else:
            print("资源文件夹是空的")
            exit()






    # 通过pandas对数据进行清洗
    # a、根据文件格式进行数据采集，形成DataFrame
    # b、对采集到的DataFrame进行数据清洗，统一格式
    # c、对DataFrame进行数据合并
    # d、对数据进行去重操作
    def pandas_data_washed(self, files_path):
        try:
            # pool = multiprocessing.Pool(processes=setting.processes)
            all_urls_df = pd.DataFrame()
            if files_path:
                for file_path in files_path:
                    with open(file_path, "r", encoding="utf-8") as f:
                        urls = []  # 创建一个空的资源信息列表，存放当前文件下的所有链接
                        twoline_url = []  # 创建一个空列表，用于存放两行信息格式的列表资源链接 [ [], [], ……]
                        for line in f.readlines():
                            line = line.strip("\n")
                            urls.append(line)

                        for number in range(len(urls)):
                            if "#EXTINF" in urls[number] and ("http" in urls[number + 1] or "https" in urls[number + 1]):  # 如果标题和url不在同一行
                                temporary_url = []  # 创建临时url列表
                                temporary_url.append(urls[number])
                                temporary_url.append(urls[number + 1])
                                twoline_url.append(temporary_url)  # 将所有两行格式的网址存入twoline_url中

                            elif ",http" in urls[number] or ",https" in urls[number]:  # 如果标题和链接在同一行
                                split_line = urls[number].strip().rsplit(",http")
                                twoline_url.append(split_line)
                        url_df = pd.DataFrame(twoline_url, columns=("title", "url"))  # 将读取到的数据转变成df表

                        all_urls_df = pd.concat([all_urls_df, url_df], ignore_index=True)  # 将所有的df表都拼接起来，同时重新整理一个新的index
            else:
                print("资源是空的")
                exit()
            # 对数据进行清洗

            # 1、删除标题列的前缀，让所有标题都不带前缀
            all_urls_df["title"] = all_urls_df["title"].str.split(r"#.*:|\s+|#").agg("".join)
            # 2、删除网址列的前缀，让所有网址都不带http
            all_urls_df["url"] = all_urls_df["url"].str.split(r"http|\s+").agg("".join)
            # 3、给标题列重新统一增加前缀
            all_urls_df["title"] = "#EXTINF:" + all_urls_df["title"].astype("str")
            # 4、给网址列重新统一增加前缀
            all_urls_df["url"] = "http" + all_urls_df["url"].astype("str")
            # 5、根据URL列删除重复的行，对结果重新排序
            all_urls_df.drop_duplicates(subset="url", keep="first", inplace=True, ignore_index=True)
            # 6、将资源信息表返回
            return all_urls_df

        except Exception as e:
            print(e)




    def check_resource(self):
        if not self.check_resource_folder():
            print("资源文件夹不存在")
            time.sleep(0.5)
            os.mkdir("source")
            print("已新建资源文件夹")
            time.sleep(0.5)
            print("请将需要整理的资源放入文件夹中")
            time.sleep(5)  #下次检测时间间隔5秒  下次将此设置调如入setting中
            exit()
        else:
            # files_path, unknow_files_path = self.get_resource_filename_lists()  # 获取资源文件格式支持的文件路径和不支持的文件路径
            all_files_path = self.get_resource_filename_lists()  # 获取资源文件格式支持的文件路径和不支持的文件路径

            # 将不支持的文件移动到不支持的文件夹
            return all_files_path
            # all_urls_df = self.pandas_data_washed(files_path)  # 返回所有URL资源信息表
            # # return all_urls_df, files_path, unknow_files_path
            # return all_urls_df, files_path, unknow_files_path




    def save_model(self, all_urls_df):
        # 删除不可以用的数据,并重置索引,两种方法都可以
        # all_urls_df = all_urls_df.loc[all_urls_df["status"] == True]
        all_urls_df.drop(all_urls_df[all_urls_df["status"] == False].index, inplace=True)

        # 重置索引号
        all_urls_df = all_urls_df.reset_index(drop=True)
        # print(all_urls_df)
        m3u_list = ["#EXTM3U"]
        for n in range(len(all_urls_df)):
            m3u_list.append(all_urls_df.loc[n, "title"])
            m3u_list.append(all_urls_df.loc[n, "url"])
        # print(m3u_list)

        # 格式重整为m3u格式
        # result = ["#EXTM3U"]
        # for n in range(len(all_urls_df)):
        #     result = result + all_urls_df[n, "title"] + "\n"

        if self.check_export_folder(m3u_list):
            print("输出完成")
            time.sleep(1)
            print("脱裤子")
            time.sleep(1)
            print("开撸")
            return True
        else:
            print("保存失败")



        # 将可用资源保存到result文件夹
        # all_urls_df.to_excel("test.xlsx")


def apply_dataframe_status(all_urls_df):
    # all_urls_df["status"] = (self.apply_dataframe_status(all_urls_df["url"]))
    all_urls_df["status"] = all_urls_df.apply(lambda x: get_dataframe_status(x["url"], ), axis=1)
    return all_urls_df


def check_urls_status(all_urls_df):
    new_urls_df = apply_dataframe_status(all_urls_df)
    return new_urls_df

def get_dataframe_status( url):
    if checkM3u8.check_url_ok(url):

        return True
    else:
        return False

# if __name__ == '__main__': # 一直在后台循环运行
#     while True:
#
#         # multiprocessing.set_start_method("spawn")
#         mp = multiprocessing.Pool(processes=setting.customize_processes)  # 自定义进程数
#         # mp = multiprocessing.Pool(processes=setting.default_processes) # 缺省进程数，跟着电脑的配置走
#         uncleaned_url = []
#         newurls = []
#         m3u8check = M3u8CheckArrange()
#         files_path, unknow_files_path = m3u8check.check_resource()
#         all_urls_df = m3u8check.pandas_data_washed(files_path)  # 返回所有URL资源信息表
#         if all_urls_df:
#             try:
#                 for i in range(len(all_urls_df)):
#                    all_urls_df.loc[i, "status"] = mp.apply_async(get_dataframe_status, (all_urls_df.loc[i, "url"],))
#                 mp.close()
#                 mp.join()
#                 # 将status中“值的对象”替换成值本身
#                 # print(all_urls_df)
#                 for i in range(len(all_urls_df)):
#                     all_urls_df.loc[i, "status"] = all_urls_df.loc[i, "status"].get()
#                 # 将结果保存，并将源文件移动到已经处理的文件夹
#                 if m3u8check.save_model(all_urls_df):
#                     m3u8check.move_files(files_path, unknow_files_path)
#             except Exception as e:
#                 print(e)
#         else:
#             print("没有可用资源")
#         time.sleep(setting.sleep_time)  # 循环执行，可以加入系统自启动
if __name__ == '__main__':
    # multiprocessing.set_start_method("spawn")
    mp = multiprocessing.Pool(processes=setting.customize_processes)  # 自定义进程数
    # mp = multiprocessing.Pool(processes=setting.default_processes) # 缺省进程数，跟着电脑的配置走
    uncleaned_url = []
    newurls = []
    m3u8check = M3u8CheckArrange()
    files_path, unknow_files_path = m3u8check.check_resource()

    all_urls_df = m3u8check.pandas_data_washed(files_path)  # 返回所有URL资源信息表


    try:
        for i in range(len(all_urls_df)):
           all_urls_df.loc[i, "status"] = mp.apply_async(get_dataframe_status, (all_urls_df.loc[i, "url"],))
        mp.close()
        mp.join()
        # 将status中“值的对象”替换成值本身
        # print(all_urls_df)
        for i in range(len(all_urls_df)):
            all_urls_df.loc[i, "status"] = all_urls_df.loc[i, "status"].get()
        # 将结果保存，并将源文件移动到已经处理的文件夹
        if m3u8check.save_model(all_urls_df):
            m3u8check.move_files(files_path, unknow_files_path)
    except Exception as e:
        print(e)
