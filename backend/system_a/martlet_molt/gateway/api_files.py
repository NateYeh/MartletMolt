"""
文件處理相關 API
"""

import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile
from loguru import logger
from pydantic import BaseModel

from martlet_molt.core.config import settings

router = APIRouter(prefix="/files", tags=["files"])


class FileInfo(BaseModel):
    """文件資訊"""

    filename: str
    size: int
    path: str
    content_type: str | None = None


@router.post("/upload", response_model=FileInfo)
async def upload_file(file: UploadFile = File(...)):
    """
    上傳文件到伺服器 (TASK-WEB-ADV)

    Args:
        file: 上傳的文件物件

    Returns:
        FileInfo: 上傳後的文件資訊
    """
    try:
        # 確保上傳目錄存在
        upload_dir = settings.data_dir / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)

        # 構建目標路徑
        file_path = upload_dir / file.filename

        # 儲存文件
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"File uploaded successfully: {file.filename} to {file_path}")

        return FileInfo(
            filename=file.filename,
            size=file_path.stat().st_size,
            path=str(file_path),
            content_type=file.content_type,
        )

    except Exception as e:
        logger.exception(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}") from e


@router.get("/list")
async def list_files():
    """
    列出已上傳的文件
    """
    upload_dir = settings.data_dir / "uploads"
    if not upload_dir.exists():
        return {"files": []}

    files = []
    for f in upload_dir.glob("*"):
        if f.is_file():
            files.append(
                {
                    "filename": f.name,
                    "size": f.stat().st_size,
                    "created_at": f.stat().st_ctime,
                }
            )

    return {"files": files}
