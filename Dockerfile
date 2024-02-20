FROM python:3.12

# 先复制 requirements.txt 文件并安装依赖
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# 然后复制其余的文件
COPY . /app

# 默认使用上海时区 + 阿里源
RUN echo "Asia/Shanghai" > /etc/timezone && dpkg-reconfigure -f noninteractive tzdata && \
    echo "deb https://mirrors.aliyun.com/debian/ buster main non-free contrib" > /etc/apt/sources.list

ENV LANG C.UTF-8

WORKDIR /app

EXPOSE 7456

# 如果有传入HTTP_PORT参数，则使用传入的端口
ENTRYPOINT ["python", "main.py", "--port", "8080"]