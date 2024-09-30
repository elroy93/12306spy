import time

import orjson
import pandas as pd
import vthread

import utils

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("max_colwidth", 1000)


def query_booking_by_station_v3_for_pc(
    station_start: str, station_end: str, date: str
) -> list:
    """
    起点 : 终点 : 日期, 查询所有的车次信息
    """
    response = utils.post_request(
        "https://m.suanya.com/restapi/soa2/14666/json/GetBookingByStationV3ForPC",
        data={
            "ArriveStation": station_end,
            "ChannelName": "ctrip.pc",
            "DepartDate": date,
            "DepartStation": station_start,
        },
    )
    text = response.text
    data = orjson.loads(text)
    TrainItems = data["ResponseBody"]["TrainItems"]
    return TrainItems


def transform_booking_train_items_info_to_dataframe(
    train_items: list, should_transform=True
):
    """
    将车次信息转换成DataFrame
    """
    # 定义列名的中英文对照字典
    columns_chinese = {
        "StartStationName": "起点站",
        "EndStationName": "终点站",
        "train_number": "车次",
        "start_time": "开始时间",
        "end_time": "结束时间",
        "duration": "耗时",
        "first_class_price": "一等座价格",
        "first_class_seats": "一等座余票量",
        "second_class_price": "二等座价格",
        "second_class_seats": "二等座余票量",
    }
    if should_transform == False:
        columns_chinese = {}

    # 使用英文列名创建DataFrame
    data = [
        {
            "StartStationName": item["StartStationName"],
            "EndStationName": item["EndStationName"],
            "train_number": item["TrainName"],
            "start_time": item["StartTime"],
            "end_time": item["EndTime"],
            "duration": f'{item["UseTime"] // 60}小时{item["UseTime"] % 60}分钟',
            "first_class_price": next(
                (
                    ticket["Price"]
                    for ticket in item["TicketResult"]["TicketItems"]
                    if ticket["SeatTypeName"] == "一等座"
                ),
                None,
            ),
            "first_class_seats": next(
                (
                    ticket["Inventory"]
                    for ticket in item["TicketResult"]["TicketItems"]
                    if ticket["SeatTypeName"] == "一等座"
                ),
                None,
            ),
            "second_class_price": next(
                (
                    ticket["Price"]
                    for ticket in item["TicketResult"]["TicketItems"]
                    if ticket["SeatTypeName"] == "二等座"
                ),
                None,
            ),
            "second_class_seats": next(
                (
                    ticket["Inventory"]
                    for ticket in item["TicketResult"]["TicketItems"]
                    if ticket["SeatTypeName"] == "二等座"
                ),
                None,
            ),
        }
        for item in train_items
    ]

    train_list = pd.DataFrame(data)
    # 重命名列名 , 不会改变原来的列名
    return train_list.rename(columns=columns_chinese)


def query_stop_station_list(
    train_name: str, date: str, start_station: str, end_station: str
) -> list:
    """
    查询车次的停靠站点
    """
    start_end_ret = utils.post_request(
        "https://m.suanya.com/restapi/soa2/14666/json/GetTrainStopListV3",
        data={
            "TrainName": train_name,
            "DepartStation": start_station,
            "ArrStation": end_station,
            "DepartureDate": date,
        },
    )
    text = start_end_ret.text
    data = orjson.loads(text)
    train_stop_list = data["TrainStopList"]
    return train_stop_list


