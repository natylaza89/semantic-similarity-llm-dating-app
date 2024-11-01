from fastapi import FastAPI

from app.config import settings
from app.api.routes import init_routers


app = FastAPI(title=settings.project_name, **settings.fastapi_info)
init_routers(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app=settings.app_string,
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env == "dev",
    )
