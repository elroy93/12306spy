import httpx
import orjson

# 定义变量
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("max_colwidth", 1000)


def query_booking_by_station_v3_for_pc(
    station_start: str, station_end: str, date: str
) -> list:
    response = httpx.post(
        "https://m.suanya.com/restapi/soa2/14666/json/GetBookingByStationV3ForPC",
        headers={
            "authority": "m.suanya.com",
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "max-age=0",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "if-modified-since": "Thu, 01 Jan 1970 00:00:00 GMT",
            "origin": "https://www.suanya.com",
            "referer": "https://www.suanya.com/",
            "sec-ch-ua": '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
        },
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


def query_booking_by_station_v3_for_pc_async(
    station_start: str, station_end: str, date: str
) -> list:
    query_booking_by_station_v3_for_pc(station_start, station_end, date)


def transform_booking_train_items_info_to_dataframe(train_items: list):
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
    start_end_ret = httpx.post(
        "https://m.suanya.com/restapi/soa2/14666/json/GetTrainStopListV3",
        headers={
            "authority": "m.suanya.com",
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "max-age=0",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "if-modified-since": "Thu, 01 Jan 1970 00:00:00 GMT",
            "origin": "https://www.suanya.com",
            "referer": "https://www.suanya.com/",
            "sec-ch-ua": '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
        },
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


def query_any_seat(station_start, station_end, date, filter_train_names=None):
    print("query_any_seat", station_start, station_end, date, filter_train_names)
    response = httpx.post(
        "https://m.suanya.com/restapi/soa2/14666/json/GetBookingByStationV3ForPC",
        headers={
            "authority": "m.suanya.com",
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "max-age=0",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "if-modified-since": "Thu, 01 Jan 1970 00:00:00 GMT",
            "origin": "https://www.suanya.com",
            "referer": "https://www.suanya.com/",
            "sec-ch-ua": '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
        },
        data={
            "ArriveStation": station_end,
            "ChannelName": "ctrip.pc",
            "DepartDate": date,
            "DepartStation": station_start,
        },
    )
    print(response.text)
    # 使用orgjson格式化输出
    text = response.text
    data = orjson.loads(text)
    TrainItems_all = None
    try:
        TrainItems_all = data["ResponseBody"]["TrainItems"]
    except Exception as e:
        raise Exception("服务器请求失败,请稍后再试")

    if len(TrainItems_all) == 0:
        raise Exception("没有找到车次")

    # 如果filter_train_names为空,则使用所有车次,直接返回transItems
    if filter_train_names == None or len(filter_train_names) == 0:
        train_items_df = transform_booking_train_items_info_to_dataframe(TrainItems_all)
        # 增加一列,拼接http链接, 跳转到当前页面的?station_start=赣榆&station_end=上海&train_date=2024-02-22&train_id=D2131.
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

    # filter_train_names
    TrainItems = [
        item for item in TrainItems_all if item["TrainName"] in filter_train_names
    ]

    if TrainItems == None or len(TrainItems) == 0:
        raise Exception("没有找到符合条件的车次")

    train_items_df = transform_booking_train_items_info_to_dataframe(TrainItems)
    # train_items_df.insert(0, "起点站", station_start)
    # train_items_df.insert(1, "终点站", station_end)
    train_items_df
    train_item = TrainItems[0]
    # 修改起点和终点名称
    station_start = train_item["StartStationName"]
    station_end = train_item["EndStationName"]
    # 获取二等座价格
    train_item_second_price = next(
        (
            ticket["Price"]
            for ticket in train_item["TicketResult"]["TicketItems"]
            if ticket["SeatTypeName"] == "二等座"
        ),
        None,
    )
    transform_booking_train_items_info_to_dataframe([train_item])

    item_stop_list_stations = query_stop_station_list(
        train_item["TrainName"], date, station_start, station_end
    )

    item_stop_list_station_df = pd.DataFrame(item_stop_list_stations)
    item_stop_list_station_df.insert(0, "车次", train_item["TrainName"])
    item_stop_list_station_df

    # stationName和始发站的映射关系的映射关系
    item_stop_list_station_name_departure_dict = {
        item["StationName"]: item["DepartureTime"] for item in item_stop_list_stations
    }

    item_stop_list_station_name_departure_dict_df = pd.DataFrame(
        item_stop_list_station_name_departure_dict.items(), columns=["站名", "出发时间"]
    )
    # 增加车次列在开头
    item_stop_list_station_name_departure_dict_df.insert(
        0, "车次", train_item["TrainName"]
    )
    item_stop_list_station_name_departure_dict_df

    # [起始点, 上车站点] 和 (上车站点, 终点站] 两个列表中找出车次名称做叉乘, 得到所有的车次名称
    item_stop_station_names = [item["StationName"] for item in item_stop_list_stations]
    # item_stop_station_names转成df
    pd.DataFrame(item_stop_station_names, columns=["站名"])

    # 按照起点名和终点名分成两个列表, 进行叉乘, 使用包含, 而不是index, 因为名字可能不一样,但是一定包含
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
    xlist = []
    index_generator = (i for i in range(0, 10000000))
    for i in range(middle_station_index, start_station_index - 1, -1):
        for j in range(len(item_stop_station_names) - 1, middle_station_index, -1):
            xlist.append([item_stop_station_names[i], item_stop_station_names[j]])

    xlist_df = pd.DataFrame(xlist, columns=["起点", "终点"])
    xlist_df.insert(0, "原始车次", train_item["TrainName"])
    xlist_df

    if len(xlist) == 0:
        raise Exception("没有找到车次")

    #
    import time
    import vthread

    xlist_item_results = []
    finished_index = []
    # 打印一下进度条
    print("开始查询车次信息, 总查询次数:", len(xlist))
    print("开始查询", len(xlist_item_results))

    # 多线程查询
    T1 = time.time()

    @vthread.pool(10)
    def xlist_item_job(index, xlist_item_start_station, xlist_item_end_station):
        xlist_item_train_items = query_booking_by_station_v3_for_pc(
            xlist_item_start_station, xlist_item_end_station, date
        )

        # 过滤出发车时间是之前dict中的时间的车次
        xlist_item_start_station_departure_time = (
            item_stop_list_station_name_departure_dict[xlist_item_start_station]
        )

        print(
            "开始查询",
            index,
            xlist_item_start_station,
            xlist_item_end_station,
            xlist_item_start_station_departure_time,
        )
        # 打印 xlist_item_train_items 的header
        print("** headers ** ", xlist_item_train_items[0].keys())
        xlist_item_train_items = [
            item
            for item in xlist_item_train_items
            if str(item["StartTime"]) == str(xlist_item_start_station_departure_time)
            and item["EndStationName"] == xlist_item_end_station
        ]

        xlist_item_train_items_df = transform_booking_train_items_info_to_dataframe(
            xlist_item_train_items
        )
        # 过滤出来起点站名字和 xlist_item_start_station一样的车次
        xlist_item_train_items_df = xlist_item_train_items_df[
            xlist_item_train_items_df["起点站"] == xlist_item_start_station
        ]
        # 给df增加一列, 起点站和终点站,放到开头
        # xlist_item_train_items_df.insert(0, "起点站", xlist_item_start_station)
        # xlist_item_train_items_df.insert(1, "终点站", xlist_item_end_station)
        xlist_item_results.append(xlist_item_train_items_df)
        finished_index.append(index)

    for index, xlist_item in enumerate(xlist):
        xlist_item_start_station = xlist_item[0]
        xlist_item_end_station = xlist_item[1]
        xlist_item_job(index, xlist_item_start_station, xlist_item_end_station)
    vthread.pool.wait()
    T2 = time.time()

    print(
        f"查询结束,cost= {int((T2 - T1) * 1000)} ms,  查询数量{len(xlist_item_results)},\n {finished_index}"
    )

    # 将xlist_item_results合并成一个df, 并且生成index
    xlist_item_results_df = pd.concat(xlist_item_results, ignore_index=True)
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
    xlist_item_results_df

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

    # 遍历xlist_item_results 计算一下多买了少买了几站, 多买的基站, 基于station_start, 多买的站点, 基于station_end, 在xlist_item_results_df_has_rest增加两列显示
    # Get the indices of station_start and station_end in the item_stop_station_names list
    start_station_index = item_stop_station_names.index(station_start)
    end_station_index = item_stop_station_names.index(station_end)

    # Calculate the number of extra stations bought based on station_start and station_end
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


# 赣榆 常州 2024-02-07 D2923
if __name__ == "__main__":
    station_start = "赣榆"
    station_end = "常州"
    date = "2024-02-07"
    filter_train_names = ["D2923"]
    trains_df = query_any_seat(station_start, station_end, date, filter_train_names)
    # df转json数组
    trains_json = trains_df.to_json(orient="records", force_ascii=False)
    print(trains_json)
