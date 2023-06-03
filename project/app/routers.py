# routers.py
from tortoise.models import Model
from fastapi import APIRouter, HTTPException

from .models import crud
from .models.pydantic import ProteinPayloadSchema, ProteinResponseSchema, ProteinJSON, AminoAcidPayloadSchema, ProteinEmbeddingPayloadSchema
from .models.tortoise import Protein, AminoAcid
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

@router.post("/upload_aminoacid_embedding/")
async def create_amino_acid(amino_acid: AminoAcidPayloadSchema):
    amino_acid_obj = await AminoAcid.create(
        amino_acid=amino_acid.amino_acid,
        location=amino_acid.location,
        embeddings=amino_acid.embeddings,
        protein_id=amino_acid.protein_id,
    )
    return {"message": f'{amino_acid_obj.id} uploaded successfully!'}

@router.post("/upload_protein_embedding/")
async def create_protein_embedding(protein_embed: ProteinEmbeddingPayloadSchema):
    try:
        protein = await Protein.get(id=protein_embed.protein_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Protein not found")

    protein_embedding = await ProteinEmbeddings.create(
        protein_id=protein.id,
        model_name=protein_embed.model_name,
        embeddings=protein_embed.embedding
    )

    return {"message": f"Protein embedding for protein with id {protein.id} has been created successfully."}
