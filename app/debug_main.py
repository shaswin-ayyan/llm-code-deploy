from fastapi import FastAPI
import time

print("🚀 Starting FastAPI app...")
start_time = time.time()

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "healthy", "startup_time": time.time() - start_time}

@app.get("/")
def read_root():
    return {"Hello": "World"}

print(f"✅ Basic app ready in {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)