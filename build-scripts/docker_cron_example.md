# Docker 镜像内自带定时任务说明

本项目的 Docker 镜像已内置 cron，每天 8:00（Asia/Shanghai）自动执行 `python hot_news_main.py`，日志输出到 `/logs/cron.log`。

---

## 使用方法

1. **构建镜像**

```bash
cd build-scripts
bash build_and_run_docker.sh
```

2. **运行容器**（无需主机 crontab，镜像内已定时）

```bash
docker run --rm -it --env-file .env hot-news-daily-push:latest
```

3. **查看定时任务日志**

```bash
docker exec -it <container_id> tail -f /logs/cron.log
```

---

## 自定义定时

如需修改定时（如改为每天 7:00），请修改 `build-scripts/Dockerfile` 中：

```
echo "0 8 * * * ..." > /etc/cron.d/hotnews-cron
```

为：

```
echo "0 7 * * * ..." > /etc/cron.d/hotnews-cron
```

---

## 说明
- 镜像启动后会自动启动 cron 服务并持续输出日志。
- 日志文件位于 `/logs/cron.log`，可通过 `docker exec` 进入容器查看。
- 如需持久化日志，可挂载主机目录：

```bash
docker run --rm -it --env-file .env -v /your/host/logs:/logs hot-news-daily-push:latest
```

---

## 进阶
- 镜像内已设置 `TZ=Asia/Shanghai`，如需其他时区可自行调整 Dockerfile。
- 支持自定义环境变量，建议通过 `.env` 文件传递。 

---

## 启动即执行一次
- 每次容器启动时，会立即执行一次 `python hot_news_main.py`，然后再进入定时循环。
- 日志同样输出到 `/logs/cron.log`。

--- 