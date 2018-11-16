# -*- coding:utf-8 -*-

from enum import Enum
from abc import ABCMeta,abstractmethod

#
# class SqlTable(Enum):
#     @property
#     def __TABLE_NAME__(self):
#         raise NotImplementedError

sql_config_str = "oracle+cx_oracle://zszs:zszs@192.168.101.102:1521/orcl"


class BASICDATA(Enum):
    __TABLE_NAME__ = "BASICDATA"
    CODE = "DM"
    TRADE_DATE = "JYRQ"
    FREE_FLOAT_SHARES = "CE_JQGB"






