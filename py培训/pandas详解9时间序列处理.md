
# 时间序列的处理

在金融数据分析中，最经常遇到的数据就是金融时间序列

时间序列相较于普通的截面数据，有自身的一些特殊需求，如数据时间频率的转换，交易日非交易日的处理等等

pandas针对金融时间序列的特殊数据分析需求，专门开发了一系列用于时间处理的操作

但在学习这些操作之前，我们需要先了解，python是如何存储时间的。

## python的时间模块——datetime模块

在我们的数据库系统里，时间是一个很重要的组成部分，日常最方便的表示时间的方式就是8位字符串或者是8位数字

例如，2008年1月1日，可以用字符串表示为"20080101"，或用数字表示为20080101

但仅仅使用数字或字符串表示时间，仅仅具有 __区分功能__ ，而没有 __运算功能__

意思是可以通过字符串和数字的不同表示不同的时间，但是却无法进行时间的各种运算如时间偏移，频率转换

例如20080131之后一天，如果直接加1的话，得到的是20080132，不是一个合法的时间格式

然而自己写函数进行判断麻烦且没有必要，因为python通过datetime模块较好的解决了这个问题

首先我们import datetime模块


```python
import datetime
```

使用datetime模块里的datetime类可以表示时间


```python
dt = datetime.datetime(2008, 1, 1)
```

#### 注意是datetime模块里的datetime类，datetime.datetime才可以访问，很多初学者容易直接键入datetime

#### datetime是模块
#### datetime.datetime才是类

最简单的构造datetime的方式是通过构造函数（注意datetime.datetime的构造函数是支持输入小时和分钟，秒等的，但是我们基本上遇不到高频数据，所以在后面的分析中，我们不会接触到日频率以下的表示）

### 构建datetime对象及与时间字符串的转换

构建一个datetime对象可以通过以下几种方式：

1.直接调用datetime.datetime的构造函数


```python
dt = datetime.datetime(2008, 1, 1)
dt
```




    datetime.datetime(2008, 1, 1, 0, 0)



2.通过时间字符串格式化得到


```python
dt_str = "20090101"
dt = datetime.datetime.strptime(dt_str, "%Y%m%d")
dt
```




    datetime.datetime(2009, 1, 1, 0, 0)



%加字母用来表示时间格式  %Y表示4位数字年份，%m表示2位数字月份，%d表示2位数字的日期

%Y%m%d格式就会将前4位数字识别为年份，随后的2位数字识别为月份，再随后的2位数字识别为日期。  
如果字符串和格式不匹配就会报错


