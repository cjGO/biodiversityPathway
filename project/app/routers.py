# routers.py
from tortoise.models import Model
from fastapi import APIRouter, HTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.contrib.pydantic import pydantic_queryset_creator
from tortoise.functions import Count

from .models import crud
from .models.pydantic import AminoAcidBindingSiteSchema,ProteinUMAPPayloadSchema, EmbeddingPayloadSchema, ProteinPayloadSchema, ProteinResponseSchema, ProteinJSON, AminoAcidPayloadSchema, ProteinEmbeddingPayloadSchema
from .models.tortoise import ProteinUMAP, Protein, AminoAcid, ProteinEmbedding, AminoAcidEmbedding
from typing import List
from tortoise.transactions import in_transaction
from tortoise.contrib.fastapi import HTTPNotFoundError
import ast

from pydantic import BaseModel
from typing import List,Dict, Optional


router = APIRouter()

def scan_features(aa_feature_list, index):
  hits = {}
  for i in aa_feature_list:
      if (i['type'] == 'Binding site'):
          start = i['location']['start']['value']
          end = i['location']['end']['value']
          if start <= index <= end:
            hits['Binding site'] = i['ligand']['name']
      if (i['type'] == 'Active site'):
          start = i['location']['start']['value']
          end = i['location']['end']['value']
          if start <= index <= end:
            hits['Active site'] = i['description']
  return hits


    # aa_feature_list = ast.literal_eval(payload.aa_features)
    # for i in aa_feature_list:
    #     if ((i['type'] == 'Binding site') or (i['type'] == 'Active site')):
    #         print(i)

    #Make new Protein entry

# @router.post('/upload_uniprot_protein/')
# async def upload_uniprot_protein(payload: ProteinPayloadSchema):
    # PAYLOAD SCHEMA
    # primary_accession: str
    # sequence: str
    # scientific_name: str
    # species_name: str
    # uniprot_id: str
    # biological_process: str
    # aa_features:str

    # protein = await Protein.create()(
    #     primary_accession=payload.primary_accession,
    #     sequence=payload.sequence,
    #     scientific_name=payload.scientific_name,
    #     species_name=payload.species_name,
    #     uniprot_id=payload.uniprot_id,
    #     biological_process=payload.biological_process,
    # )

@router.get('/get_all_protein/')
async def get_all_protein():
    total_proteins = await Protein.all().count()
    proteins = await Protein.all()
    return proteins

@router.get('/proteins/')
async def get_proteins():
    total_proteins = await Protein.all().count()
    proteins = await Protein.all().limit(5)
    return {
        'total_proteins': total_proteins,
        'proteins': list(proteins),
    }
@router.get('/amino_acids/')
async def get_amino_acids():
    total_amino_acids = await AminoAcid.all().count()
    amino_acids = await AminoAcid.all().limit(5)
    return {
        'total_amino_acids': total_amino_acids,
        'amino_acids': list(amino_acids),
    }

@router.get('/umaps/')
async def get_umaps():
    total_amino_acids = await ProteinUMAP.all().count()
    amino_acids = await ProteinUMAP.all().limit(5)
    return {
        'total_amino_acids': total_amino_acids,
        'amino_acids': list(amino_acids),
    }


@router.get('/get_protein_embedding/')
async def get_protein_embedding(model_name: Optional[str] = None):
    if model_name:
        total_embeddings = await ProteinEmbedding.filter(model_name=model_name).count()
        embeddings = await ProteinEmbedding.filter(model_name=model_name)
    else:
        total_embeddings = await ProteinEmbedding.all().count()
        embeddings = await ProteinEmbedding.all()

    return {
        'total_embeddings': total_embeddings,
        'embeddings': list(embeddings),
    }

@router.post('/upload_uniprot_protein/')
async def upload_uniprot_protein(payload: ProteinPayloadSchema):
    
    existing_protein = await Protein.filter(primary_accession=payload.primary_accession).first()
    if existing_protein:
        print('it exists!')
        protein = existing_protein  # use the existing protein for further operations
    else:
        protein = await Protein.create(
            primary_accession=payload.primary_accession,
            sequence=payload.sequence,
            scientific_name=payload.scientific_name,
            species_name=payload.species_name,
            uniprot_id=payload.uniprot_id,
            biological_process=payload.biological_process,
        )


    #handle amino acids
    aa_feature_list = ast.literal_eval(payload.aa_features)
    for i in aa_feature_list:
        if i['type'] == 'Binding site':
            print(i)
    # Inside your loop:
    for c, i in enumerate(payload.sequence):
        x = scan_features(aa_feature_list, c)
        
        activeSite = ''  # Initialize activeSite to empty string
        bs = ''  # Initialize bs to empty string

        if 'Binding site' in x:
            bs = x['Binding site']

        if 'Active site' in x:
            activeSite = x['Active site']

        aa = await AminoAcid.create(
            amino_acid=payload.sequence[c],
            location=int(c),
            protein=protein,
        )




class EmbeddingPayloadSchema(BaseModel):
    model_name : str
    embedding_str : str
    protein_id : int
    embedding_size : int

@router.post('/upload_embeddings/')
async def upload_embedding(payload: EmbeddingPayloadSchema):
    embedding_size = payload.embedding_size
    protein_id = payload.protein_id
    model_name = payload.model_name
    errors = ''

    #confirm protein already exists in database
    try:
        protein = await Protein.get(id=protein_id)
        sequence = protein.sequence
    except DoesNotExist:
        errors += "Protein with the provided id does not exist."


    #extract each amino acids individual embedding
    aa_embeddings = payload.embedding_str.split()
    aa_embeddings = [aa_embeddings[i:i+embedding_size] for i in range(0, len(aa_embeddings), embedding_size)]
    for c,i in enumerate(aa_embeddings):
        amino_acid = await AminoAcid.get(protein_id=protein_id, location=c)
        location = c
        aa_embedding = i
        aa = sequence[location]

        AminoAcidEmbedding.create(
            amino_acid = amino_acid,
            protein = protein,
            model_name = payload.model_name,
            embeddings = aa
        )

    #convert the list of strings into 
    #get protein embedding e.g. average of each aa sublist for each index
    averages = [sum(float(val) for val in values) / len(values) for values in zip(*aa_embeddings)]
    #convert back to a string and round decimals
    protein_embedding = ' '.join(f'{num:.4f}' for num in averages)

    # Try to create the ProteinEmbeddings entry
    try:
        await ProteinEmbedding.create(
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




class ProteinUMAPPayloadSchema(BaseModel):
    protein_id: int
    model_name: str
    umap_component1: float
    umap_component2: float
    umap_component3: float
    umap_component4: float
    

@router.post('/upload_protein_umap')
async def upload_protein_umap(payload: ProteinUMAPPayloadSchema):
    errors = ''
    #check if ProteinUMAP is already uploaded for given protein and model_name
    #confirm protein already exists in database
    exists = await ProteinUMAP.filter(protein_id=payload.protein_id, model_name=payload.model_name).exists()
    print('exists', exists)
    if exists:
        return 'UMAP already exists for this protein/model'

    protein_instance = await Protein.get(id=payload.protein_id)
    await ProteinUMAP.create(
        model_name=payload.model_name,
        protein = protein_instance,
        umap_component1=payload.umap_component1,
        umap_component2=payload.umap_component2,
        umap_component3=payload.umap_component3,
        umap_component4=payload.umap_component4,
    )

    print('created')
    return payload

@router.delete('/delete_all_umaps/')
async def delete_all_umaps():
    await ProteinUMAP.all().delete()
    return {"status": "All ProteinUMAP entries deleted successfully"}
