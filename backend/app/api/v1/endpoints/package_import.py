"""
HERCU 课程包导入 API
支持 V2 格式 (CoursePackageV2 - lessons/script 结构)
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, Dict, List
import json

from app.services.package_importer import PackageImporterV2, CoursePackageV2
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.core.security import get_current_admin_user
from app.models.models import User


router = APIRouter(tags=["Package Import"])


# ==================== 请求/响应模型 ====================

class ImportPackageRequest(BaseModel):
    """导入课程包请求 (V2 格式)"""
    package: Dict


class ImportPackageResponse(BaseModel):
    """导入课程包响应"""
    success: bool
    course_id: int
    nodes_created: int
    edges_created: int
    message: str


class PackageInfoResponse(BaseModel):
    """课程包信息响应"""
    studio_package_id: str
    version: str
    style: str
    imported_at: str


# ==================== API 端点 ====================

@router.post("/import-package", response_model=ImportPackageResponse)
async def import_package(
    request: ImportPackageRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    导入 HERCU Studio 课程包 (V2 格式)

    **请求体**:
    ```json
    {
      "package": {
        "id": "PKG-20240115-A3F2",
        "version": "2.0.0",
        "meta": {
          "title": "课程标题",
          "description": "课程描述",
          ...
        },
        "lessons": [...],
        "edges": [...],
        "global_ai_config": {...}
      }
    }
    ```

    **响应**:
    ```json
    {
      "success": true,
      "course_id": 123,
      "nodes_created": 8,
      "edges_created": 7,
      "message": "课程包导入成功"
    }
    ```
    """
    try:
        # 解析课程包
        package = CoursePackageV2(**request.package)

        # 导入 - 传入当前用户信息
        importer = PackageImporterV2(db)
        result = await importer.import_package(
            package,
            user_id=current_user.id,
            instructor_name=current_user.username
        )

        return ImportPackageResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.post("/import-package-file")
async def import_package_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    通过上传 JSON 文件导入课程包 (V2 格式)

    **文件格式**: JSON (Studio 导出格式 V2)

    支持的格式:
    - V2 格式: 包含 lessons 和 script 字段
    """
    try:
        # 验证文件类型
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="只支持 JSON 文件")

        # 读取文件
        content = await file.read()
        package_data = json.loads(content.decode('utf-8'))

        # 解析课程包 (V2 格式)
        package = CoursePackageV2(**package_data)

        # 导入 - 传入当前用户信息
        importer = PackageImporterV2(db)
        result = await importer.import_package(
            package,
            user_id=current_user.id,
            instructor_name=current_user.username
        )

        return result

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="无效的 JSON 文件")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.get("/courses/{course_id}/package", response_model=PackageInfoResponse)
async def get_package_info(
    course_id: int,
    db: Session = Depends(get_db)
):
    """
    获取课程的 Studio 课程包信息
    """
    from sqlalchemy import text

    result = db.execute(
        text("""
            SELECT studio_package_id, version, style, imported_at
            FROM course_packages
            WHERE course_id = :course_id
        """),
        {"course_id": course_id}
    )

    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="课程包信息不存在")

    return PackageInfoResponse(
        studio_package_id=row[0],
        version=row[1],
        style=row[2],
        imported_at=str(row[3])
    )


@router.get("/packages")
async def list_packages(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    获取已导入的课程包列表

    **查询参数**:
    - limit: 每页数量 (默认 50)
    - offset: 偏移量 (默认 0)
    """
    from sqlalchemy import text

    result = db.execute(
        text("""
            SELECT
                cp.id, cp.studio_package_id, cp.course_id,
                c.name as title, cp.version, cp.style, cp.imported_at
            FROM course_packages cp
            JOIN courses c ON cp.course_id = c.id
            ORDER BY cp.imported_at DESC
            LIMIT :limit OFFSET :offset
        """),
        {"limit": limit, "offset": offset}
    )

    packages = []
    for row in result.fetchall():
        packages.append({
            "id": row[0],
            "studio_package_id": row[1],
            "course_id": row[2],
            "title": row[3],
            "version": row[4],
            "style": row[5],
            "imported_at": str(row[6])
        })

    # 获取总数
    count_result = db.execute(text("SELECT COUNT(*) FROM course_packages"))
    total = count_result.fetchone()[0]

    return {
        "packages": packages,
        "total": total
    }


@router.delete("/packages/{studio_package_id}")
async def delete_package(
    studio_package_id: str,
    db: Session = Depends(get_db)
):
    """
    删除课程包 (同时删除关联的课程和节点)

    **警告**: 此操作不可逆
    """
    from sqlalchemy import text

    try:
        # 查找课程包
        result = db.execute(
            text("SELECT course_id FROM course_packages WHERE studio_package_id = :pkg_id"),
            {"pkg_id": studio_package_id}
        )

        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="课程包不存在")

        course_id = row[0]

        # 删除课程节点
        db.execute(
            text("DELETE FROM course_nodes WHERE course_id = :course_id"),
            {"course_id": course_id}
        )

        # 删除课程包记录
        db.execute(
            text("DELETE FROM course_packages WHERE studio_package_id = :pkg_id"),
            {"pkg_id": studio_package_id}
        )

        # 删除课程
        db.execute(
            text("DELETE FROM courses WHERE id = :course_id"),
            {"course_id": course_id}
        )

        db.commit()

        return {
            "success": True,
            "message": f"课程包 {studio_package_id} 已删除"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


# ==================== 健康检查 ====================

@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "package-import", "version": "2.0"}
