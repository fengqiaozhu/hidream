FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# 设置环境变量避免交互式提示
ENV DEBIAN_FRONTEND=noninteractive

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip \
    python3.10-venv \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/python3.10 /usr/bin/python

# 配置pip使用国内源
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ \
    && pip config set global.trusted-host mirrors.aliyun.com

# 设置工作目录
WORKDIR /app

# 复制应用文件
COPY app.py web.py requirements.txt /app/
COPY scripts/ /app/scripts/

# 创建模型目录
RUN mkdir -p /models

# 安装 PyTorch（使用官方源）和其他依赖（使用清华源）
RUN pip install --no-cache-dir torch torchvision torchaudio  && \
    pip install --no-cache-dir \
    diffusers==0.30.3 \
    transformers==4.44.2 \
    accelerate==0.33.0 \
    fastapi==0.115.0 \
    uvicorn==0.30.6 \
    gradio==4.44.0 \
    requests==2.32.3 \
    pillow==10.4.0 \
    supervisor==4.2.5 \
    huggingface-hub>=0.20.3 \
    tqdm>=4.66.1 && \
    pip install flash-attn==2.6.3 --no-build-isolation

# 配置 supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 设置执行权限
RUN chmod +x /app/scripts/start.sh

# 暴露端口
EXPOSE 8000 7860

# 设置启动命令
CMD ["/app/scripts/start.sh"]
