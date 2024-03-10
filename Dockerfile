# 使用轻量级的基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt .
# 使用中国大陆的源来加速pip安装，同时清理缓存以减小体积
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 将代码复制到/app中
COPY . .

# 设置环境变量
ENV LANG C.UTF-8

# 暴露端口
EXPOSE 8080

# 设置启动命令
ENTRYPOINT ["python", "main.py", "--port", "8080"]
