import os
import shutil
import uuid
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from processor import process_demo_file

app = FastAPI(title="CS:GO Demo Processor Microservice")

@app.on_event("startup")
async def startup_event():
    # Clean up any stale temp files from previous runs
    if os.path.exists("temp"):
        shutil.rmtree("temp")
    os.makedirs("temp", exist_ok=True)

@app.post("/demo")
def parse_demo(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    Synchronous endpoint (run in threadpool) to handle CPU-bound demo processing.
    """
    # Unique ID for this processing request
    request_id = str(uuid.uuid4())
    
    # Create a temporary directory structure for this request
    # structure: temp/{request_id}/input -> for .dem
    #            temp/{request_id}/output -> for csvs
    base_temp_dir = Path("temp") / request_id
    input_dir = base_temp_dir / "input"
    output_dir = base_temp_dir / "output"
    
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded file
    file_location = input_dir / file.filename
    try:
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        cleanup_files(base_temp_dir)
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
    
    try:
        generated_files = process_demo_file(str(file_location), str(output_dir))
        
        if not generated_files:
             raise HTTPException(status_code=422, detail="No data could be extracted from the demo.")

        # Create a ZIP of the output directory
        zip_filename = f"analysis_{request_id}.zip"
        zip_path = base_temp_dir / zip_filename
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(output_dir):
                for f in files:
                    file_path = os.path.join(root, f)
                    arcname = os.path.relpath(file_path, output_dir)
                    zipf.write(file_path, arcname)
                    
        # Schedule cleanup after response is sent
        return FileResponse(
            path=zip_path, 
            filename=f"{file.filename}_analysis.zip",
            media_type='application/zip',
            background=BackgroundTask(cleanup_files, base_temp_dir)
        )

    except Exception as e:
        cleanup_files(base_temp_dir)
        raise HTTPException(status_code=500, detail=f"Error processing demo: {str(e)}")

def cleanup_files(path: Path):
    try:
        shutil.rmtree(path)
        print(f"Cleaned up {path}")
    except Exception as e:
        print(f"Error cleaning up {path}: {e}")

if __name__ == "__main__":
    import uvicorn
    # Create temp dir if not exists
    os.makedirs("temp", exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)
