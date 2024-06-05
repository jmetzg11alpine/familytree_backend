from fastapi import APIRouter

from src.family_tree.endpoints import router as family_tree_router
from src.budget.endpoints import router as budget_router

combined_router = APIRouter()
combined_router.include_router(family_tree_router)
combined_router.include_router(budget_router)
