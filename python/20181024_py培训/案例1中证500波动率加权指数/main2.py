# -*- coding: utf-8 -*-
# @Time    : 2018/10/30 19:01
# @Author  : Big Huang
# @Email   : kenhuang866@qq.com
# @File    : main2.py
# @Software: PyCharm Community Edition

# -*- coding: utf-8 -*-
# @Time    : 2018/10/23 16:26
# @Author  : Big Huang
# @Email   : kenhuang866@qq.com
# @File    : main.py
# @Software: PyCharm Community Edition


import pandas as pd
import numpy as np
# 从我们自定义的fun.py文件里将code_num2wind_code_str函数导入
from funs import code_num2wind_code_str
import dill
num_selected = 100

dill.load_session("data.pkl")
# ser_vol_long是个长格式数据，与宽格式数据有明显不同
# 有兴趣运行下面代码对比看看，还可以看长格式与宽格式那个notebook，无兴趣暂时不看
# df_vol_wide = ser_vol_long.unstack(1)

#### 选样

# time1 = time.time()
# 利用数据从500的样本空间里选样 # 方式1
# 新建一个空字典
tmp_dict2 = {}
# ser_vol_long.index有两层，第一层是调仓日，循环每个调仓日
for date in ser_vol_long.index.levels[0]:
    # 选取出这个调仓日对应的波动率数据
    vol_at_date = ser_vol_long.xs(date, level=0)
    # pandas有个现成的nsmallest函数，可以将波动率最小的100个股票及其对应的波动率选出来，生成一个新的Series
    sample_vol = vol_at_date.nsmallest(num_selected)
    # 用1除以波动率得到波动率倒数
    sample_vol_inv = 1/sample_vol # 波动率倒数
    # 用波动率倒数除以波动率倒数总和得到权重
    sample_weight = sample_vol_inv/sample_vol_inv.sum()
    # 把计算出来的权重存入字典
    tmp_dict2[date] = sample_weight

# 我们得到了一个字典tmp_dict2，这个字典键为调仓日，值为一个个调仓日对应的成分股及权重数据
# 用pd.concat函数可以将他们连接成一个有MultiIndex的Series
# 这个MultiIndex的第一层是调仓日，第二层是股票代码
weight_ser = pd.concat(tmp_dict2, axis=0)


# 利用数据从500的样本空间里选样 # 方式2
# 这种方法就比较花式，暂时不要看，写在这只是为了说明pandas功能真的很强大，三行代码就解决了
# samples_vols = ser_vol_long.groupby(level=0, group_keys=False).nsmallest(num_selected)
# samples_vol_invs = 1/samples_vols
# weight_ser2 = samples_vol_invs.div(samples_vol_invs.sum(level=0), level=0)


#### 将权重处理后存储
# 拿出所有的调仓日
dates = weight_ser.index.levels[0]
# 把weight_ser的MultiIndex变为两列，这样就生成了一个df
result_df = weight_ser.reset_index()
# 给列换个标签
result_df.columns = ["开始日期", "证券代码", "权重"]

# 定义一个函数，该函数的作用是输入一个调仓日，就返回该调仓日下个调仓日的前一天，
# 如果输入的是最后一个调仓日，由于没有下个调仓日了，就返回nan
# 这个函数的作用是生成开始日期对应的结束日期
# 暂时不用看里面的细节，因为涉及到一些python时间的处理。


def find_end_date(start_date):
    start_date_id = dates.get_loc(start_date)
    if start_date_id < dates.shape[0]-1:
        next_start_date_id = start_date_id + 1
        next_start_date = dates[next_start_date_id]
        end_date = (pd.to_datetime(next_start_date) - pd.Timedelta(days=1)).strftime("%Y%m%d")
        return end_date
    else:
        return np.nan


# 生成开始日期对应的结束日期列
end_date_ser = result_df["开始日期"].map(find_end_date)
# 将这一列插入到result_df中
result_df.insert(1, "结束日期", end_date_ser)
# 在result_df的第一列插入一列，标题是指数代码，指数代码为500LV，这是为了和研发的模块保持一致
result_df.insert(0, "指数代码", "500LV")
# 我们会发现，最后一个调仓日没有对应的截止日期，被填充为了nan，这里我们暂时把这些都填充为当前日期。
import datetime
now_time = datetime.datetime.now()
result_df.fillna(now_time.strftime("%Y%m%d"))

# 写入excel
result_df.to_excel("result.xlsx", index=False)
