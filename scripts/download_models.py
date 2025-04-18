#!/usr/bin/env python3
import os
import argparse
from huggingface_hub import snapshot_download
from tqdm import tqdm

def download_model(model_id, local_dir, token=None):
    """
    从 Hugging Face Hub 下载模型
    
    Args:
        model_id: Hugging Face Hub 上的模型ID
        local_dir: 本地保存目录
        token: Hugging Face token
    """
    print(f"正在下载模型: {model_id}")
    try:
        snapshot_download(
            repo_id=model_id,
            local_dir=local_dir,
            token=token,
            local_dir_use_symlinks=False
        )
        print(f"模型 {model_id} 下载完成！保存在: {local_dir}")
    except Exception as e:
        print(f"下载模型 {model_id} 时发生错误: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description="下载 HiDream 所需的模型")
    parser.add_argument("--token", type=str, help="Hugging Face token", default=os.environ.get("HF_TOKEN"))
    parser.add_argument("--models-dir", type=str, default="models", help="模型保存目录")
    args = parser.parse_args()

    if not args.token:
        print("错误: 未提供 Hugging Face token")
        print("请通过 --token 参数提供，或设置 HF_TOKEN 环境变量")
        return

    # 确保模型目录存在
    os.makedirs(args.models_dir, exist_ok=True)

    # 模型列表
    models = {
        "HiDream-I1-Full": "HiDream/HiDream-I1-Full",
        "Meta-Llama-3.1-8B-Instruct": "meta-llama/Llama-2-8b-chat"
    }

    # 下载每个模型
    for model_name, model_id in models.items():
        local_dir = os.path.join(args.models_dir, model_name)
        try:
            download_model(model_id, local_dir, args.token)
        except Exception as e:
            print(f"下载模型 {model_name} 失败: {str(e)}")
            continue

if __name__ == "__main__":
    main() 