```python
dt_str = "20092-01-01"
dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d")
dt
```


    ---------------------------------------------------------------------------

    ValueError                                Traceback (most recent call last)

    <ipython-input-53-01e9af4fc2dc> in <module>()
          1 dt_str = "20092-01-01"
    ----> 2 dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d")
          3 dt
    

    D:\IDE\anaconda\lib\_strptime.py in _strptime_datetime(cls, data_string, format)
        563     """Return a class cls instance based on the input string and the
        564     format string."""
    --> 565     tt, fraction = _strptime(data_string, format)
        566     tzname, gmtoff = tt[-2:]
        567     args = tt[:6] + (fraction,)
    

    D:\IDE\anaconda\lib\_strptime.py in _strptime(data_string, format)
        360     if not found:
        361         raise ValueError("time data %r does not match format %r" %
    --> 362                          (data_string, format))
        363     if len(data_string) != found.end():
        364         raise ValueError("unconverted data remains: %s" %
    

    ValueError: time data '20092-01-01' does not match format '%Y-%m-%d'



```python
dt_str = "2009-01-31"
dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d")
dt
```




    datetime.datetime(2009, 1, 31, 0, 0)



当然除了这三个时间格式还有很多其他的时间格式

%y 两位数的年份表示（00-99） 

%Y 四位数的年份表示（0000-9999）

%m 月份（01-12）

%d 月内中的一天（00-31）

%H 24小时制小时数（00-23）

%I 12小时制小时数（01-12）

%M 分钟数（00-59）

%S 秒（00-59）

%a 本地简化星期名称 (Thu)

%A 本地完整星期名称 (Thursday)

%b 本地简化的月份名称 (Jan)

%B 本地完整的月份名称 (January)

%c 本地相应的日期表示和时间表示 (Thu Jan  1 00:00:00 2009)

%j 年内的一天（001-366）

%p 本地A.M.或P.M.的等价符

%U 一年中的星期数（00-53）星期天为星期的开始

%w 星期（0-6），星期天为星期的开始

%W 一年中的星期数（00-53）星期一为星期的开始

%x 本地相应的日期表示 (01/31/09)

%X 本地相应的时间表示 (00:00:00)

%Z 当前时区的名称 

当然大多数我们都用不到

datetime.datetime.strptime方法用来将字符串转换为datetime.datetime对象       
也可以使用datetime.datetime.strftime方法将datetime.datetime对象转换成一定格式的字符串    
这种字符串与datetime.datetime对象的互相转换是非常常用的   


```python
dt
```




    datetime.datetime(2009, 1, 31, 0, 0)




```python
dt.strftime("%Y%m%d")
```




    '20090131'




```python
dt.strftime("%Y-%m-%d")
```




    '2009-01-31'




```python
dt.strftime("%Y-%m-%d %H:%M:%S")
```




    '2009-01-31 00:00:00'



例如，我们有一个列表里，全是8位字符串（例如"20090101"）的时间，想转换成靠直线连接年月日的字符串（"2009-01-01"）


```python
dt_str_list1 = ["20090101", "20090102", "20090103", "20090104", "20090105"]
dt_str_list2 = [datetime.datetime.strptime(dt_str, "%Y%m%d").strftime("%Y-%m-%d") for dt_str in dt_str_list1]
dt_str_list2
```




    ['2009-01-01', '2009-01-02', '2009-01-03', '2009-01-04', '2009-01-05']



### datetime对象的运算

对时间进行偏移运算，需要使用datetime.timedelta对象


```python
dt
```




    datetime.datetime(2009, 1, 31, 0, 0)




```python
dt + datetime.timedelta(1)
```




    datetime.datetime(2009, 2, 1, 0, 0)




```python
dt + datetime.timedelta(5)
```




    datetime.datetime(2009, 2, 5, 0, 0)




```python
dt + datetime.timedelta(1)*2
```




    datetime.datetime(2009, 2, 2, 0, 0)



## pandas对于时间的处理


```python
import pandas as pd
import numpy as np
```

当将一个全为datetime.datetime对象的集合数据结构转换为pandas中的数据类型时（Index Series），pandas会自动识别，并将其转换为特定类型

例如


```python
dt_list = [datetime.datetime(2008, 1, 1), datetime.datetime(2008, 1, 2), datetime.datetime(2008, 1, 3), datetime.datetime(2008, 1, 4)]
```


```python
dt_list
```




    [datetime.datetime(2008, 1, 1, 0, 0),
     datetime.datetime(2008, 1, 2, 0, 0),
     datetime.datetime(2008, 1, 3, 0, 0),
     datetime.datetime(2008, 1, 4, 0, 0)]




```python
pd.Series(dt_list)
```




    0   2008-01-01
    1   2008-01-02
    2   2008-01-03
    3   2008-01-04
    dtype: datetime64[ns]



注意这里的Series的dtype不是常见的int64 float64 object，而是专门用来存储时间的datetime64[ns]


```python
pd.Index(dt_list)
```




    DatetimeIndex(['2008-01-01', '2008-01-02', '2008-01-03', '2008-01-04'], dtype='datetime64[ns]', freq=None)



转换为Index则会自动识别时间并生成专用的DatetimeIndex，DatetimeIndex也是一种Index，Index有的属性和方法他都有，但是他还有Index没有的一些专门处理时间的属性和方法（实际上DatetimeIndex类是继承自Index类的，感兴趣的可以百度 python类的继承，不感兴趣可以无视）


当然有的时候是从一个全为时间字符串的集合数据结构进行转换的，pandas提供了to_datetime函数


```python
dt_str_list1 = ["20090101", "20090102", "20090103", "20090104", "20090105"]
dt_str_list2 = ["2009-01-01", "2009-01-02", "2009-01-03", "2009-01-04", "2009-01-05"]
dt_str_ser1 = pd.Series(dt_str_list1)
dt_str_ser2 = pd.Series(dt_str_list2)
```


```python
pd.to_datetime(dt_str_list1)
```




    DatetimeIndex(['2009-01-01', '2009-01-02', '2009-01-03', '2009-01-04',
                   '2009-01-05'],
                  dtype='datetime64[ns]', freq=None)




```python
pd.to_datetime(dt_str_list2)
```




    DatetimeIndex(['2009-01-01', '2009-01-02', '2009-01-03', '2009-01-04',
                   '2009-01-05'],
                  dtype='datetime64[ns]', freq=None)



转list会自动生成DatetimeIndex（因为大多数情况下我们将时间转换成pandas里的数据结构，都是想用作Index，所以pd.to_datetime函数设计的时候就默认了生成的数据结构）


```python
当然转Series就是
```


```python
pd.to_datetime(dt_str_ser1)
```




    0   2009-01-01
    1   2009-01-02
    2   2009-01-03
    3   2009-01-04
    4   2009-01-05
    dtype: datetime64[ns]




```python
pd.to_datetime(dt_str_ser2)
```




    0   2009-01-01
    1   2009-01-02
    2   2009-01-03
    3   2009-01-04
    4   2009-01-05
    dtype: datetime64[ns]



任何一种高级编程语言都有专门处理时间的方式，例如matlab通过datenum处理时间，在datenum上jia，
