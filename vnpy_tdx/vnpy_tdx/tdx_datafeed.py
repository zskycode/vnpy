import warnings
from datetime import timedelta, datetime
from enum import Enum

from pytdx.hq import TdxHq_API
from pytz import timezone
from typing import Dict, List, Optional
from copy import deepcopy

import pandas as pd
import tushare as ts

from vnpy.trader.setting import SETTINGS
from vnpy.trader.datafeed import BaseDatafeed
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData, HistoryRequest
from vnpy.trader.utility import round_to

# 数据频率映射
INTERVAL_VT2TS = {
    Interval.MINUTE: "1min",
    Interval.HOUR: "60min",
    Interval.DAILY: "D",
    Interval.WEEKLY: "W",
    Interval.TICK: "1min"
}

# 股票支持列表
STOCK_LIST = [
    Exchange.SSE,
    Exchange.SZSE,
]

# 期货支持列表
FUTURE_LIST = [
    Exchange.CFFEX,
    Exchange.SHFE,
    Exchange.CZCE,
    Exchange.DCE,
    Exchange.INE,
]

# 交易所映射
EXCHANGE_VT2TS = {
    Exchange.CFFEX: "CFX",
    Exchange.SHFE: "SHF",
    Exchange.CZCE: "ZCE",
    Exchange.DCE: "DCE",
    Exchange.INE: "INE",
    Exchange.SSE: "SH",
    Exchange.SZSE: "SZ",
}

# 时间调整映射
INTERVAL_ADJUSTMENT_MAP = {
    Interval.MINUTE: timedelta(minutes=1),
    Interval.HOUR: timedelta(hours=1),
    Interval.DAILY: timedelta()
}

# 中国上海时区
CHINA_TZ = timezone("Asia/Shanghai")

freq_convert = {"1min": "1m", "5min": '5m', '15min': '15m',
                "30min": "30m", "60min": '60m', "D": "1d", "W": '1w', "M": "1M"}

freq_map = {'1min': 8, '5min': 0, '15min': 1, '30min': 2,
            '60min': 3, 'D': 4, 'W': 5, 'M': 6}


class Freq(Enum):
    Tick = "Tick"
    F1 = "1分钟"
    F5 = "5分钟"
    F15 = "15分钟"
    F30 = "30分钟"
    F60 = "60分钟"
    D = "日线"
    W = "周线"
    M = "月线"
    S = "季线"
    Y = "年线"


freq_map_jq = {'1min': Freq.F1, '5min': Freq.F5, '15min': Freq.F15, '30min': Freq.F30,
               '60min': Freq.F60, 'D': Freq.D, 'W': Freq.W, 'M': Freq.M}


def to_ts_symbol(symbol, exchange) -> Optional[str]:
    """将交易所代码转换为tdx代码"""
    # 股票
    if exchange in STOCK_LIST:
        ts_symbol = f"{symbol}.{EXCHANGE_VT2TS[exchange]}"
    # 期货
    elif exchange in FUTURE_LIST:
        ts_symbol = f"{symbol}.{EXCHANGE_VT2TS[exchange]}".upper()
    else:
        return None

    return ts_symbol


def to_ts_asset(symbol, exchange) -> Optional[str]:
    """生成tushare资产类别"""
    # 股票
    if exchange in STOCK_LIST:
        if exchange is Exchange.SSE and symbol[0] == "6":
            asset = "E"
        elif exchange is Exchange.SZSE and symbol[0] == "0" or symbol[0] == "3":
            asset = "E"
        else:
            asset = "I"
    # 期货
    elif exchange in FUTURE_LIST:
        asset = "FT"
    else:
        return None

    return asset


