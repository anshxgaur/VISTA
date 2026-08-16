from fastapi import FastAPI

from api.upload import router

app = FastAPI(
    title="VISTA2 Data Pipeline",
    version="1.0"
)

app.include_router(router)