def query_any_seat(
    station_start,
    station_end,
    date,
    filter_train_names=None,
    time_range="00:00 - 23:59",
):
    print("query_any_seat", station_start, station_end, date, filter_train_names)

    trainItems_all = []
    try:
        response = utils.post_request(
            "https://m.suanya.com/restapi/soa2/14666/json/GetBookingByStationV3ForPC",
            data={
                "ArriveStation": station_end,
                "ChannelName": "ctrip.pc",
                "DepartDate": date,
                "DepartStation": station_start,
            },
        )
        data = orjson.loads(response.text)
        trainItems_all = data["ResponseBody"]["TrainItems"]
    except Exception as e:
        raise Exception("服务器请求失败,请稍后再试")

    if len(trainItems_all) == 0:
        raise Exception("没有找到车次")

        # 根据时间进行过滤
    if time_range:
        time_range_list = time_range.split(" - ")
        print("time_range_list", time_range_list)
        start_time = time_range_list[0]
        end_time = time_range_list[1]
        trainItems_all = [
            item
            for item in trainItems_all
            if start_time <= item["StartTime"] <= end_time
        ]

    if len(trainItems_all) == 0:
        raise Exception("没有找到车次")
    # 如果没有输入车次,则返回所有车次
    if utils.is_empty(filter_train_names) or utils.is_blank(filter_train_names[0]):
        train_items_df = transform_booking_train_items_info_to_dataframe(trainItems_all)
        # http://localhost:8081/web/main.html?station_start=赣榆&station_end=上海&date=2024-02-22&filter_train_name=D2131
        train_items_df.insert(
            10,
            "查询链接",
            train_items_df.apply(
                lambda x: f"/web/main.html?station_start={x['起点站']}&station_end={x['终点站']}&train_date={date}&filter_train_name={x['车次']}&auto_query=1",
                axis=1,
            ),
        )
        return train_items_df

    # 具体的车次,
    train_items = [
        item for item in trainItems_all if item["TrainName"] in filter_train_names
    ]

    if utils.is_empty(train_items):
        raise Exception("没有找到符合条件的车次")
    # train_items_df = transform_booking_train_items_info_to_dataframe(train_items)

    train_item = train_items[0]

    # 修改起点名称和终点名称, 因为同城多个站点, 但是名字不一样.
    station_start = train_item["StartStationName"]
    station_end = train_item["EndStationName"]
    # 获取二等座价格
    train_item_second_price = 1
    for ticket in train_item["TicketResult"]["TicketItems"]:
        if ticket["SeatTypeName"] == "二等座":
            train_item_second_price = ticket["Price"]
            break

    # transform_booking_train_items_info_to_dataframe([train_item])

    # 获取车次的停靠站点
    item_stop_list_stations = query_stop_station_list(
        train_item["TrainName"], date, station_start, station_end
    )

    item_stop_list_station_df = pd.DataFrame(item_stop_list_stations)
    item_stop_list_station_df.insert(0, "车次", train_item["TrainName"])
    print("---- 停靠站列表 ----")
    print(item_stop_list_station_df)

    # stationName和始发站的映射关系的映射关系
    item_stop_list_station_name_departure_dict = {
        item["StationName"]: item["DepartureTime"] for item in item_stop_list_stations
    }
    if utils.is_debug():
        # 车站名称和出发时间的映射关系.
        item_stop_list_station_name_departure_dict_df = pd.DataFrame(
            item_stop_list_station_name_departure_dict.items(),
            columns=["站名", "出发时间"],
        )
        # 增加车次列在开头
        item_stop_list_station_name_departure_dict_df.insert(
            0, "车次", train_item["TrainName"]
        )
        print("---- 车站名称和出发时间的映射关系 ----")
        print(item_stop_list_station_name_departure_dict_df)

    # ----------------------- 计算车次的叉乘 -----------------------
    # [起始点, 上车站点] 和 (上车站点, 终点站] 两个列表中找出车次名称做叉乘, 得到所有的车次名称
    xlist = []
    item_stop_station_names = [item["StationName"] for item in item_stop_list_stations]
    start_station_index = 0  # 和middle_station_index可能相同
    middle_station_index = 0  # 和end_station_index一定不同
    end_station_index = 0
    for index, station_name in enumerate(item_stop_station_names):
        if station_start in station_name:
            middle_station_index = index
        if station_end in station_name:
            end_station_index = index
    # 两个队列的叉乘
    print(start_station_index, middle_station_index, end_station_index)
    index_generator = (i for i in range(0, 10000000))
    for i in range(middle_station_index, start_station_index - 1, -1):
        for j in range(len(item_stop_station_names) - 1, middle_station_index, -1):
            xlist.append([item_stop_station_names[i], item_stop_station_names[j]])
    if utils.is_debug():
        xlist_df = pd.DataFrame(xlist, columns=["起点", "终点"])
        xlist_df.insert(0, "原始车次", train_item["TrainName"])
        print("---- 车次的叉乘 ----")
        print(xlist_df)
    # ----------------------- 计算车次的叉乘 -----------------------

    if utils.is_empty(xlist):
        raise Exception("没有找到车次")

    xlist_item_results_df = []
    finished_index = []
    # 打印一下进度条
    print("开始查询车次信息, 总查询次数:", len(xlist))
    print("开始查询", len(xlist_item_results_df))

    # 多线程查询
    T1 = time.time()

    # ========================================== 多线程查询 ==========================================
    # ---- 10个线程同时查询 ----
    @vthread.pool(10)
    def xlist_item_job(index, xlist_item_start_station, xlist_item_end_station):
        xlist_item_train_items = query_booking_by_station_v3_for_pc(
            xlist_item_start_station, xlist_item_end_station, date
        )

        # 过滤出发车时间是之前dict中的时间的车次
        xlist_item_start_station_departure_time = (
            item_stop_list_station_name_departure_dict[xlist_item_start_station]
        )

        # 过滤出来需要的信息
        xlist_item_train_items = [
            item
            for item in xlist_item_train_items
            if str(item["StartTime"]) == str(xlist_item_start_station_departure_time)
            and item["EndStationName"] == xlist_item_end_station
            and item["StartStationName"] == xlist_item_start_station
        ]

        xlist_item_train_items_df = transform_booking_train_items_info_to_dataframe(
            xlist_item_train_items
        )
        # 如果没有找到车次,则直接返回
        if len(xlist_item_train_items_df) == 0:
            return

        # 过滤出来起点站名字和 xlist_item_start_station一样的车次
        xlist_item_train_items_df = xlist_item_train_items_df[
            xlist_item_train_items_df["起点站"] == xlist_item_start_station
        ]

        xlist_item_results_df.append(xlist_item_train_items_df)
        finished_index.append(index)
        # ---- 10个线程同时查询 end ----

    # 并发查询
    for index, xlist_item in enumerate(xlist):
        xlist_item_start_station = xlist_item[0]
        xlist_item_end_station = xlist_item[1]
        xlist_item_job(index, xlist_item_start_station, xlist_item_end_station)

    # 等待所有线程结束
    vthread.pool.wait()
    T2 = time.time()
    print(
        f"查询结束,cost= {int((T2 - T1) * 1000)} ms,  查询数量{len(xlist_item_results_df)},\n {finished_index}"
    )
    # ========================================== 多线程查询 end ==========================================

    # 将xlist_item_results合并成一个df, 并且生成index
    xlist_item_results_df = pd.concat(xlist_item_results_df, ignore_index=True)
    # 增加原始车次列
    xlist_item_results_df.insert(0, "原始车次", train_item["TrainName"])
    print("item_stop_station_names", item_stop_station_names)
    print("xlist_item_results_df", xlist_item_results_df)
    # item_stop_station_names中有站名, 按照xlist_item_results_df中的终点站和起点站进行排序, 先按照站名在item_stop_station_names中越靠后则优先级越高. 终点站比较特殊,按照靠近配置中的终点站的距离排序.
    xlist_item_results_df["起点站优先级"] = xlist_item_results_df["起点站"].apply(
        lambda x: item_stop_station_names.index(x)
    )
    xlist_item_results_df["终点站优先级"] = xlist_item_results_df["终点站"].apply(
        lambda x: abs(
            item_stop_station_names.index(x)
            - item_stop_station_names.index(station_end)
        )
    )
    # 一等座价格排序优先级,
    xlist_item_results_df["一等座价格优先级"] = xlist_item_results_df[
        "一等座价格"
    ].apply(lambda x: 0 if x is None else x)
    xlist_item_results_df = xlist_item_results_df.sort_values(
        by=["终点站优先级", "一等座价格优先级", "起点站优先级"],
        ascending=[True, True, False],
    )
    # 移除两个优先级列
    xlist_item_results_df = xlist_item_results_df.drop(
        columns=["起点站优先级", "终点站优先级", "一等座价格优先级"]
    )
    # 增加一列, 拼接个http链接    https://www.suanya.com/pages/trainList?fromCn=日照西&toCn=苏州&fromDate=2024-02-19#:~:text=D2923
    xlist_item_results_df["车次链接"] = xlist_item_results_df.apply(
        lambda x: f'https://www.suanya.com/pages/trainList?fromCn={x["起点站"]}&toCn={x["终点站"]}&fromDate={date}#:~:text={x["车次"]}',
        axis=1,
    )
    xlist_item_results_df = xlist_item_results_df.reset_index(drop=True)

    # 保留一等座余量或者二等座余量大于0的车次
    # 打印一下战列列表
    # item_stop_station_names
    for index, station_name in enumerate(item_stop_station_names):
        print("", index, " : ", station_name)

    xlist_item_results_df_has_rest = xlist_item_results_df[
        (xlist_item_results_df["一等座余票量"] > 0)
        | (xlist_item_results_df["二等座余票量"] > 0)
    ]
    if len(xlist_item_results_df_has_rest) == 0:
        raise Exception("没有座位")

    # ==========================================  查询结束, 计算表格的输出信息 ==========================================
    start_station_index = item_stop_station_names.index(station_start)
    end_station_index = item_stop_station_names.index(station_end)

    xlist_item_results_df_has_rest_buy_more_1 = xlist_item_results_df_has_rest[
        "起点站"
    ].apply(lambda x: start_station_index - item_stop_station_names.index(x))
    xlist_item_results_df_has_rest_buy_more_2 = xlist_item_results_df_has_rest[
        "终点站"
    ].apply(lambda x: end_station_index - item_stop_station_names.index(x))

    xlist_item_results_df_has_rest.insert(
        5, "提前买", xlist_item_results_df_has_rest_buy_more_1
    )
    xlist_item_results_df_has_rest.insert(
        6, "少买", xlist_item_results_df_has_rest_buy_more_2
    )
    # 提前买和少买的绝对值加合,增加一列
    xlist_item_results_df_has_rest.insert(
        7,
        "提前买+少买",
        xlist_item_results_df_has_rest_buy_more_1.abs()
        + xlist_item_results_df_has_rest_buy_more_2.abs(),
    )
    # 增加原始车次的结束时间
    xlist_item_results_df_has_rest.insert(9, "原始车次结束时间", train_item["EndTime"])
    # 计算车次的时间区间和原始时间的重叠度,即当前车次的有效时间/原始需要的时间

    # 时间差值,需要字符串转换成时间
    from datetime import datetime

    # Convert strings to datetime objects
    train_item_start_time = datetime.strptime(train_item["StartTime"], "%H:%M")
    train_item_end_time = datetime.strptime(train_item["EndTime"], "%H:%M")
    train_time_diff = train_item_end_time - train_item_start_time
    train_time_diff_min = train_time_diff.total_seconds() / 60

    # 花钱的时间
    xlist_item_results_df_has_rest.insert(
        10,
        "支出总时间",
        xlist_item_results_df_has_rest.apply(
            lambda x: (
                max(datetime.strptime(x["结束时间"], "%H:%M"), train_item_end_time)
                - datetime.strptime(x["开始时间"], "%H:%M")
            ).total_seconds()
            / 60,
            axis=1,
        ),
    )
    # 花钱时间除以原始时间
    xlist_item_results_df_has_rest.insert(
        11,
        "无效时间比",
        xlist_item_results_df_has_rest.apply(
            lambda x: x["支出总时间"] / train_time_diff_min, axis=1
        ),
    )
    # 计算一下补票的时间,也就是需要站着的时间
    xlist_item_results_df_has_rest.insert(
        12,
        "站票时间(min)",
        xlist_item_results_df_has_rest.apply(
            lambda x: int(
                (
                    train_item_end_time
                    - min(
                        datetime.strptime(x["结束时间"], "%H:%M"), train_item_end_time
                    )
                ).total_seconds()
                / 60
            ),
            axis=1,
        ),
    )

    xlist_item_results_df_has_rest.insert(
        13,
        "二等座全程支出(元)",
        xlist_item_results_df_has_rest.apply(
            lambda x: int(x["无效时间比"] * train_item_second_price), axis=1
        ),
    )
    xlist_item_results_df_has_rest.insert(
        14,
        "多余支出(元)",
        xlist_item_results_df_has_rest.apply(
            lambda x: int(x["二等座全程支出(元)"] - train_item_second_price), axis=1
        ),
    )
    xlist_item_results_df_has_rest.insert(
        9,
        "支出总时间/路程时间",
        xlist_item_results_df_has_rest.apply(
            lambda x: str(int(x["支出总时间"])) + "/" + str(int(train_time_diff_min)),
            axis=1,
        ),
    )

    # 移除掉购买链接
    # xlist_item_results_df_has_rest = xlist_item_results_df_has_rest.drop(columns=["车次链接"])
    xlist_item_results_df_has_rest = xlist_item_results_df_has_rest.drop(
        columns=["耗时"]
    )
    # xlist_item_results_df_has_rest = xlist_item_results_df_has_rest.drop(columns=["开始时间"])
    xlist_item_results_df_has_rest = xlist_item_results_df_has_rest.drop(
        columns=["结束时间"]
    )
    xlist_item_results_df_has_rest = xlist_item_results_df_has_rest.drop(
        columns=["一等座价格"]
    )
    xlist_item_results_df_has_rest = xlist_item_results_df_has_rest.drop(
        columns=["二等座价格"]
    )
    xlist_item_results_df_has_rest = xlist_item_results_df_has_rest.drop(
        columns=["原始车次结束时间"]
    )
    xlist_item_results_df_has_rest = xlist_item_results_df_has_rest.drop(
        columns=["开始时间"]
    )
    xlist_item_results_df_has_rest = xlist_item_results_df_has_rest.drop(
        columns=["支出总时间"]
    )
    xlist_item_results_df_has_rest = xlist_item_results_df_has_rest.rename(
        columns={"终点站": "补票站"}
    )
    xlist_item_results_df_has_rest = xlist_item_results_df_has_rest.rename(
        columns={"原始车次": "上车站车次"}
    )

    xlist_item_results_df_has_rest = xlist_item_results_df_has_rest.sort_values(
        by=["多余支出(元)"], ascending=[True]
    )

    print("------------------------")
    print("| 当前时间 : ", datetime.now().strftime("%H:%M:%S"), " | ")
    print("------------------------")

    xlist_item_results_df_has_rest = xlist_item_results_df_has_rest.reset_index(
        drop=True
    )
    xlist_item_results_df_has_rest
    return xlist_item_results_df_has_rest


def exe_main():
    station_start = "赣榆"
    station_end = "常州"
    date = "2024-02-07"
    filter_train_names = ["D2923"]
    trains_df = query_any_seat(
        station_start,
        station_end,
        date,
        filter_train_names,
        "00:00 - 23:59",
    )
    # df转json数组
    trains_json = trains_df.to_json(orient="records", force_ascii=False)
    print(trains_json)


# 赣榆 常州 2024-02-07 D2923
if __name__ == "__main__":
    exe_main()
