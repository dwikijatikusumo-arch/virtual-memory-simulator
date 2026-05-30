from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from algorithms import PageReplacement, detect_thrashing

app = FastAPI(
    title="Virtual Memory Simulator API",
    description="Simulasi algoritma penggantian halaman untuk pembelajaran Sistem Operasi",
    version="2.0.0"
)

# CORS untuk frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimulationRequest(BaseModel):
    reference_string: List[int]
    frames: int

class SimulationResponse(BaseModel):
    fifo: dict
    lru: dict
    optimal: dict
    total_pages: int
    thrashing_analysis: dict

@app.post("/simulate", response_model=SimulationResponse)
async def simulate(request: SimulationRequest):
    """
    Simulasi ketiga algoritma penggantian halaman
    """
    if request.frames <= 0:
        raise HTTPException(status_code=400, detail="Jumlah frame harus lebih dari 0")
    if not request.reference_string:
        raise HTTPException(status_code=400, detail="Reference string tidak boleh kosong")
    if len(request.reference_string) > 200:
        raise HTTPException(status_code=400, detail="Maksimal 200 akses halaman")
    
    pages = request.reference_string
    frames = request.frames
    
    # Eksekusi ketiga algoritma
    fifo_faults, fifo_steps = PageReplacement.fifo(pages, frames)
    lru_faults, lru_steps = PageReplacement.lru(pages, frames)
    opt_faults, opt_steps = PageReplacement.optimal(pages, frames)
    
    # Analisis thrashing (menggunakan LRU sebagai baseline)
    thrash_analysis = detect_thrashing(lru_faults, len(pages))
    
    return {
        "fifo": {
            "faults": fifo_faults,
            "steps": fifo_steps,
            "hit_ratio": round((len(pages) - fifo_faults) / len(pages) * 100, 2)
        },
        "lru": {
            "faults": lru_faults,
            "steps": lru_steps,
            "hit_ratio": round((len(pages) - lru_faults) / len(pages) * 100, 2)
        },
        "optimal": {
            "faults": opt_faults,
            "steps": opt_steps,
            "hit_ratio": round((len(pages) - opt_faults) / len(pages) * 100, 2)
        },
        "total_pages": len(pages),
        "thrashing_analysis": thrash_analysis
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Memory Virtual Simulator"}

@app.get("/")
async def root():
    return {
        "message": "Virtual Memory Simulator API",
        "endpoints": {
            "POST /simulate": "Jalankan simulasi dengan reference string dan jumlah frame",
            "GET /health": "Cek status server"
        },
        "example_request": {
            "reference_string": [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1],
            "frames": 3
        }
    }
