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
@router.get('/proteins/')
async def get_proteins():
    total_proteins = await Protein.all().count()
    proteins = await Protein.all().limit(5)
    return {
        'total_proteins': total_proteins,
        'proteins': list(proteins),
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

