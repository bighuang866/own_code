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

### 取数据

# 读取EXCEL里的数据，这里我们只读取1 2 5列，即开始日，截止日和成分股
raw_data = pd.read_excel("000905历史样本、行业分类.xls", usecols=[0, 1, 4])
# 读进的生效日数据全是数字，我们将其转换为字符串
# map函数接收一个函数作为参数，之后会将那个函数作用于series的每一个元素上，并返回新的series
raw_data["生效日"] = raw_data["生效日"].map(lambda x: "%8d" % x)
# 读进的截止日数据全是数字，我们将其转换为字符串
# 注意截止日这一列中有nan，所以定义的函数多了一步
raw_data["截止日"] = raw_data["截止日"].map(lambda x: "%8d" % x if not np.isnan(x) else np.nan)

# 证券代码由1， 600000这样的数字转换为000001.SZ,600000.SH，这里我们通过自定义的函数code_num2wind_code_str实现
raw_data["证券代码"] = raw_data["证券代码"].map(code_num2wind_code_str)

# 得到每一开始日对应的成分股方式一
# 新建一个字典，后续装入 键为调仓日，格式为8位字符串如："20080101"，
# 值为该调仓日调整后的成分股，格式为一个装有股票代码字符串的list如：["000001.SZ", "000002.SZ"...]
constitute = {}
# 在调仓日里进行循环，Series.unique函数会返回一个该Series不重复元素构建的列表
for start_date in raw_data["生效日"].unique():
    # 我们现在需要选取生效日等于start_date的所有成分股，因此我们选取"证券代码"对应的列
    # 而在行上，我们需要使用bool索引，选取出raw_data["生效日"]列等于start_date的那些行
    tmp_ser = raw_data.loc[raw_data["生效日"] == start_date, "证券代码"]
    # 把这个Series转换成list，这里纯粹是个人喜欢，也可以直接往字典里存Series
    tmp_list = tmp_ser.tolist()
    # 以开始日为键，把这个list存入字典
    constitute[start_date] = tmp_list

# # 得到每一开始日对应的成分股方式二
# 这种方法就比较花式，暂时不要看，写在这只是为了说明pandas功能真的很强大
# constitute = raw_data.groupby("生效日").apply(lambda x: x.loc[:, "证券代码"].tolist()).to_dict()

# 从wind里取数据的过程
from WindPy import w # 导入wind的插件
# wind插件是需要初始化的，调用w.start()函数即可
w.start()

# 为了编制中证500波动率加权指数，我们需要每个调仓日时，中证500成分股的过去一年波动率数据（每个调仓日对应一个截面数据）
# 因此我们用for循环，每次循环取出一个调仓日的 截面波动率数据
# 新建一个新的字典，该字典用来装取得的数据，键为调仓日，
# 值为该调仓日的截面波动率数据，为一个Series，index为股票代码，值为股票代码对应的波动率数据
tmp_dict = {}
# 前面已经得到了包含每个调仓日的成分股的字典constitute
for date in constitute:
    # 对于每个调仓日，找到他一年前的日期
    date_minus1year = str(int(date)-10000)
    # wind的取数据函数需要的参数，具体见wind插件使用攻略
    para_str = "startDate=%s;endDate=%s;period=1;returnType=1" % (date_minus1year, date)
    # 用wss取出波动率数据，详细请见wind插件使用攻略
    _, tmp_df = w.wss(constitute[date], "stdevr", para_str, usedf=True)
    # 把tmp_df转换为Series之后，以调仓日为键，存入字典
    tmp_dict[date] = tmp_df.squeeze()

# 我们得到了一个字典tmp_dict，这个字典键为调仓日，值为一个个调仓日对应的zz500成分股的波动率数据，格式是Series，index为股票代码
# 用pd.concat函数可以将他们连接成一个有MultiIndex的Series
# 这个MultiIndex的第一层是调仓日，第二层是股票代码
ser_vol_long = pd.concat(tmp_dict, axis=0)

# 修改一下ser_vol_long的名字和ser_vol_long.index的名字
ser_vol_long.index.names = ["date", "code"]
ser_vol_long.name = "vol"

del w
# 存储工作空间所有数据，实际上，我们后面用到的就是ser_vol_long这个数据，
dill.dump_session("data.pkl")
# 将"data.pkl"里的数据读取进入工作空间
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
result_df.fillna(datetime.datetime.now().strftime("%Y%m%d"))

# 写入excel
result_df.to_excel("result.xlsx", index=False)



