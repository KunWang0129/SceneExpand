import bentoml
from pathlib import Path
import numpy as np

def clip_image_embedding(image_path):
    # with bentoml.SyncHTTPClient("http://localhost:3000") as client:
    with bentoml.SyncHTTPClient("http://chetak.ucsd.edu:3002") as client:
        result = client.encode_image(
            items=[
                Path(image_path),
            ],
        )
    result = result[0]
    result = result / np.linalg.norm(result)
    return result    

def clip_text_embedding(text):
    with bentoml.SyncHTTPClient("http://chetak.ucsd.edu:3002") as client:
        result = client.encode_text(
            items=[
                text,
            ],
        )
    result = result[0]
    result = result / np.linalg.norm(result)
    
    return result    

def cosine_similarity(text, image_path):
    with bentoml.SyncHTTPClient("http://chetak.ucsd.edu:3002") as client:
        result = client.rank(
            queries=[
                Path(image_path),
            ],
            candidates=[
                text,
            ],
        )
    # result = result[0]
    # result = result / np.linalg.norm(result)
    
    return result    

# text_embd = clip_text_embedding("a table")
# img_embd = clip_image_embedding("/kunal-data/SceneProg/dataset/3dc72ce1-1c86-325d-9192-5ec0eb7d6979/image.jpg")

# result = cosine_similarity("a dog", "/kunal-data/SceneProg/dataset/3dc72ce1-1c86-325d-9192-5ec0eb7d6979/image.jpg")
# breakpoint()