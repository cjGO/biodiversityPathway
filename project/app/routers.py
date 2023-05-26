# routers.py
from fastapi import APIRouter, HTTPException

from .models import crud
from .models.pydantic import ProteinPayloadSchema, ProteinResponseSchema
from .models.tortoise import Protein

router = APIRouter()


@router.post("/protein/")
async def create_protein(payload: ProteinPayloadSchema):
    protein = Protein(**payload.dict())
    await protein.save()
    return None


@router.get("/proteins/")
async def get_proteins():
    proteins = await Protein.all()
    return proteins


@router.delete("/protein/{protein_id}")
async def delete_protein(protein_id: int):
    protein_obj = await Protein.filter(id=protein_id).prefetch_related("protein_obj").first()
    if not protein_obj:
        raise HTTPException(
            status_code=404, detail="Protein with ID {} not found".format(protein_id))
    await delete_object(Protein, protein_id)
    return {"message": "Protein with ID {} has been deleted".format(protein_id)}


@router.delete("/protein/")
async def delete_all_proteins():
    entries_to_delete = Protein.all()
    await entries_to_delete.delete()
    return {"message": "All proteins have been deleted"}


@router.get("/protein_count/")
async def count_all_proteins():
    total_protein_entries = await Protein.all().count()
    return {"count": total_protein_entries}


@router.get("/protein/{primary_accession}")
async def check_protein_exists(primary_accession: str):
    protein = await Protein.get(primary_accession=primary_accession)
    if protein:
        return {"exists": True}
    else:
        return {'exists': False}
