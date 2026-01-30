import lancedb
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import json

# 1. Setup App
app = FastAPI()

# Enable CORS so your HTML file can talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Connect to your LanceDB
DB_PATH = "./data/neurips_vdb" 
db = lancedb.connect(DB_PATH)

# The table name is the name of the .lance folder (papers.lance -> "papers")
TABLE_NAME = "papers"

try:
    table = db.open_table(TABLE_NAME)
except Exception as e:
    print(f"❌ Error: Could not find table '{TABLE_NAME}'")
    print(f"Available tables in {DB_PATH}: {db.table_names()}")
    if db.table_names():
        first_table = db.table_names()[0]
        print(f"⚠️ Falling back to first available table: '{first_table}'")
        table = db.open_table(first_table)
    else:
        raise e

@app.get("/search")
async def search(q: str):
    print(f"🔍 Search request received: '{q}'")
    # Perform semantic search
    # We use .to_pandas() to get the result set
    df = table.search(q).limit(50).to_pandas()
    
    # --- FIX FOR SERIALIZATION ERROR ---
    # 1. Drop the vector column if it exists (it's heavy and causes JSON issues)
    if "_vector" in df.columns:
        df = df.drop(columns=["_vector"])
    if "vector" in df.columns:
        df = df.drop(columns=["vector"])
        
    # 2. Replace NaN values with empty strings (JSON can't handle NaN)
    df = df.fillna("")
    
    # 3. Convert to list of dicts
    results = df.to_dict(orient="records")
    print(f"✅ Returning {len(results)} results")
    return results

@app.get("/health")
async def health():
    return {"status": "online", "table": TABLE_NAME, "rows": len(table)}

if __name__ == "__main__":
    import uvicorn
    print("🚀 LanceDB Bridge running at http://localhost:")
    print(f"📂 Connected to database at: {os.path.abspath(DB_PATH)}")
    print(f"📊 Active Table: {TABLE_NAME}")
    uvicorn.run(app, host="0.0.0.0", port=8000)