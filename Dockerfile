FROM python:3.12.1-alpine3.19

# 先复制 requirements.txt 文件并安装依赖
COPY requirements.txt /tmp/
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && \
    apk add  --no-cache gcc python3-dev linux-headers musl-dev && \
    pip install -r /tmp/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 然后复制其余的文件
COPY . /app

ENV LANG C.UTF-8

WORKDIR /app

EXPOSE 8080

# 如果有传入HTTP_PORT参数，则使用传入的端口
ENTRYPOINT ["python", "main.py", "--port", "8080"]
