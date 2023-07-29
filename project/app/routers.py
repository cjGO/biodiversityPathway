# routers.py
from tortoise.models import Model
from fastapi import APIRouter, HTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError

from .models import crud
from .models.pydantic import ProteinUMAPPayloadSchema, EmbeddingPayloadSchema, ProteinPayloadSchema, ProteinResponseSchema, ProteinJSON, AminoAcidPayloadSchema, ProteinEmbeddingPayloadSchema
from .models.tortoise import ProteinUMAP, Protein, AminoAcid, ProteinEmbeddings
from typing import List
from tortoise.transactions import in_transaction
from tortoise.contrib.fastapi import HTTPNotFoundError

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
    try:
        protein = await Protein.get(primary_accession=primary_accession)
        return protein
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Protein not found")


@router.post("/protein/")
async def create_protein(payload: ProteinPayloadSchema):
    protein = Protein(**payload.dict())
    await protein.save()
    return None

@router.post('/upload_embeddings/')
async def upload_embedding(payload: EmbeddingPayloadSchema):
    embedding_size = 320 # HARDCODED, big mistake should have sent this var in payload...
    protein_id = payload.protein_id
    model_name = payload.model_name
    errors = ''

    #confirm protein already exists in database
    try:
        protein = await Protein.get(id=protein_id)
        sequence = protein.sequence
    except DoesNotExist:
        errors += "Protein with the provided id does not exist."

    #confirm the amino acid embeddings haven't already been uploaded
    try:
        # Try to get the AminoAcid, if it exists an error will be thrown
        amino_acid = await AminoAcid.get(protein_id=protein_id, location=1)
        raise IntegrityError("Amino Acid at the provided location for the given protein id already exists.")
    except DoesNotExist:
        pass

    #extract each amino acids individual embedding
    aa_embeddings = payload.embedding_str.split()
    aa_embeddings = [aa_embeddings[i:i+embedding_size] for i in range(0, len(aa_embeddings), embedding_size)]
    for c,i in enumerate(aa_embeddings):
        location = c
        aa_embedding = i
        aa = sequence[location]
        #print(c)
        # create new AminoAcid entry
        await AminoAcid.create(
            amino_acid=aa, 
            location=c, 
            embeddings=aa_embeddings[c], 
            protein_id=protein_id,
        )
    #convert the list of strings into 
    #get protein embedding e.g. average of each aa sublist for each index
    averages = [sum(float(val) for val in values) / len(values) for values in zip(*aa_embeddings)]
    #convert back to a string and round decimals
    protein_embedding = ' '.join(f'{num:.4f}' for num in averages)

    # Try to create the ProteinEmbeddings entry
    try:
        await ProteinEmbeddings.create(
            protein_id = protein_id,
            model_name = model_name,
            embeddings = protein_embedding,
        )
    except IntegrityError:
        errors += "ProteinEmbeddings entry for the given protein and model already exists."
    
    if errors:
        return {"error": errors}
    else:
        return {'ok':'ok'}

@router.get("/aa_embeddings/")
async def get_aa_embeddings():
    seqs = await AminoAcid.all()
    return seqs

@router.get("/p_embeddings/")
async def get_protein_embeddings():
    seqs = await ProteinEmbeddings.all()
    return seqs

@router.get("/count_aa_embeddings/")
async def get_aa_embeddings():
    seqs = await AminoAcid.all().count()
    return seqs

@router.get("/count_p_embeddings/")
async def get_p_embeddings():
    seqs = await ProteinEmbeddings.all().count()
    return seqs


@router.delete("/delete_all_aa_embeddings/")
async def delete_all_aa_embeddings():
    chunk_size = 1000  # Adjust this to a number that your server can handle
    count = 0

    while True:
        async with in_transaction("default") as transaction:
            results = await AminoAcid.all().limit(chunk_size).values_list("id", flat=True)
            if not results:
                break

            await transaction.execute_query("DELETE FROM aminoacid WHERE id IN " + str(tuple(results)))

            count += len(results)

    return {"message": f"{count} records deleted successfully!"}

@router.delete("/delete_all_p_embeddings/")
async def delete_all_p_embeddings():
    count = await ProteinEmbeddings.all().delete()
    return {"message": f"{count} records deleted successfully!"}



@router.post('/upload_umap')
async def upload_umap(payload: ProteinUMAPPayloadSchema):
    # First, we need to ensure that the protein_id provided actually exists in the Protein table
    try:
        protein = await Protein.get(id=payload.protein_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Protein not found")

    # Now we create a new ProteinUMAP object with the data from the request
    protein_umap_obj = ProteinUMAP(
        protein=protein,
        umap_component1=payload.umap_component1,
        umap_component2=payload.umap_component2,
        umap_component3=payload.umap_component3,
        umap_component4=payload.umap_component4,
    )

    # Save the new object to the database
    await protein_umap_obj.save()

    # Return the newly created object
    return 'ok'


@router.get("/protein_umap/{protein_id}", responses={404: {"model": HTTPNotFoundError}})
async def get_protein_umap(protein_id: int):
    protein_umap = await ProteinUMAP.filter(protein_id=protein_id).prefetch_related("protein")
    if not protein_umap:
        raise HTTPException(status_code=404, detail="ProteinUMAP not found")
    return protein_umap

@router.get("/protein_umaps/", responses={404: {"model": HTTPNotFoundError}})
async def get_protein_umaps(protein_ids: str):
    ids = [int(id) for id in protein_ids.split(',')]
    protein_umaps = await ProteinUMAP.filter(protein_id__in=ids).prefetch_related("protein")
    if not protein_umaps:
        raise HTTPException(status_code=404, detail="ProteinUMAPs not found")
    return protein_umaps

@router.get("/protein_umaps", responses={404: {"model": HTTPNotFoundError}})
async def get_all_protein_umaps():
    protein_umaps = await ProteinUMAP.all().prefetch_related("protein")
    if not protein_umaps:
        raise HTTPException(status_code=404, detail="No ProteinUMAPs found")
    return protein_umaps

@router.get("/all_protein_umaps", responses={404: {"model": HTTPNotFoundError}})
async def get_all_protein_umaps():
    protein_umaps = await ProteinUMAP.all().prefetch_related("protein")
    if not protein_umaps:
        raise HTTPException(status_code=404, detail="No ProteinUMAPs found")
    return protein_umaps


@router.get("/amino_acids/{protein_id}", responses={404: {"model": HTTPNotFoundError}})
async def get_amino_acids(protein_id: int):
    try:
        amino_acids = await AminoAcid.filter(protein_id=protein_id).prefetch_related("protein").all()
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="No amino acids found for given protein ID")
    return amino_acids