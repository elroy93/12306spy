
# 停止名字叫做12306spy的容器
docker stop 12306spy

docker run -d -p 8081:8080 -e HTTP_PORT=8080 12306spy