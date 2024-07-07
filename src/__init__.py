from fastapi import APIRouter

from .family_tree.endpoints import router as family_tree_router
from .budget.endpoints import router as budget_router
from .health.endpoints import router as health_router
from .logistics.endpoints import router as logistics_router

combined_router = APIRouter()
combined_router.include_router(family_tree_router)
combined_router.include_router(budget_router)
combined_router.include_router(health_router)
combined_router.include_router(logistics_router)
