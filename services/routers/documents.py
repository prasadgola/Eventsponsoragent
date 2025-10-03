from fastapi import APIRouter, File, UploadFile, HTTPException
import os
import uuid

router = APIRouter()

UPLOAD_DIR = "/tmp/uploads" if os.getenv('K_SERVICE') else "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and save document, return file_id"""
    
    # Generate unique file_id
    file_id = str(uuid.uuid4())[:8]
    ext = os.path.splitext(file.filename)[1]
    saved_filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)
    
    try:
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return {
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "path": file_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/analyze/{file_id}")
async def analyze_by_id(file_id: str, query: str = "Analyze this document"):
    """Analyze previously uploaded document using Gemini"""
    
    try:
        import google.generativeai as genai
        
        # Find file
        files = [f for f in os.listdir(UPLOAD_DIR) if f.startswith(file_id)]
        if not files:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_path = os.path.join(UPLOAD_DIR, files[0])
        
        # Configure Gemini
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        
        # Upload to Gemini
        uploaded_file = genai.upload_file(file_path)
        
        # Analyze
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"{query}\n\nProvide a clear, concise analysis."
        
        response = model.generate_content([prompt, uploaded_file])
        
        return {
            "file_id": file_id,
            "analysis": response.text
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")