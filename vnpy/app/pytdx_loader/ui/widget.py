import traceback
from datetime import datetime, timedelta
from threading import Thread

import pandas as pd
import tushare as ts
from vnpy_ctabacktester.engine import EVENT_BACKTESTER_LOG

from vnpy.event import EventEngine, Event
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import get_database
from vnpy.trader.datafeed import get_datafeed
from vnpy.trader.engine import MainEngine
from vnpy.trader.object import HistoryRequest
from vnpy.trader.ui import QtCore, QtWidgets
from vnpy.trader.utility import extract_vt_symbol

from ..engine import APP_NAME
from ..my_pytdx.contracts import read_contracts_json_dict


class PytdxLoaderWidget(QtWidgets.QWidget):
    """"""
    signal_log = QtCore.pyqtSignal(Event)

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super().__init__()

        self.engine = main_engine.get_engine(APP_NAME)
        self.main_engine = main_engine
        self.event_engine = event_engine
        self.progress_bar_dict = {}
        self.init_ui()

        self.register_event()
        self.thread = None
        self.isRunnig = True
        self.count = 0

    def register_event(self):
        self.signal_log.connect(self.process_log_event)
        self.event_engine.register("tdxlog", self.signal_log.emit)

    def init_ui(self):
        """"""
        self.setWindowTitle("pytdx载入")
        # self.setFixedWidth(600)
        self.log_monitor = QtWidgets.QTextEdit()
        self.log_monitor.setMaximumHeight(400)
        vbox = QtWidgets.QVBoxLayout()

        vbox.addWidget(self.log_monitor)

        self.setWindowFlags(
            (self.windowFlags() | QtCore.Qt.CustomizeWindowHint)
            & ~QtCore.Qt.WindowMaximizeButtonHint)

        run_download = QtWidgets.QPushButton("自动下载数据.to_db")
        run_download.clicked.connect(self.run_downloading1)

        run_downloadstop = QtWidgets.QPushButton("自动下载数据停止")
        run_downloadstop.clicked.connect(self.run_downloading2)

        form_left = QtWidgets.QFormLayout()
        form_left.addRow(QtWidgets.QLabel())
        form_left.addRow(run_download)
        form_left.addRow(run_downloadstop)
        form_left_widget = QtWidgets.QWidget()
        form_left_widget.setLayout(form_left)
        vbox.addWidget(form_left_widget)

        self.setLayout(vbox)

    def onExchangeActivated(self, exchange_str):
        self.symbol_combo.clear()
        contracts_dict = read_contracts_json_dict()

        # 提取 contracts_dict 中信息变为 symbols_dict
        symbols_dict = {}
        for key, value in contracts_dict.items():
            if value["exchange"] in symbols_dict:
                symbols_dict[value["exchange"]].append(f"{key}.{value['name']}")
            else:
                symbols_dict[value["exchange"]] = [f"{key}.{value['name']}"]

        if exchange_str in symbols_dict:
            for symbol in symbols_dict[exchange_str]:
                self.symbol_combo.addItem(symbol, symbol)
        else:
            err_msg = f"{exchange_str} is not in pytdx market_code_info.json file!"
            QtWidgets.QMessageBox.information(self, "载入失败！", err_msg)
            self.write_log1(err_msg)

    def run_downloading2(
            self
    ):
        self.isRunnig = False
        self.thread = None

    def run_downloading1(
            self
    ):
        self.thread = Thread(
            target=self.run_downloading,
            args=(

            )
        )
        self.thread.start()

    def run_downloading(
            self
    ):

        ts.set_token('6a6c84ffeaa318f9a1d96414416feabc32bf52244ea2bfdd675959b9')
        # 初始化pro接口
        pro = ts.pro_api()
        df = pro.stock_basic(exchange='', list_status='L',
                             fields='ts_code,symbol,name,area,industry,list_date')
        records = df.to_dict('records')
        end_date: [str, datetime] = datetime.now()

        for row in records:
            if self.isRunnig:
                vt_symbol = row['ts_code']
                if vt_symbol[-2:] == "SZ":
                    vt_symbol = row['symbol'] + "." + "SZSE"
                elif vt_symbol[-2:] == "SH":
                    vt_symbol = row['symbol'] + "." + "SSE"
                intervals = ["1m", "1h", "d"]  # "w", "tick"
                for index in range(len(intervals)):
                    interval = intervals[index]
                    start = datetime.now() + timedelta(days=-365 * 10)

                    self.write_log1(f"{vt_symbol}-{interval}开始下载历史数据")

                    try:
                        symbol, exchange = extract_vt_symbol(vt_symbol)
                    except ValueError:
                        self.write_log1(f"{vt_symbol}解析失败，请检查交易所后缀")
                        return

                    req = HistoryRequest(
                        symbol=symbol,
                        exchange=exchange,
                        interval=Interval(interval),
                        start=start,
                        end=end_date
                    )

                    try:
                        data = get_datafeed().query_bar_history(req)

                        if data:
                            get_database().save_bar_data(data)
                            self.write_log1(f"{vt_symbol}-{interval}历史数据下载完成")
                        else:
                            self.write_log1(f"数据下载失败，无法获取{vt_symbol}的历史数据")
                    except Exception:
                        msg = f"数据下载失败，触发异常：\n{traceback.format_exc()}"
                        self.write_log1(msg)

    def load_data(self):
        """"""
        symbol_code = self.symbol_combo.currentData().split(".")[0]
        symbol_type = self.symbol_type.text()
        exchange = self.exchange_combo.currentData()
        interval = self.interval_combo.currentData()
        datetime_head = self.datetime_edit.text()
        open_head = self.open_edit.text()
        low_head = self.low_edit.text()
        high_head = self.high_edit.text()
        close_head = self.close_edit.text()
        volume_head = self.volume_edit.text()
        open_interest_head = self.open_interest_edit.text()
        datetime_format = self.format_edit.text()

        # to_db / to_csv
        click_button_text = self.sender().text().split('.')[1]

        symbol = symbol_code + symbol_type
        start, end, count = self.engine.load(
            symbol,
            exchange,
            interval,
            datetime_head,
            open_head,
            high_head,
            low_head,
            close_head,
            volume_head,
            open_interest_head,
            datetime_format,
            progress_bar_dict=self.progress_bar_dict,
            opt_str=click_button_text
        )

        msg = f"\
        执行成功\n\
        代码：{symbol}\n\
        交易所：{exchange.value}\n\
        周期：{interval.value}\n\
        起始：{start}\n\
        结束：{end}\n\
        总数量：{count}\n\
        "
        QtWidgets.QMessageBox.information(self, "载入成功！", msg)

    def write_log(self, msg):
        """"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"{timestamp}\t{msg}"
        self.log_monitor.append(msg)
        self.count = self.count + 1
        if self.count > 10:
            self.log_monitor.clear()
            self.count = 0

    def write_log1(self, msg: str):
        """"""
        event = Event("tdxlog")
        event.data = msg
        self.event_engine.put(event)

    def process_log_event(self, event: Event):
        """"""
        msg = event.data
        self.write_log(msg)
