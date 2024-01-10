from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import argparse
from endpoints import router


app = FastAPI()
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def run_server(production):
    if production:
        print('running production')
        uvicorn.run("main:app", host='0.0.0.0', port=8000,
                    ssl_keyfile='', ssl_certfile='', reload=True)
    else:
        print('running development')
        uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run the FastAPI application.')
    parser.add_argument('--production', action='store_true',
                        help='Run in production mode.')
    args = parser.parse_args()
    run_server(args.production)
