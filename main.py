from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
# from src.endpoints import router
from src import combined_router
import sys

# registering the models
import src.family_tree.models
import src.budget.models

app = FastAPI()
app.include_router(combined_router)

# allow_origins=['18.235.27.100']

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    if 'dev' in sys.argv:
        uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)
    else:
        uvicorn.run("main:app", host='0.0.0.0', port=8000)
