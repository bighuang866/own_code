# -*- coding: utf-8 -*-
# @Time    : 2018/10/23 16:26
# @Author  : Big Huang
# @Email   : kenhuang866@qq.com
# @File    : main.py
# @Software: PyCharm Community Edition


import time # 用来统计代码运行花费时间
# 记录代码运行开始时间
time_code_start = time.time()
import pandas as pd
import datetime
import numpy as np
# from WindPy import w # wind的插件
from funs import code_num2wind_code_str

num_selected = 100
#### 取数据

# 读取EXCEL里的数据，这里我们只读取1 2 5列，即成分股信息
raw_data = pd.read_excel("000905历史样本、行业分类.xls",usecols=[0, 1, 4])
# 读进的日期数据全是数字，我们将其转换为字符串
raw_data["生效日"] = raw_data["生效日"].map(lambda x: "%8d" % x)
today = int(datetime.datetime.now().strftime("%Y%m%d"))
raw_data.fillna(today, inplace=True)
raw_data["截止日"] = raw_data["截止日"].map(lambda x: "%8d" % x)

# 证券代码由1， 600000这样的数字转换为000001.SZ,600000.SH
raw_data["证券代码"] = raw_data["证券代码"].map(code_num2wind_code_str)

# 得到每一天的成分股
constitute = raw_data.groupby("生效日").apply(lambda x: x.loc[:, "证券代码"].tolist())

# # 从wind里取数据的过程
# w.start()
# tmp_dict = {}
# for date in constitute.index:
#     print(date)
#     date_minus1year = str(int(date)-10000)
#     para_str = "startDate=%s;endDate=%s;period=1;returnType=1" % (date_minus1year, date)
#     _, tmp_df = w.wss(constitute[date], "stdevr", para_str, usedf=True)
#     tmp_dict[date] = tmp_df.squeeze()
#
# ser_vol_long = pd.concat(tmp_dict, axis=0)
# ser_vol_long.index.names = ["date", "code"]
# ser_vol_long.name = "vol"
# ser_vol_long.to_excel("中证500成分股过去1年波动率.xlsx")

ser_vol_long = pd.read_excel("中证500成分股过去1年波动率.xlsx", index_col=[0, 1], squeeze=True)
ser_vol_long.index.set_levels(ser_vol_long.index.levels[0].map(str), level=0, inplace=True)
# df_vol_wide = ser_vol_long.unstack(1)

#### 选样

# time1 = time.time()
# 利用数据从500的样本空间里选样
tmp_dict2 = {}
for date in ser_vol_long.index.levels[0]:
    vol_at_date = ser_vol_long.xs(date, level=0)
    # 这时候我们可以用排序再选择最小的100个，不过pandas有个现成的nsmallest函数
    sample_vol = vol_at_date.nsmallest(num_selected)
    # 我们最关键的是要得到权重
    sample_vol_inv = 1/sample_vol
    sample_weight = sample_vol_inv/sample_vol_inv.sum()
    tmp_dict2[date] = sample_weight
weight_ser = pd.concat(tmp_dict2, axis=0)

# time2 = time.time()
# samples_vols = ser_vol_long.groupby(level=0, group_keys=False).nsmallest(num_selected)
# samples_vol_invs = 1/samples_vols
# weight_ser2 = samples_vol_invs.div(samples_vol_invs.sum(level=0), level=0)
# time3 = time.time()
# print(time2-time1)
# print(time3-time2)


#### 将权重处理后存储

dates = weight_ser.index.levels[0]
result_df = weight_ser.reset_index()
result_df.columns = ["开始日期", "证券代码", "权重"]

def find_end_date(start_date):
    start_date_id = dates.get_loc(start_date)
    if start_date_id < dates.shape[0]-1:
        next_start_date_id = start_date_id + 1
        next_start_date = dates[next_start_date_id]
        end_date = (pd.to_datetime(next_start_date) - pd.Timedelta(days=1)).strftime("%Y%m%d")
        return end_date
    else:
        return np.nan

# result_df["结束日期"] = result_df["开始日期"].map(find_end_date)
end_date_ser = result_df["开始日期"].map(find_end_date)
result_df.insert(1, "结束日期", end_date_ser)
result_df.insert(0, "指数代码", "500LV")
# 接下来要填上结束日期
result_df.fillna("20181024")

result_df.to_excel("result.xlsx", index=False)

# 记录代码运行结束时间
time_code_end = time.time()
print("代码运行完毕，用时：%.7f s" % (time_code_end-time_code_start))

