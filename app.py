from fastapi import FastAPI
from robot_router import router as robot_router

app = FastAPI()

app.include_router(robot_router)
