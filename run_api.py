import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Smart Wardrobe Assistant API on http://127.0.0.1:8000 ...")
    print("📖 Swagger API Documentation available at http://127.0.0.1:8000/docs")
    uvicorn.run("backend.api:app", host="127.0.0.1", port=8000, reload=True)
