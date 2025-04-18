from diffusers import HiDreamImagePipeline
from transformers import PreTrainedTokenizerFast, LlamaForCausalLM
import torch
from fastapi import FastAPI, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
import io
from typing import Optional
import time
from starlette.requests import Request

app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 速率限制配置
RATE_LIMIT_DURATION = 60  # 60秒窗口
RATE_LIMIT_REQUESTS = 10  # 每个窗口最多10个请求
request_history = {}

# 输入验证
MIN_STEPS = 1
MAX_STEPS = 100
MIN_GUIDANCE_SCALE = 1.0
MAX_GUIDANCE_SCALE = 20.0
MIN_SIZE = 256
MAX_SIZE = 1024

MODEL_PATH = "/models/HiDream-I1-Full"
LLAMA_PATH = "/models/Meta-Llama-3.1-8B-Instruct"

# 延迟加载模型
tokenizer_4 = None
text_encoder_4 = None
pipe = None

def get_model():
    global tokenizer_4, text_encoder_4, pipe
    if pipe is None:
        try:
            tokenizer_4 = PreTrainedTokenizerFast.from_pretrained(LLAMA_PATH)
            text_encoder_4 = LlamaForCausalLM.from_pretrained(
                LLAMA_PATH,
                output_hidden_states=True,
                output_attentions=True,
                torch_dtype=torch.bfloat16,
            )

            pipe = HiDreamImagePipeline.from_pretrained(
                MODEL_PATH,
                tokenizer_4=tokenizer_4,
                text_encoder_4=text_encoder_4,
                torch_dtype=torch.bfloat16,
            )
            pipe.to("cuda")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")
    return pipe

# 速率限制检查
async def check_rate_limit(request: Request):
    client_ip = request.client.host
    current_time = time.time()
    
    # 清理过期的请求记录
    if client_ip in request_history:
        request_history[client_ip] = [
            timestamp for timestamp in request_history[client_ip]
            if current_time - timestamp < RATE_LIMIT_DURATION
        ]
    
    # 检查请求频率
    if client_ip in request_history and len(request_history[client_ip]) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_DURATION} seconds."
        )
    
    # 记录新请求
    if client_ip not in request_history:
        request_history[client_ip] = []
    request_history[client_ip].append(current_time)

@app.get("/generate")
async def generate_image(
    request: Request,
    prompt: str,
    steps: int = 50,
    guidance_scale: float = 7.5,
    height: int = 512,
    width: int = 512,
    seed: Optional[int] = None,
    _: None = Depends(check_rate_limit)
):
    # 输入验证
    if not prompt or len(prompt.strip()) == 0:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    if not MIN_STEPS <= steps <= MAX_STEPS:
        raise HTTPException(status_code=400, detail=f"Steps must be between {MIN_STEPS} and {MAX_STEPS}")
    
    if not MIN_GUIDANCE_SCALE <= guidance_scale <= MAX_GUIDANCE_SCALE:
        raise HTTPException(status_code=400, detail=f"Guidance scale must be between {MIN_GUIDANCE_SCALE} and {MAX_GUIDANCE_SCALE}")
    
    if not MIN_SIZE <= height <= MAX_SIZE or not MIN_SIZE <= width <= MAX_SIZE:
        raise HTTPException(status_code=400, detail=f"Height and width must be between {MIN_SIZE} and {MAX_SIZE}")

    try:
        pipe = get_model()
        
        # 设置随机种子
        if seed is not None:
            torch.manual_seed(seed)
        
        # 生成图像
        image = pipe(
            prompt=prompt,
            num_inference_steps=steps,
            guidance_scale=guidance_scale,
            height=height,
            width=width
        ).images[0]

        # 转换图像格式
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_byte_arr = img_byte_arr.getvalue()
        
        return Response(content=img_byte_arr, media_type="image/png")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
