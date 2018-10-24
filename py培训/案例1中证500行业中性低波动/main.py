# -*- coding: utf-8 -*-
# @Time    : 2018/10/23 16:26
# @Author  : Big Huang
# @Email   : kenhuang866@qq.com
# @File    : main.py
# @Software: PyCharm Community Edition

import time
time1 = time.time()
import pandas as pd
from WindPy import w
w.start()
excel_file = pd.ExcelFile("历史权重.xls")
data = []
for sheet_name in excel_file.sheet_names:
    data.append(pd.read_excel(excel_file, sheet_name=sheet_name))

raw_df = pd.concat(data, axis=0)

raw_df.columns = raw_df.columns.str.split("\n").str[0]

raw_df["日期"] = pd.to_datetime(raw_df["日期"])
def code_num2wind_code_str(code_num):
    code_str = "%06d" % code_num
    if code_num < 600000:
        return code_str + ".SZ"
    else:
        return code_str + ".SH"
raw_df["成分券代码"] = raw_df["成分券代码"].map(code_num2wind_code_str)
raw_df.set_index(["成分券代码", "日期"], inplace=True)

df = raw_df.loc[:, ['收盘', '计算用市值', '权重(%)']]

for date in df.index.levels[1]:
    CSI1000_constituent = df.xs(date, axis=0, level=1).index.tolist()
    w.wss(CSI1000_constituent, "", )

df2 = df['权重(%)'].unstack(0)
df2.index =
print(time.time()-time1)






