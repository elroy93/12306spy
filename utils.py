import httpx

headers = {
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
}

debug = True


def post_request(url, data):
    """
    发送post请求, 返回的是response对象
    """
    resp = httpx.post(
        url,
        headers=headers,
        data=data,
    )
    if resp.status_code == 200:
        return resp
    else:
        raise Exception(f"请求失败,状态码:{resp.status_code}, url={url} data={data}")


def is_blank(s):
    return s is None or s.isspace()


def is_not_blank(s):
    return not is_blank(s)


def is_empty(arr):
    return arr is None or len(arr) == 0


def is_debug():
    return debug
