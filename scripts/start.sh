#!/bin/bash

# 创建supervisor日志目录
mkdir -p /var/log/supervisor

# 启动supervisor
exec /usr/local/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf 