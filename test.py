from orjson import orjson

with open("data.json", "r", encoding="utf-8") as f:
    data = f.read()
    orjson.loads(data)
    print(orjson.loads(data))

for i in range(0, 10):
    print(i)
