from typing import Union

import uvicorn
from fastapi import FastAPI
from orjson import orjson
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from query_any_seat import query_any_seat
import traceback


app = FastAPI()
# 允许跨域
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 挂在静态文件目录 /web的文件,都去web目录下找
app.mount("/web", StaticFiles(directory="web"), name="web")


@app.get("/")
def read_root():
    # Redirect to /web/test.html
    return RedirectResponse(url="/web/main.html")


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None, p: int = 0):
    return {"item_id": item_id, "q": q, "p": p}


@app.get("/query_trains")
def read_item(station_start: str, station_end: str, date: str):
    return {"status": "success", "data": ["D2923", "D2924"]}


@app.get("/query_any_seat")
def read_item(
    station_start: str, station_end: str, date: str, filter_train_name, is_test=False
):
    """
    station_start = "赣榆"
    station_end = "常州"
    date = "2024-02-19"
    filter_train_names = ["D2923"]

    http://127.0.0.1:8081/query_any_seat?station_start=赣榆&station_end=常州&date=2024-02-19&filter_train_name=D2923
    """
    if is_test:
        # 返回data.json的数据
        with open("data.json", "r", encoding="utf-8") as f:
            data = f.read()
            return orjson.loads(data)

    print(station_start, station_end, date, filter_train_name)
    filter_train_names = (
        len(filter_train_name) > 0 and filter_train_name.split(",") or []
    )
    try:
        trains_df = query_any_seat(station_start, station_end, date, filter_train_names)
        trains_json_str = trains_df.to_json(orient="records", force_ascii=False)
        #     转json对象返回
        return {"status": "success", "data": orjson.loads(trains_json_str)}
    except Exception as e:
        # 打印异常堆栈
        traceback.print_exc()
        return {"status": "fail", "data": str(e)}


# ENTRYPOINT ["python", "main.py", "--port", "$HTTP_PORT"]
if __name__ == "__main__":
    # 获取参数列表, 启动参数第一个作为端口号
    import sys

    args = sys.argv
    # 获取-- port参数
    port = None
    if "--port" in args:
        port_index = args.index("--port")
        if len(args) > port_index + 1:
            port = int(args[port_index + 1])
    if port is None:
        port = 8081

    print("port:", port)
    uvicorn.run(app, host="0.0.0.0", port=port)
