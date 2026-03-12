# DataNext Uploader API

A FastAPI-based automation service that uploads media files (audio/video) and PDF documents to the DataNext platform using Selenium browser automation.

---

## Project Structure

```
├── main.py                  # FastAPI application & API endpoints
├── datanext_uploader.py     # Selenium automation for media uploads
├── datanext_pdf_uploader.py # Selenium automation for PDF uploads
```

---

## Requirements

- Python 3.8+
- Google Chrome browser
- ChromeDriver (matching your Chrome version)

### Install Dependencies

```bash
pip install fastapi uvicorn selenium pydantic
```

---

## Running the Server

```bash
python main.py
```

The API will start at `http://0.0.0.0:8000`

---

## API Endpoints

### `POST /automation` — Upload Media Files

Queues a background task to upload audio + video files from a folder to DataNext.

**Request Body (JSON):**
```json
{
  "folder_path": "/path/to/your/folder",
  "class_text": "Only"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `folder_path` | string | ✅ | Path to the folder containing media files + a `.txt` metadata file |
| `class_text` | string | ❌ | Navigation text to click on the platform (default: `"Only"`) |

**Expected folder contents:**
- 1 `.txt` file with metadata (see format below)
- At least 2 media files (e.g., `.mp3` and `.mp4`)

**`.txt` Metadata File Format:**
```
Teacher Name: John Doe
Course Name: Mathematics 101
Date: 2024-01-15
Start Time: 09:00 AM
End Time: 10:00 AM

DESCRIPTION:
This lecture covers quadratic equations and their applications.
```

**Response:**
```json
{
  "success": true,
  "message": "Upload task queued successfully",
  "task_id": "media_a1b2c3d4",
  "status": "queued"
}
```

---

### `POST /upload-pdf` — Upload a PDF File

Queues a background task to upload a PDF with metadata to DataNext.

**Request (multipart/form-data):**

| Field | Type | Required | Description |
|---|---|---|---|
| `post_title` | string | ✅ | Title shown as the post heading |
| `title` | string | ✅ | Internal title field |
| `description` | string | ✅ | Description text |
| `pdf_file` | file | ✅ | The PDF file to upload |
| `class_text` | string | ❌ | Navigation text to click (default: `"Only"`) |

**Response:**
```json
{
  "success": true,
  "message": "PDF upload task queued successfully",
  "task_id": "pdf_e5f6g7h8",
  "filename": "lecture_notes.pdf",
  "status": "queued"
}
```

---

### `GET /task-status/{task_id}` — Check Task Status

Check the status of any queued or completed task.

**Example:** `GET /task-status/media_a1b2c3d4`

**Response:**
```json
{
  "task_id": "media_a1b2c3d4",
  "status": "completed",
  "started_at": "2024-01-15T09:05:00",
  "completed_at": "2024-01-15T09:07:30",
  "error": null
}
```

**Possible statuses:** `queued` → `processing` → `completed` / `failed`

---

### `GET /queue-status` — Check Queue Health

Returns the overall status of the task queue.

**Response:**
```json
{
  "is_processing": true,
  "current_task": "media_a1b2c3d4",
  "queue_size": 2,
  "total_tasks": 5
}
```

---

## How the Queue Works

- All upload tasks run **one at a time** (sequential queue) to avoid browser conflicts.
- Tasks are added with a unique ID and processed in FIFO order.
- Use `/task-status/{task_id}` to poll for completion.
- Failed tasks retain their error message in the status response.

---

## Chrome Profile

The uploader uses a persistent Chrome profile to retain login sessions. The default path is `./chrome_profile`. On first run, you will be prompted in the terminal to log in manually, after which the session is saved.

```python
uploader = DataNextUploader(chrome_profile_path="./chrome_profile")
```

---

## Notes

- Media files are resolved from `/home/datanext/PocBackend/media/recordings/<folder_name>/` on the server.
- PDF temp files are automatically cleaned up after upload.
- The browser automation submits the form **twice** as required by the DataNext platform workflow.
- If an `.mp4` file is detected, the `FacialRecognition` checkbox is selected; otherwise `SpeechToText` is selected.