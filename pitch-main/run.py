import uvicorn
from src.config import API_HOST, API_PORT, DEBUG

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=DEBUG
    ) 