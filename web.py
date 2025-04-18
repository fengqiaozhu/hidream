import gradio as gr
import requests
from PIL import Image
from io import BytesIO
import time

def generate(prompt, steps=50, guidance_scale=7.5, height=512, width=512, seed=None):
    if not prompt or len(prompt.strip()) == 0:
        raise gr.Error("提示词不能为空")
    
    try:
        params = {
            "prompt": prompt,
            "steps": steps,
            "guidance_scale": guidance_scale,
            "height": height,
            "width": width
        }
        if seed is not None:
            params["seed"] = seed

        # 添加重试机制
        max_retries = 3
        retry_delay = 1  # 初始延迟1秒
        
        for attempt in range(max_retries):
            try:
                response = requests.get("http://api:8000/generate", params=params, timeout=30)
                
                if response.status_code == 429:  # 速率限制
                    raise gr.Error("请求过于频繁，请稍后再试")
                
                response.raise_for_status()
                image_data = response.content
                image = Image.open(BytesIO(image_data))
                return image
            
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:  # 最后一次重试
                    if "Connection refused" in str(e):
                        raise gr.Error("服务暂时不可用，请稍后再试")
                    else:
                        raise gr.Error(f"生成图像失败: {str(e)}")
                time.sleep(retry_delay)
                retry_delay *= 2  # 指数退避
    
    except Exception as e:
        if "status_code=400" in str(e):
            raise gr.Error("输入参数无效，请检查输入范围")
        raise gr.Error(f"发生错误: {str(e)}")

# 创建自定义CSS样式
custom_css = """
.gradio-container {
    font-family: 'Arial', sans-serif;
}
.output-image {
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
"""

# 创建界面
with gr.Blocks(css=custom_css) as iface:
    gr.Markdown("""
    # HiDream-I1 图像生成器
    
    使用AI生成精美的图像。输入描述文字，调整参数，即可创建独特的艺术作品。
    
    ## 使用说明
    1. 在提示词框中输入详细的图像描述
    2. 调整生成参数（可选）
    3. 点击生成按钮
    """)
    
    with gr.Row():
        with gr.Column():
            prompt = gr.Textbox(
                label="提示词",
                placeholder="请输入详细的图像描述...",
                lines=3
            )
            with gr.Row():
                steps = gr.Slider(
                    minimum=1,
                    maximum=100,
                    value=50,
                    step=1,
                    label="推理步数",
                    info="步数越多，质量越高，但生成时间更长"
                )
                guidance_scale = gr.Slider(
                    minimum=1.0,
                    maximum=20.0,
                    value=7.5,
                    label="引导比例",
                    info="数值越高，生成的图像越接近提示词，但可能降低创造性"
                )
            with gr.Row():
                height = gr.Slider(
                    minimum=256,
                    maximum=1024,
                    value=512,
                    step=64,
                    label="高度",
                    info="图像高度（像素）"
                )
                width = gr.Slider(
                    minimum=256,
                    maximum=1024,
                    value=512,
                    step=64,
                    label="宽度",
                    info="图像宽度（像素）"
                )
            seed = gr.Number(
                label="随机种子",
                value=None,
                precision=0,
                info="设置固定的随机种子可以重现相同的结果"
            )
            generate_btn = gr.Button("生成图像", variant="primary")
        
        with gr.Column():
            output = gr.Image(label="生成的图像", elem_classes="output-image")
            
    # 绑定生成按钮
    generate_btn.click(
        fn=generate,
        inputs=[prompt, steps, guidance_scale, height, width, seed],
        outputs=output
    )
    
    gr.Markdown("""
    ### 提示
    - 提示词越详细，生成的图像质量越好
    - 如果遇到错误，请稍等片刻后重试
    - 可以保存随机种子以重现喜欢的结果
    """)

# 启动服务
iface.launch(server_name="0.0.0.0", server_port=7860)
