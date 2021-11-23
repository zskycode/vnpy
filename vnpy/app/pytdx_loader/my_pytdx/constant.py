# -*- coding:utf-8 -*-



from enum import Enum, unique


class KBarType(Enum):
    '''
    K 线种类
    0 -  5 分钟K 线
    1 -  15 分钟K 线
    2 -  30 分钟K 线
    3 -  1 小时K 线
    4 -  日K 线
    5 -  周K 线
    6 -  月K 线
    7 -  1 分钟
    8 -  1 分钟K 线
    9 -  日K 线
    10 - 季K 线
    11 - 年K 线
    '''
    KLINE_TYPE_5MIN = MINUTE_5 = 0
    KLINE_TYPE_15MIN = MINUTE_15 = 1
    KLINE_TYPE_30MIN = MINUTE_30 = 2
    KLINE_TYPE_1HOUR = HOUR = 3
    KLINE_TYPE_DAILY = DAILY = 4
    KLINE_TYPE_WEEKLY = WEEKLY = 5
    KLINE_TYPE_EXHQ_1MIN = MINUTE = 7
    KLINE_TYPE_1MIN = 8
    # vnpy.trade.constant 的 Interval 枚举类
    # 在 pytdxLoader 读取数据的时候, 将vnpy界面拿到的参数转成pytdx
    # MINUTE_5 = 0
    # MINUTE_15 = 1
    # MINUTE_30 = 2
    # HOUR = 3

    KLINE_TYPE_MONTHLY = 6
    KLINE_TYPE_RI_K = 9
    KLINE_TYPE_3MONTH = 10
    KLINE_TYPE_YEARLY = 11


class FutureMarketCode(Enum):
    '''
    使用pytdx获取
    data_df = ex_api.to_df(ex_api.get_markets())
    '''
    CFFEX = 47  # 中国金融期货交易所(期货), 期权是 7
    SHFE = 30  # 上海期货交易所
    CZCE = 28  # 郑州商品交易所
    DCE = 29  # 大连商品交易所
    INE = 30  # 上海国际能源交易中心


if __name__ == '__main__':
    x = FutureMarketCode['SHFE'].value
    print(1)
