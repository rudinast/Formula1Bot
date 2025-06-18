from fastapi import FastAPI
from Requests.get_requests import get_route
from Requests.post_requests import post_route
from Requests.delete_requests import delete_route
from Requests.auth_requests import user_router

app = FastAPI()

app.include_router(get_route)
app.include_router(post_route)
app.include_router(delete_route)
app.include_router(user_router)