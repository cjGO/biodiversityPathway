# routers.py
from tortoise.models import Model
from fastapi import APIRouter, HTTPException

from .models import crud
from .models.pydantic import EmbeddingPayloadSchema, ProteinPayloadSchema, ProteinResponseSchema, ProteinJSON, AminoAcidPayloadSchema, ProteinEmbeddingPayloadSchema
from .models.tortoise import Protein, AminoAcid, ProteinEmbeddings
from typing import List

router = APIRouter()





@router.get("/proteins/")
async def get_proteins():
    proteins = await Protein.all()
    return proteins

@router.get("/sequences/")
async def get_sequences():
    seqs = await Protein.all().values('sequence','primary_accession')
    return seqs

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




@router.post("/protein/")
async def create_protein(payload: ProteinPayloadSchema):
    protein = Protein(**payload.dict())
    await protein.save()
    return None


@router.post('/upload_embeddings/')
async def upload_embedding(payload: EmbeddingPayloadSchema):
    return payload



@router.get("/aa_embeddings/")
async def get_aa_embeddings():
    seqs = await AminoAcid.all().values('protein_id','location')
    return seqs

@router.get("/p_embeddings/")
async def get_protein_embeddings():
    seqs = await ProteinEmbeddings.all()
    return seqs

@router.get("/count_aa_embeddings/")
async def get_aa_embeddings():
    seqs = await AminoAcid.all().count()
    return seqs


@router.delete("/delete_all_aa_embeddings/")
async def delete_all_aa_embeddings():
    count = await AminoAcid.all().delete()
    return {"message": f"{count} records deleted successfully!"}

@router.delete("/delete_all_p_embeddings/")
async def delete_all_p_embeddings():
    count = await ProteinEmbeddings.all().delete()
    return {"message": f"{count} records deleted successfully!"}