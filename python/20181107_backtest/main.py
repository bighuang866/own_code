# -*- coding:utf-8 -*-
import pandas as pd
import numpy as np
import cx_Oracle
import datetime
from enum import Enum

# position = pd.read_excel("position.xlsx")
# position = pd.DataFrame()
# position.index.name = TRADEDATE_COL
# position.columns.name = CODE_COL
# db = cx_Oracle.connect('zszs/zszs@192.168.101.102:1521/orcl')

import sqlalchemy as sa
from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import create_engine
from sql_tables import BASICDATA, sql_config_str

base = declarative_base()


class ORMReprMixin:
    def __repr__(self):
        columns = [attr_name for (attr_name, attr_value) in BasicData.__dict__.items()
                    if isinstance(attr_value, sa.orm.attributes.InstrumentedAttribute)]

        elem_expr = ", ".join(["{column}: {column_val}".format(column=column,
                                                               column_val=self.__dict__[column])
                               for column in columns])

        return "{class_name}: ({elem_expr})".format(class_name=self.__class__.__name__,
                                                    elem_expr=elem_expr)


class BasicData(base, ORMReprMixin):
    __tablename__ = BASICDATA.__TABLE_NAME__
    code = Column(BASICDATA.CODE.value, Integer, primary_key=True)
    trade_date = Column(BASICDATA.TRADE_DATE.value, String, primary_key=True)
    free_float_shares = Column(BASICDATA.FREE_FLOAT_SHARES.value, Integer)


if __name__ == '__main__':
    import pandas as pd
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(sql_config_str, echo=True)
    # Session = sessionmaker()
    # Session.configure(bind=engine)
    # session = Session()

    # a = pd.read_sql_query(sa.select([BasicData]).where(BasicData.code=="600000").order_by(BasicData.trade_date), engine)
    a = pd.read_sql_query(sa.select([BasicData]).
                          where(BasicData.code.in_(["600000", "600001"]))
                          .order_by(BasicData.code, BasicData.trade_date),
                          engine)


