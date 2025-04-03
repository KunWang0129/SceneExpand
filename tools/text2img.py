import bentoml
from PIL import Image
def text2img(text):
    # with bentoml.SyncHTTPClient("http://localhost:4000") as client:
    with bentoml.SyncHTTPClient("http://chetak.ucsd.edu:3003") as client:
        result = client.txt2img(
            prompt=text,
            num_inference_steps=1,
            guidance_scale=0.0
        )
    
    result = Image.open(result)
    return result
