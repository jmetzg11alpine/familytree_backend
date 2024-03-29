from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.endpoints import router

import cProfile
# allow_origins=['18.235.27.100'],

app = FastAPI()
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['18.235.27.100'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8000)
    # uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)
    # cProfile.run('uvicorn.run("main:app", host="0.0.0.0", port=8000)', sort='cumulative')
