# from flask import Flask
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from item_routes import item_bp
from purchase_routes import purchases_bp
from ticket_routes import tickets_bp
from agent_routes import agent_bp
from sop_cat_routes import sop_cats_bp
from orders_routes import orders_bp
from payments_routes import payment_bp
from shared import redis_client

app = FastAPI()

origins = ["http://localhost", "http://localhost:5173", "http://127.0.0.1:5173", "http://127.0.0.1:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # or ["*"] to allow all (less secure)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(item_bp)
app.include_router(purchases_bp)
app.include_router(tickets_bp)
app.include_router(agent_bp)
app.include_router(sop_cats_bp)
app.include_router(orders_bp)
app.include_router(payment_bp)

# @app.on_event("startup")
# async def startup_event():
#     # You can add a redis.ping() here to check connection
#     print("Connecting to Redis...")

# @app.on_event("shutdown")
# async def shutdown_event():
#     await redis_client.close()
#     print("Redis connection closed.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
    