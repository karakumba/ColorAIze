from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
from loguru import logger
import shutil
from colorizer import ImageColorizer

app = FastAPI(
    title="ColorAIze API",
    description="API for black and white image colorization",
    version="1.0.0"
)

colorizer = ImageColorizer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/processed", StaticFiles(directory="storage/processed"), name="processed")


@app.on_event("startup")
async def startup_event():
    logger.info("Starting ColorAIze Backend API")
    os.makedirs('storage/uploads', exist_ok=True)
    os.makedirs('storage/processed', exist_ok=True)


@app.post("/api/colorize")
async def colorize_image(file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(400, "File must be an image")

        temp_path = f"storage/uploads/temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = os.path.getsize(temp_path)
        if file_size > 20 * 1024 * 1024:
            os.remove(temp_path)
            raise HTTPException(400, "File too large (max 20MB)")

        with open(temp_path, "rb") as f:
            image_bytes = f.read()
        os.remove(temp_path)

        logger.info(f"Processing image: {file.filename}")
        result_path = colorizer.colorize(image_bytes, file.filename)
        result_filename = os.path.basename(result_path)

        return {
            "status": "success",
            "filename": result_filename,
            "download_url": f"/api/download/{result_filename}",
            "preview_url": f"/processed/{result_filename}",
        }

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(500, f"Internal server error: {str(e)}")


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join('storage/processed', filename)
    if not os.path.exists(file_path):
        raise HTTPException(404, "File not found")
    return FileResponse(file_path, filename=f"colorized_{filename}")


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "backend",
        "model_loaded": colorizer.is_model_loaded()
    }


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "ColorAIze API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "colorize": "POST /api/colorize",
            "download": "GET /api/download/{filename}"
        },
        "note": "Это упрощенная версия без Celery/Redis"
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)