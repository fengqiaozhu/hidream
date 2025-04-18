# HiDream Image Generator

基于 HiDream-I1 模型的图像生成服务，提供 REST API 和 Web 界面。

## 功能特点

- 使用 HiDream-I1 模型进行高质量图像生成
- 提供 REST API 接口
- 提供用户友好的 Web 界面
- 支持自定义生成参数
- 支持 GPU 加速
- 自动服务监控和重启

## 系统要求

- NVIDIA GPU (推荐)
- Docker 和 Docker Compose
- NVIDIA Container Toolkit
- 至少 16GB 内存
- 至少 20GB 磁盘空间

## 快速开始

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/hidream.git
cd hidream
```

2. 设置环境变量：
```bash
export HF_TOKEN=your_huggingface_token
```

3. 下载模型：
将模型文件放在 `models` 目录下：
- HiDream-I1-Full
- Meta-Llama-3.1-8B-Instruct

4. 启动服务：
```bash
docker-compose up -d
```

5. 访问服务：
- Web 界面: http://localhost:7860
- API 文档: http://localhost:8000/docs

## API 使用

### 生成图像

```
GET /generate
```

参数：
- `prompt`: 图像描述文本
- `steps`: 推理步数 (1-100, 默认: 50)
- `guidance_scale`: 引导比例 (1.0-20.0, 默认: 7.5)
- `height`: 图像高度 (256-1024, 默认: 512)
- `width`: 图像宽度 (256-1024, 默认: 512)
- `seed`: 随机种子 (可选)

## 开发

### 本地开发

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 启动服务：
```bash
python app.py  # API 服务
python web.py  # Web 界面
```

### 构建 Docker 镜像

```bash
docker-compose build
```

## 项目结构

```
.
├── Dockerfile          # Docker 构建配置
├── app.py             # API 服务
├── web.py             # Web 界面
├── docker-compose.yml # Docker 编排配置
├── supervisord.conf   # 进程管理配置
└── scripts/
    └── start.sh       # 启动脚本
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请通过 GitHub Issues 联系我们。 