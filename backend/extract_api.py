from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import tempfile
from pathlib import Path
from data_extractor import extractor
import logging

app = FastAPI(title="Data Extraction API", description="Extract tables and text from PDFs to Excel.")

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/extract/upload")
async def upload_for_extraction(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported for extraction")
        temp_dir = Path(tempfile.mkdtemp())
        file_path = temp_dir / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        extraction_files = getattr(app.state, 'extraction_files', {})
        file_id = f"extract_{len(extraction_files) + 1}"
        extraction_files[file_id] = str(file_path)
        app.state.extraction_files = extraction_files
        return {
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "message": "File uploaded successfully for extraction"
        }
    except Exception as e:
        logging.error(f"Error uploading file for extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/extract/process")
async def process_extraction(file_id: str = Form(...)):
    try:
        extraction_files = getattr(app.state, 'extraction_files', {})
        if file_id not in extraction_files:
            raise HTTPException(status_code=404, detail="File not found")
        file_path = extraction_files[file_id]
        output_dir = Path(tempfile.mkdtemp())
        output_path = output_dir / f"extracted_{Path(file_path).stem}.xlsx"
        result = extractor.extract_and_convert(file_path, str(output_path))
        if result["success"]:
            extraction_outputs = getattr(app.state, 'extraction_outputs', {})
            extraction_outputs[file_id] = str(output_path)
            app.state.extraction_outputs = extraction_outputs
            return {
                "success": True,
                "file_id": file_id,
                "excel_file": str(output_path),
                "summary": result["summary"],
                "message": "Extraction completed successfully"
            }
        else:
            raise HTTPException(status_code=500, detail=f"Extraction failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        logging.error(f"Error processing extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/api/extract/download/{file_id}")
async def download_extracted_excel(file_id: str):
    try:
        extraction_outputs = getattr(app.state, 'extraction_outputs', {})
        if file_id not in extraction_outputs:
            raise HTTPException(status_code=404, detail="Extracted file not found")
        excel_path = extraction_outputs[file_id]
        if not os.path.exists(excel_path):
            raise HTTPException(status_code=404, detail="Excel file not found")
        return FileResponse(
            path=excel_path,
            filename=f"extracted_data_{file_id}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        logging.error(f"Error downloading extracted file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.get("/api/extract/status/{file_id}")
async def get_extraction_status(file_id: str):
    try:
        extraction_files = getattr(app.state, 'extraction_files', {})
        extraction_outputs = getattr(app.state, 'extraction_outputs', {})
        if file_id not in extraction_files:
            raise HTTPException(status_code=404, detail="File not found")
        has_output = file_id in extraction_outputs
        return {
            "file_id": file_id,
            "uploaded": True,
            "processed": has_output,
            "download_available": has_output
        }
    except Exception as e:
        logging.error(f"Error getting extraction status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}") 