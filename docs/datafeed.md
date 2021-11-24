# DataFeed - 数据服务


对于数据服务，vn.py提供了标准化的接口BaseDatafeed（位于vnpy.trader.datafeed中），实现了更加灵活的数据服务支持。在全局配置中，和数据服务相关的字段全部都以datafeed作为前缀。

具体字段含义如下：
- datafeed.name：数据服务接口的名称，必须为全称的小写英文字母；
- datafeed.username：数据服务的用户名；
- datafeed.password：数据服务的密码。

以上字段对于所有数据服务都是必填的，如果是token方式授权请填写在database.password字段中。目前VN Trader支持以下七种数据服务，**具体每个数据服务的细节可在对应的项目地址中找到**。

## RQData

米筐RQData一直以来都是我们vn.py官方团队长期推荐的数据服务，对于大部分个人投资者来说应该都是性价比比较高的选择：
- 项目地址：[vnpy_rqdata](https://github.com/vnpy/vnpy_rqdata)
- 数据分类：股票、期货、期权、基金和黄金TD
- 数据周期：日线、小时线、分钟线、TICK（实时更新）
- 注册申请：[RICEQUANT](https://www.ricequant.com/welcome/purchase?utm_source=vnpy)

**请注意，配置信息里的username和password不是米筐官网登录用的账号和密码。**


## UData

恒有数UData是由恒生电子最新推出的云端数据服务，提供不限次、不限量的多种金融数据获取：
- 项目地址：[vnpy_udata](https://github.com/vnpy/vnpy_udata)
- 数据分类：股票、期货
- 数据周期：分钟线（盘后更新）
- 注册申请：[恒有数UData](https://udata.hs.net/home)


## TuShare

TuShare是国内知名的开源Python金融数据接口项目，由大神Jimmy团队长期开发维护，除了行情数据外还提供许多另类数据：
- 项目地址：[vnpy_tushare](https://www.github.com/vnpy/vnpy_tushare)
- 数据分类：股票、期货
- 数据周期：日线、分钟线（盘后更新）
- 注册申请：[Tushare大数据社区](https://tushare.pro/)


## TQSDK
天勤TQSDK是由信易科技推出的Python程序化交易解决方案，提供当前所有可交易合约上市以来的全部历史数据获取：
- 项目地址：[vnpy_tqsdk](https://github.com/vnpy/vnpy_tqsdk)
- 数据分类：期货
- 数据周期：分钟线（实施更新）
- 注册申请：[天勤量化-信易科技(shinnytech.com)](https://www.shinnytech.com/tianqin)


## Wind
万得Wind对于在国内金融机构工作的从业者来说，已经是工作中的标准配置，不管是股票、债券还是商品市场的数据，Wind可以说是应有尽有：
- 项目地址：[vnpy_wind](https://github.com/vnpy/vnpy_wind)
- 数据分类：期货
- 数据周期：分钟线（实施更新）
- 注册申请：[Wind金融终端](https://www.wind.com.cn/newsite/wft.html)

## iFinD
同花顺iFinD是同花顺公司推出的面向专业机构用户的金融数据终端，且在过去几年中的市场占有率快速上升：
- 项目地址：[vnpy_ifind](https://github.com/vnpy/vnpy_ifind)
- 数据分类：期货
- 数据周期：分钟线（实施更新）
- 注册申请：[iFinD金融数据终端](http://www.51ifind.com/)

## Tinysoft
作为国内老牌金融数据公司的天软，其核心产品【天软.NET金融分析平台】（简称TinySoft），在券商研究所和自营领域积累了大量用户。翻看券商的金融工程研报时，经常会发现图表的备注信息中写有“以上数据来自天软”的数据来源说明：
- 项目地址：[vnpy_tinysoft](https://github.com/vnpy/vnpy_tinysoft)
- 数据分类：期货
- 数据周期：分钟线（实施更新）
- 注册申请：[天软.NET金融分析平台](http://www.tinysoft.com.cn/TSDN/HomePage.tsl)