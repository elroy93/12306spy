
# 停止IMAGE  名字叫做12306spy的容器
docker stop $(docker ps -a | grep 12306spy | awk '{print $1}')

docker run -d -p 8081:8080 12306spy

# registry.cn-hangzhou.aliyuncs.com/elroy93/12306spy