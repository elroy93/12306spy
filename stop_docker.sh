
# 停止IMAGE  名字叫做12306spy的容器
docker stop $(docker ps -a | grep 12306spy | awk '{print $1}')