class TdxDatafeed(BaseDatafeed):
    """Tdx数据服务接口"""

    def __init__(self):
        """"""
        self.username: str = SETTINGS["datafeed.username"]
        self.password: str = SETTINGS["datafeed.password"]

        self.inited: bool = False

    def init(self) -> bool:
        """初始化"""
        if self.inited:
            return True

        # ts.set_token(self.password)
        # self.pro = ts.pro_api()
        self.api = TdxHq_API(heartbeat=True, auto_retry=True)
        self.inited = True

        return True

    def query_bar_history(self, req: HistoryRequest) -> Optional[List[BarData]]:
        """查询k线数据"""
        if not self.inited:
            self.init()

        symbol = req.symbol
        exchange = req.exchange
        interval = req.interval
        start = req.start.strftime("%Y%m%d")
        end = req.end.strftime("%Y%m%d")
        start_date = pd.to_datetime(start)
        end_date = pd.to_datetime(end)
        end_date = end_date+ timedelta(days=1)
        ts_symbol = to_ts_symbol(symbol, exchange)
        if not ts_symbol:
            return None

        asset = to_ts_asset(symbol, exchange)
        if not asset:
            return None

        ts_interval = INTERVAL_VT2TS.get(interval)
        if not ts_interval:
            return None

        adjustment = INTERVAL_ADJUSTMENT_MAP[interval]

        if (end_date - start_date).days * 5 / 7 > 1000:
            warnings.warn(f"{end_date.date()} - {start_date.date()} 超过1000个交易日，K线获取可能失败，返回为0")

        api = TdxHq_API(heartbeat=True, auto_retry=True)

        bar_dict: Dict[datetime, BarData] = {}
        bars: List[BarData] = []

        if api.connect('tdx.xmzq.com.cn', 7709):
            # data = api.to_df(api.get_security_bars(0, 0, '000001', 0, 800))
            to_tdx_market = lambda x: 1 if x[0] == "6" else 0
            freq = ts_interval
            begin_index = self.get_index(api, end_date, freq, symbol, to_tdx_market)


            end_index = 30
            # print(begin_index)

            count = (end_index - begin_index) * 800

            if count and count >= 800:
                all_step = int(count / 800)
                num = 0
                for step1 in range(0, all_step):
                    step = all_step - num
                    num += 1
                    if step == all_step:
                        rows = api.get_security_bars(freq_map[freq], to_tdx_market(symbol[:6]), symbol[:6],
                                                     begin_index + step * 800,
                                                     count - step * 800)
                        bars = self.build_bar(bars, freq, rows, symbol, exchange, interval, adjustment, bar_dict)
                    else:
                        rows = api.get_security_bars(freq_map[freq], to_tdx_market(symbol[:6]), symbol[:6],
                                                     begin_index + step * 800, 800)
                        bars = self.build_bar(bars, freq, rows, symbol, exchange, interval, adjustment, bar_dict)
                rows = api.get_security_bars(freq_map[freq], to_tdx_market(symbol[:6]), symbol[:6],
                                             begin_index + 0, 800)
                bars = self.build_bar(bars, freq, rows, symbol, exchange, interval, adjustment, bar_dict)
            else:
                rows = api.get_security_bars(freq_map[freq], to_tdx_market(symbol[:6]), symbol[:6], begin_index + 0,
                                             count)
                bars = self.build_bar(bars, freq, rows, symbol, exchange, interval, adjustment, bar_dict)

            if start_date:
                bars = [x for x in bars if x.datetime >= start_date]
            if "min" in freq:
                bars[-1].dt = self.bar_end_time(bars[-1].datetime, m=int(freq.replace("min", "")))
            bars = [x for x in bars if x.datetime <= end_date]
            api.disconnect()

        # bar_keys = bar_dict.keys()
        # bar_keys = sorted(bar_keys, reverse=False)
        # for i in bar_keys:
        #     data.append(bar_dict[i])

        return bars

    def get_index(self, api, end_date, freq, symbol, to_tdx_market):
        # 探测偏移量
        for step in range(0, 31):
            # print(step)
            bars = api.get_security_bars(freq_map[freq], to_tdx_market(symbol[:6]), symbol[:6], step * 800, 800)
            length = len(bars)
            dt = pd.to_datetime(bars[0]['datetime'])
            if dt is None:
                return -1
            # print(dt)
            if dt <= end_date:
                bars = [x for x in bars if pd.to_datetime(x['datetime']) <= end_date]
                # print("find")
                if length < 800:
                    return 0
                else:
                    return step * 800 + (800 - len(bars))
            else:
                continue

    def build_bar(self, bars, freq, rows, symbol, exchange, interval, adjustment, bar_dict):
        i = -1 + len(bars)
        if rows is None:
            return bars
        for row in rows:
            dt = pd.to_datetime(row['datetime'])
            dt = datetime.strptime(str(dt), "%Y-%m-%d %H:%M:%S") - adjustment

            if row["open"] is None:
                continue

            if int(row['vol']) > 0:
                i += 1
                bar: BarData = BarData(
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval,
                    datetime=dt,
                    open_price=round_to(row["open"], 0.000001),
                    high_price=round_to(row["high"], 0.000001),
                    low_price=round_to(row["low"], 0.000001),
                    close_price=round_to(row["close"], 0.000001),
                    volume=row["vol"],
                    turnover=row.get("amount", 0),
                    open_interest=row.get("oi", 0),
                    gateway_name="TS"
                )
                bars.append(bar)
                bar_dict[dt] = bar
        return bars

    def bar_end_time(self, dt: datetime, m=1):
        """获取 dt 对应的分钟周期结束时间

        :param dt: datetime
        :param m: int
            分钟周期，1 表示 1分钟，5 表示 5分钟 ...
        :return: datetime
        """
        dt = dt.replace(second=0, microsecond=0)
        dt_span = {
            60: ["01:00", "2:00", "3:00", '10:30', "11:30", "14:00", "15:00", "22:00", "23:00", "23:59"],
        }

        if m < 60:
            if (dt.hour == 15 and dt.minute == 0) or (dt.hour == 11 and dt.minute == 30):
                return dt

            delta_m = dt.minute % m
            if delta_m != 0:
                dt += timedelta(minutes=m - delta_m)
            else:
                dt += timedelta(minutes=m)
            return dt
        else:
            for v in dt_span[m]:
                hour, minute = v.split(":")
                edt = dt.replace(hour=int(hour), minute=int(minute))
                if dt <= edt:
                    return edt
        return dt
