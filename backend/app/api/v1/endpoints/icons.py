"""
Simulator Icon Library API
模拟器图标库 API - 供两个应用调用
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import BaseModel

from app.db.session import get_db
from app.models.models import SimulatorIcon, SimulatorIconPreset

router = APIRouter()


# ============================================
# Pydantic Schemas
# ============================================

class IconBase(BaseModel):
    id: str
    name: str
    name_en: Optional[str] = None
    category: str
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    default_color: str = "#3B82F6"
    default_scale: float = 1.0
    recommended_scenes: Optional[List[str]] = None


class IconCreate(IconBase):
    pass


class IconResponse(IconBase):
    is_active: int = 1
    sort_order: int = 0
    usage_count: int = 0

    class Config:
        from_attributes = True


class IconPresetBase(BaseModel):
    id: str
    name: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    icons: List[dict]
    canvas_config: Optional[dict] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class IconPresetCreate(IconPresetBase):
    pass


class IconPresetResponse(IconPresetBase):
    is_official: int = 0
    is_active: int = 1
    usage_count: int = 0

    class Config:
        from_attributes = True


class IconCategoryInfo(BaseModel):
    id: str
    name: str
    name_en: str
    count: int


class BulkIconCreate(BaseModel):
    icons: List[IconCreate]


# ============================================
# Icon Endpoints
# ============================================

@router.get("/icons", response_model=List[IconResponse])
async def get_icons(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(default=100, le=500),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """获取图标列表"""
    query = db.query(SimulatorIcon).filter(SimulatorIcon.is_active == 1)

    if category:
        query = query.filter(SimulatorIcon.category == category)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                SimulatorIcon.id.ilike(search_pattern),
                SimulatorIcon.name.ilike(search_pattern),
                SimulatorIcon.name_en.ilike(search_pattern),
                SimulatorIcon.description.ilike(search_pattern)
            )
        )

    query = query.order_by(SimulatorIcon.category, SimulatorIcon.sort_order, SimulatorIcon.id)
    icons = query.offset(offset).limit(limit).all()

    return icons


@router.get("/icons/categories", response_model=List[IconCategoryInfo])
async def get_icon_categories(db: Session = Depends(get_db)):
    """获取图标分类列表及数量"""
    # 分类名称映射
    category_names = {
        "basic": ("基础形状", "Basic Shapes"),
        "education": ("教育学习", "Education"),
        "science": ("科学实验", "Science"),
        "cognition": ("思维认知", "Cognition"),
        "nature": ("自然生物", "Nature"),
        "anatomy": ("人体解剖", "Anatomy"),
        "sports": ("体育运动", "Sports"),
        "sports_equipment": ("体育器材", "Sports Equipment"),
        "sports_action": ("运动动作", "Sports Actions"),
        "sports_ball": ("球类运动", "Ball Sports"),
        "mechanical": ("机械工程", "Mechanical"),
        "electronic": ("电子电气", "Electronic"),
        "construction": ("建筑工程", "Construction"),
        "transport": ("交通运输", "Transport"),
        "medical": ("医疗健康", "Medical"),
        "art": ("音乐艺术", "Art & Music"),
        "business": ("商业金融", "Business"),
        "food": ("食物饮品", "Food & Drink"),
        "animal": ("动物", "Animals"),
        "geography": ("天文地理", "Geography"),
        "furniture": ("家具家电", "Furniture"),
        "daily": ("日常用品", "Daily Items"),
        "kitchen": ("厨房用品", "Kitchen"),
        "classroom": ("教室用品", "Classroom"),
        "math": ("数学工具", "Math Tools"),
        "outdoor": ("户外场景", "Outdoor"),
        "weather": ("天气场景", "Weather"),
        "time": ("时间场景", "Time"),
        "emotion": ("情绪表情", "Emotions"),
        "social": ("社交场景", "Social"),
        "office": ("工作场景", "Office"),
        "safety": ("安全场景", "Safety"),
    }

    # 统计每个分类的图标数量
    from sqlalchemy import func
    counts = db.query(
        SimulatorIcon.category,
        func.count(SimulatorIcon.id).label('count')
    ).filter(
        SimulatorIcon.is_active == 1
    ).group_by(SimulatorIcon.category).all()

    result = []
    for cat, count in counts:
        names = category_names.get(cat, (cat, cat))
        result.append(IconCategoryInfo(
            id=cat,
            name=names[0],
            name_en=names[1],
            count=count
        ))

    return result


@router.get("/icons/{icon_id}", response_model=IconResponse)
async def get_icon(icon_id: str, db: Session = Depends(get_db)):
    """获取单个图标详情"""
    icon = db.query(SimulatorIcon).filter(SimulatorIcon.id == icon_id).first()
    if not icon:
        raise HTTPException(status_code=404, detail="Icon not found")
    return icon


@router.post("/icons", response_model=IconResponse)
async def create_icon(icon: IconCreate, db: Session = Depends(get_db)):
    """创建新图标"""
    existing = db.query(SimulatorIcon).filter(SimulatorIcon.id == icon.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Icon ID already exists")

    db_icon = SimulatorIcon(**icon.model_dump())
    db.add(db_icon)
    db.commit()
    db.refresh(db_icon)
    return db_icon


@router.post("/icons/bulk", response_model=dict)
async def bulk_create_icons(data: BulkIconCreate, db: Session = Depends(get_db)):
    """批量创建图标"""
    created = 0
    skipped = 0

    for icon_data in data.icons:
        existing = db.query(SimulatorIcon).filter(SimulatorIcon.id == icon_data.id).first()
        if existing:
            skipped += 1
            continue

        db_icon = SimulatorIcon(**icon_data.model_dump())
        db.add(db_icon)
        created += 1

    db.commit()
    return {"created": created, "skipped": skipped, "total": len(data.icons)}


@router.put("/icons/{icon_id}", response_model=IconResponse)
async def update_icon(icon_id: str, icon: IconCreate, db: Session = Depends(get_db)):
    """更新图标"""
    db_icon = db.query(SimulatorIcon).filter(SimulatorIcon.id == icon_id).first()
    if not db_icon:
        raise HTTPException(status_code=404, detail="Icon not found")

    for key, value in icon.model_dump().items():
        setattr(db_icon, key, value)

    db.commit()
    db.refresh(db_icon)
    return db_icon


@router.delete("/icons/{icon_id}")
async def delete_icon(icon_id: str, db: Session = Depends(get_db)):
    """删除图标（软删除）"""
    db_icon = db.query(SimulatorIcon).filter(SimulatorIcon.id == icon_id).first()
    if not db_icon:
        raise HTTPException(status_code=404, detail="Icon not found")

    db_icon.is_active = 0
    db.commit()
    return {"message": "Icon deleted"}


# ============================================
# Preset Endpoints
# ============================================

@router.get("/presets", response_model=List[IconPresetResponse])
async def get_presets(
    category: Optional[str] = None,
    official_only: bool = False,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """获取预设列表"""
    query = db.query(SimulatorIconPreset).filter(SimulatorIconPreset.is_active == 1)

    if category:
        query = query.filter(SimulatorIconPreset.category == category)

    if official_only:
        query = query.filter(SimulatorIconPreset.is_official == 1)

    query = query.order_by(SimulatorIconPreset.is_official.desc(), SimulatorIconPreset.usage_count.desc())
    presets = query.offset(offset).limit(limit).all()

    return presets


@router.get("/presets/{preset_id}", response_model=IconPresetResponse)
async def get_preset(preset_id: str, db: Session = Depends(get_db)):
    """获取单个预设详情"""
    preset = db.query(SimulatorIconPreset).filter(SimulatorIconPreset.id == preset_id).first()
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    return preset


@router.post("/presets", response_model=IconPresetResponse)
async def create_preset(preset: IconPresetCreate, db: Session = Depends(get_db)):
    """创建新预设"""
    existing = db.query(SimulatorIconPreset).filter(SimulatorIconPreset.id == preset.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Preset ID already exists")

    db_preset = SimulatorIconPreset(**preset.model_dump())
    db.add(db_preset)
    db.commit()
    db.refresh(db_preset)
    return db_preset


@router.put("/presets/{preset_id}", response_model=IconPresetResponse)
async def update_preset(preset_id: str, preset: IconPresetCreate, db: Session = Depends(get_db)):
    """更新预设"""
    db_preset = db.query(SimulatorIconPreset).filter(SimulatorIconPreset.id == preset_id).first()
    if not db_preset:
        raise HTTPException(status_code=404, detail="Preset not found")

    for key, value in preset.model_dump().items():
        setattr(db_preset, key, value)

    db.commit()
    db.refresh(db_preset)
    return db_preset


@router.delete("/presets/{preset_id}")
async def delete_preset(preset_id: str, db: Session = Depends(get_db)):
    """删除预设（软删除）"""
    db_preset = db.query(SimulatorIconPreset).filter(SimulatorIconPreset.id == preset_id).first()
    if not db_preset:
        raise HTTPException(status_code=404, detail="Preset not found")

    db_preset.is_active = 0
    db.commit()
    return {"message": "Preset deleted"}


# ============================================
# Utility Endpoints
# ============================================

@router.post("/icons/{icon_id}/usage")
async def increment_icon_usage(icon_id: str, db: Session = Depends(get_db)):
    """增加图标使用次数"""
    db_icon = db.query(SimulatorIcon).filter(SimulatorIcon.id == icon_id).first()
    if db_icon:
        db_icon.usage_count += 1
        db.commit()
    return {"message": "Usage incremented"}


@router.post("/presets/{preset_id}/usage")
async def increment_preset_usage(preset_id: str, db: Session = Depends(get_db)):
    """增加预设使用次数"""
    db_preset = db.query(SimulatorIconPreset).filter(SimulatorIconPreset.id == preset_id).first()
    if db_preset:
        db_preset.usage_count += 1
        db.commit()
    return {"message": "Usage incremented"}


@router.get("/icons/all/list")
async def get_all_icon_ids(db: Session = Depends(get_db)):
    """获取所有图标ID列表（轻量级）"""
    icons = db.query(SimulatorIcon.id, SimulatorIcon.name, SimulatorIcon.category).filter(
        SimulatorIcon.is_active == 1
    ).order_by(SimulatorIcon.category, SimulatorIcon.sort_order).all()

    return [{"id": i.id, "name": i.name, "category": i.category} for i in icons]
