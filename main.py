from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel
from datanext_uploader import DataNextUploader
from datanext_pdf_uploader import DataNextPDFUploader
import re
from pathlib import Path
import shutil
import tempfile
import asyncio
from typing import Optional
import uuid
from datetime import datetime

app = FastAPI(title="DataNext Uploader API")

# ==================== Queue Management ====================

class TaskQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.is_processing = False
        self.current_task = None
        self.task_status = {}
    
    async def add_task(self, task_id: str, task_func, *args, **kwargs):
        """Add task to queue"""
        self.task_status[task_id] = {
            "status": "queued",
            "started_at": None,
            "completed_at": None,
            "error": None
        }
        await self.queue.put((task_id, task_func, args, kwargs))
        
        # Start processing if not already running
        if not self.is_processing:
            asyncio.create_task(self.process_queue())
    
    async def process_queue(self):
        """Process tasks one by one"""
        self.is_processing = True
        
        while not self.queue.empty():
            task_id, task_func, args, kwargs = await self.queue.get()
            self.current_task = task_id
            
            try:
                self.task_status[task_id]["status"] = "processing"
                self.task_status[task_id]["started_at"] = datetime.now().isoformat()
                
                # Run the task in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, task_func, *args, **kwargs)
                
                self.task_status[task_id]["status"] = "completed"
                self.task_status[task_id]["completed_at"] = datetime.now().isoformat()
                
            except Exception as e:
                self.task_status[task_id]["status"] = "failed"
                self.task_status[task_id]["error"] = str(e)
                self.task_status[task_id]["completed_at"] = datetime.now().isoformat()
                print(f"❌ Task {task_id} failed: {str(e)}")
            
            finally:
                self.queue.task_done()
                self.current_task = None
        
        self.is_processing = False

# Global queue instance
task_queue = TaskQueue()


# ==================== Media Upload Models & Functions ====================

class UploadRequest(BaseModel):
    folder_path: str
    class_text: str = "Only"


def parse_txt_file(txt_path: str) -> dict:
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    data = {
        'teacher_name': re.search(r'Teacher Name:\s*(.+)', content).group(1).strip(),
        'course_name': re.search(r'Course Name:\s*(.+)', content).group(1).strip(),
        'date': re.search(r'Date:\s*(.+)', content).group(1).strip(),
        'start_time': re.search(r'Start Time:\s*(.+)', content).group(1).strip(),
        'end_time': re.search(r'End Time:\s*(.+)', content).group(1).strip(),
        'description': re.search(r'DESCRIPTION:\s*\n(.+)', content, re.DOTALL).group(1).strip()
    }
    return data


def get_files_from_folder(folder_path: str):
    folder = Path(folder_path)
    media_files = [str(f) for f in folder.glob('*') if f.is_file() and f.suffix.lower() != '.txt']
    txt_file = next((str(f) for f in folder.glob('*.txt')), None)
    
    if not txt_file or len(media_files) < 2:
        raise ValueError("Need 1 txt file and at least 2 media files")
    
    return media_files[:2], txt_file


# ==================== Background Task Functions ====================

def process_media_upload(task_id: str, folder_path: str, class_text: str):
    """Background task for media upload"""
    try:
        base_path = Path("/home/datanext/PocBackend/media/recordings/")
        folder_path_obj = Path(folder_path)
        last_folder_name = folder_path_obj.name
        final_path = base_path / last_folder_name

        print(f"📁 Processing media upload - Task ID: {task_id}")
        print(f"📂 Final path: {final_path}")
        
        media_files, txt_file = get_files_from_folder(final_path)
        data = parse_txt_file(txt_file)
        
        summary = f"{data['teacher_name']} -- {data['course_name']} -- {data['date']} -- {data['start_time']} -- {data['end_time']}"
        description = f"{data['description']}\n\n{summary}"
        
        uploader = DataNextUploader()
        uploader.run_full_workflow(
            class_text=class_text,
            file1_path=media_files[0],
            file2_path=media_files[1],
            post_title=summary,
            title=summary,
            description=description
        )
        
        print(f"✅ Media upload completed - Task ID: {task_id}")
        
    except Exception as e:
        print(f"❌ Media upload failed - Task ID: {task_id}, Error: {str(e)}")
        raise


def process_pdf_upload(task_id: str, pdf_path: str, post_title: str, title: str, description: str, class_text: str):
    """Background task for PDF upload"""
    try:
        print(f"📄 Processing PDF upload - Task ID: {task_id}")
        
        uploader = DataNextPDFUploader()
        uploader.run_pdf_workflow(
            class_text=class_text,
            pdf_path=pdf_path,
            post_title=post_title,
            title=title,
            description=description
        )
        
        print(f"✅ PDF upload completed - Task ID: {task_id}")
        
    except Exception as e:
        print(f"❌ PDF upload failed - Task ID: {task_id}, Error: {str(e)}")
        raise
    finally:
        # Clean up temporary file
        if Path(pdf_path).exists():
            Path(pdf_path).unlink()


# ==================== API Endpoints ====================

@app.post("/automation")
async def upload_folder(request: UploadRequest):
    """
    Upload media files (audio + video) from a folder to DataNext.
    Returns immediately with task_id while processing in background.
    """
    try:
        # Generate unique task ID
        task_id = f"media_{uuid.uuid4().hex[:8]}"
        
        # Add to queue
        await task_queue.add_task(
            task_id,
            process_media_upload,
            task_id,
            request.folder_path,
            request.class_text
        )
        
        # Return immediate response
        return {
            "success": True,
            "message": "Upload task queued successfully",
            "task_id": task_id,
            "status": "queued"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-pdf")
async def upload_pdf(
    post_title: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    pdf_file: UploadFile = File(...),
    class_text: str = Form("Only")
):
    """
    Upload a PDF file to DataNext with form details.
    Returns immediately with task_id while processing in background.
    """
    try:
        # Validate file type
        if not pdf_file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Generate unique task ID
        task_id = f"pdf_{uuid.uuid4().hex[:8]}"
        
        # Create temporary file to save uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            shutil.copyfileobj(pdf_file.file, tmp_file)
            tmp_path = tmp_file.name
        
        # Add to queue
        await task_queue.add_task(
            task_id,
            process_pdf_upload,
            task_id,
            tmp_path,
            post_title,
            title,
            description,
            class_text
        )
        
        # Return immediate response
        return {
            "success": True,
            "message": "PDF upload task queued successfully",
            "task_id": task_id,
            "filename": pdf_file.filename,
            "status": "queued"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """
    Get the status of a specific task.
    """
    if task_id not in task_queue.task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task_id,
        **task_queue.task_status[task_id]
    }


@app.get("/queue-status")
async def get_queue_status():
    """
    Get overall queue status.
    """
    return {
        "is_processing": task_queue.is_processing,
        "current_task": task_queue.current_task,
        "queue_size": task_queue.queue.qsize(),
        "total_tasks": len(task_queue.task_status)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)