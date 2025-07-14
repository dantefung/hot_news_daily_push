# 基于官方Python镜像
FROM python:3.11-slim

# 安装cron和系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        cron \
        build-essential \
        libxml2-dev \
        libxslt1-dev \
        libffi-dev \
        libssl-dev \
        libjpeg-dev \
        libpng-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        libopenjp2-7-dev \
        libtiff5-dev \
        libharfbuzz-dev \
        libfribidi-dev \
        libxcb1-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt ./

# 安装Python依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 复制项目全部代码
COPY . .

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai

# 创建必要目录
RUN mkdir -p data/raw data/filtered data/merged data/inputs data/outputs data/webhook data/debug data/test \
    && mkdir -p cache/summary

# 添加crontab定时任务（每天utc 0点 = 东八区8点执行主程序，日志输出到/logs/cron.log）
RUN mkdir -p /logs && \
    echo "0 0 * * * cd /app && python hot_news_main.py >> /logs/cron.log 2>&1" > /etc/cron.d/hotnews-cron && \
    chmod 0644 /etc/cron.d/hotnews-cron && \
    crontab /etc/cron.d/hotnews-cron

# 启动时先立即执行一次主程序，再启动cron和日志
CMD python hot_news_main.py >> /logs/cron.log 2>&1 && cron && tail -F /logs/cron.log 