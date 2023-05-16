# routers.py
from fastapi import APIRouter, HTTPException

from .models import crud
from .models.schemas import ProteinCreate, Protein, FeaturesCreate, Features, EmbeddingsCreate, Embeddings

router = APIRouter()


@router.post("/protein/", response_model=Protein)
async def create_protein(protein: ProteinCreate):
    return await crud.Protein.create(**protein.dict())


@router.get("/protein/{protein_id}", response_model=Protein)
async def get_protein(protein_id: int):
    protein = await crud.Protein.get(id=protein_id)
    if protein is None:
        raise HTTPException(status_code=404, detail="Protein not found")
    return protein


@router.delete("/protein/{protein_id}", response_model=Protein)
async def delete_protein(protein_id: int):
    protein = await crud.Protein.get(id=protein_id)
    if protein is None:
        raise HTTPException(status_code=404, detail="Protein not found")
    await protein.delete()
    return protein

# Repeat the above pattern for Features and Embeddings
