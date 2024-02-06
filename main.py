import httpx
import orjson
# 定义变量
import pandas as pd

station_start = "赣榆"
station_end = "常州"
date = "2024-02-19"
#过滤器, 可以根据时间, 价格, 车次进行过滤
filter_train_names = ["D2923"]