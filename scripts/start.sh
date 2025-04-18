#!/bin/bash

# 创建必要的目录
mkdir -p /var/log/supervisor
mkdir -p /models

# 检查模型是否存在并下载
check_and_download_models() {
    if [ -z "$HF_TOKEN" ]; then
        echo "错误: 未设置 HF_TOKEN 环境变量"
        exit 1
    fi

    # 检查 HiDream 模型
    if [ ! -d "/models/HiDream-I1-Full" ] || [ -z "$(ls -A /models/HiDream-I1-Full)" ]; then
        echo "HiDream-I1-Full 模型不存在，开始下载..."
        python /app/scripts/download_models.py --token "$HF_TOKEN" --models-dir /models || exit 1
    else
        echo "模型已存在，跳过下载"
    fi
}

# 执行模型检查和下载
check_and_download_models

# 启动服务
exec /usr/local/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf 