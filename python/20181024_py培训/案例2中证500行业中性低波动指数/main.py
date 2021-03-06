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
from funs import code_num2wind_code_str
import dill
num_selected = 150


#
# #### 取数据
#
# # 读取EXCEL里的数据，这里我们只读取1 2 5列，即开始日，截止日和成分股
# raw_data = pd.read_excel("000905历史样本、行业分类.xls",usecols=[0, 1, 4, 10])
# # 读进的日期数据全是数字，我们将其转换为字符串
# raw_data["生效日"] = raw_data["生效日"].map(lambda x: "%8d" % x)
#
# raw_data["截止日"] = raw_data["截止日"].map(lambda x: "%8d" % x if not np.isnan(x) else np.nan)
#
# # 证券代码由1， 600000这样的数字转换为000001.SZ,600000.SH
# raw_data["证券代码"] = raw_data["证券代码"].map(code_num2wind_code_str)
#
# # 中证500行业从2008年开始的，因此之前的成分股没有该数据，暂时先剔除，若要使用后面行业数据前推，需要更多数据 详细说明
# raw_data.dropna(subset=["中证二级"], inplace=True)
#
# # 得到每一开始日对应的成分股方式一
# constitute = {}
# for start_date in raw_data["生效日"].unique():
#     tmp_list = raw_data.loc[raw_data["生效日"] == start_date, "证券代码"].tolist()
#     constitute[start_date] = tmp_list
#
# # # 得到每一开始日对应的成分股方式二
# # constitute = raw_data.groupby("生效日").apply(lambda x: x.loc[:, "证券代码"].tolist()).to_dict()
#
# # 从wind里取数据的过程
# from WindPy import w # wind的插件
# w.start()
# tmp_dict = {}
# for date in constitute:
#     print(date)
#     date_minus1year = str(int(date)-10000)
#     para_str = "startDate=%s;endDate=%s;period=1;returnType=1" % (date_minus1year, date)
#     _, tmp_df = w.wss(constitute[date], "stdevr", para_str, usedf=True)
#     tmp_dict[date] = tmp_df.squeeze()
#
# ser_vol_long = pd.concat(tmp_dict, axis=0)
# ser_vol_long.index.names = ["date", "code"]
# ser_vol_long.name = "vol"
#
#
# dill.dump_session("data.pkl")

dill.load_session("data.pkl")
# ser_vol_long是个长格式数据，与宽格式数据有明显不同
# df_vol_wide = ser_vol_long.unstack(1)


# ser_vol_long有股票的波动率数据，我们需要将这数据同raw_data join起来
df_vol_long = ser_vol_long.reset_index()
data_merged = pd.merge(raw_data, df_vol_long, left_on=["生效日", "证券代码"], right_on=["date", "code"])

data_merged.drop(["date", "code"], axis=1, inplace=True)
#### 选样


def mod_weight(weight_ser):
    int_sum = int(weight_ser.sum())
    # 对权重四舍五入
    tmp = weight_ser.sort_values().round()

    if tmp.sum() == int_sum:
        return tmp
    elif tmp.sum() > int_sum:
        return tmp
    elif tmp.sum() < int_sum:
        return tmp


# time1 = time.time()
# 利用数据从500的样本空间里选样
tmp_dict2 = {}
data_merged2 = data_merged.set_index(["生效日", "证券代码"])
for date in data_merged2.index.levels[0]:
    data_at_date = data_merged2.xs(date, level=0)
    # 这时候我们可以用排序再选择最小的100个，不过pandas有个现成的nsmallest函数
    zz500_industrys_count = data_at_date["中证二级"].value_counts()
    tmp = zz500_industrys_count * num_selected/zz500_industrys_count.sum()
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

