from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
import uvicorn

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=['*'],  
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

#pem = family6!FAMILY2023

key = '/etc/nginx/fastapi-ssl/key.pem'
cert = '/etc/nginx/fastapi-ssl/cert.pem'

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000, ssl_keyfile=key, ssl_certfile=cert)

@app.get('/')
def read_root():
    return {'message': 'I love you!!!, attempt at 21:20'}

@app.get('/backend')
def read_backend():
    return {'Hello wife': 'I love you!!!'}

