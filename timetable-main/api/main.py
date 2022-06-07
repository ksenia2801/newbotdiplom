import uvicorn

from config import Config
from web.service import app

if __name__ == '__main__':
    config = Config(filename='config.yaml')

    uvicorn.run(
        app=app,
        host=config.ENDPOINT_HOST,
        port=config.ENDPOINT_PORT,
        log_level=config.LOG_LEVEL
    )
