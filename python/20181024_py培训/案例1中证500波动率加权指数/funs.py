# -*- coding: utf-8 -*-
# @Time    : 2018/10/25 13:23
# @Author  : Big Huang
# @Email   : kenhuang866@qq.com
# @File    : funs.py
# @Software: PyCharm Community Edition


def code_num2wind_code_str(code_num):
    code_str = "%06d" % code_num
    if code_num < 600000:
        return code_str + ".SZ"
    else:
        return code_str + ".SH"