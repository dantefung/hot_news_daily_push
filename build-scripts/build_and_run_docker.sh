#!/bin/bash

# 构建镜像
IMAGE_NAME="hot-news-daily-push:latest"

echo "\n==> 构建 Docker 镜像: $IMAGE_NAME"
docker build -t $IMAGE_NAME .

# 检查.env文件
if [ -f .env ]; then
  ENV_ARG="--env-file .env"
  echo "使用.env文件作为环境变量"
else
  ENV_ARG=""
  echo "未检测到.env文件，容器将不加载本地环境变量"
fi

# 运行容器（可根据需要挂载数据目录）
echo "\n==> 运行 Docker 容器..."
docker run --rm -it $ENV_ARG $IMAGE_NAME 