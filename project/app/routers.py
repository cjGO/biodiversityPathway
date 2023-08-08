# routers.py
from tortoise.models import Model
from fastapi import APIRouter, HTTPException, Depends
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

import umap
import numpy as np

router = APIRouter()


def split_list(d_list):
    list1 = []
    list2 = []
    for d in d_list:
        if d['model_name'] == 'facebook/esm2_t33_650M_UR50D':
            list1.append(d)
        else:
            list2.append(d)
    assert len(list1) == len(list2), 'different number of amino acid embeddings per model for same protein'
    return list1, list2


def get_embeddings(d_list):
    return np.array([[float(num) for num in ast.literal_eval(d['embeddings'])] for d in d_list if 'embeddings' in d])


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


@router.get('/run_umap_on_selected_protein/{protein_id}')
async def run_umap_on_a_protein(protein_id:int):
    
    #get the amino acids for that protein
    protein = await Protein.get(id=protein_id)
    amino_acids = await AminoAcid.filter(protein=protein).all().values()
    # Get the amino acids associated with the protein
    aa_embeddings = await AminoAcidEmbedding.filter(protein=protein).all().values()
    #get the embeddings for those amino acids
    big,small = split_list(aa_embeddings)
    amino_acids_dict = {d['id']: d for d in amino_acids}
    
    emb = get_embeddings(small)
    reducer = umap.UMAP(n_components=4)
    small_umap = reducer.fit_transform(emb)
    emb = get_embeddings(big)
    reducer = umap.UMAP(n_components=4)
    big_umap = reducer.fit_transform(emb)

    return_dict = []
    count = 0
    for R,B,S in zip(amino_acids, big_umap, small_umap):
        dict_lookup = amino_acids_dict[R['id']]
        entry = {
            'binding_site':dict_lookup['binding_site'],
            'active_site':dict_lookup['active_site'],
            'location':dict_lookup['location'],
            'amino_acid_id':R['id'],
            'protein_id':R['protein_id'],
            'facebook/esm2_t6_8M_UR50D_umap_component_1':float(S[0]) ,
            'facebook/esm2_t6_8M_UR50D_umap_component_2':float(S[1]) ,
            'facebook/esm2_t6_8M_UR50D_umap_component_3':float(S[2]),
            'facebook/esm2_t6_8M_UR50D_umap_component_4':float(S[3]) ,
            'facebook/esm2_t33_650M_UR50D_umap_component_1':float(B[0]),
            'facebook/esm2_t33_650M_UR50D_umap_component_2':float(B[1]) ,
            'facebook/esm2_t33_650M_UR50D_umap_component_3':float(B[2]) ,
            'facebook/esm2_t33_650M_UR50D_umap_component_4':float(B[3]),
            'id':count,
            'amino_acid':R['amino_acid'],
        }
        count+=1
        return_dict.append(entry)
    return return_dict

@router.get('/do_umap_protein')
async def do_umap_for_a_protein():
    return 'test'


@router.get("/grab_protein_umap_both")
async def grab_both_umap_embeddings_for_all_proteins():

    def combine_dicts(dict_list):
        result = {}
        for d in dict_list:
            for k, v in d.items():
                if k.startswith('umap_component'):
                    new_key = d['model_name'] + "_" + k
                    result[new_key] = v
                else:
                    result[k] = v
        return result

    def get_unique_protein_id(proteins):
        unique_protein_ids = set()
        for protein in proteins:
            unique_protein_ids.add(protein['protein_id'])
        return unique_protein_ids

    consolidation = [] 
    proteins = await ProteinUMAP.all().values()
    unique_protein_ids = get_unique_protein_id(proteins)
    for i in unique_protein_ids:
        i_protein = await ProteinUMAP.filter(protein_id = i).values()
        consolidation.append(combine_dicts(i_protein))
    return consolidation
    

@router.get("/grab_aa_embeddings_full/{protein_id}")
async def read_protein(protein_id: int):
    protein = await Protein.get(id=protein_id)
    if not protein:
        raise HTTPNotFoundError(detail=f"Protein {protein_id} not found")
    amino_acids = await AminoAcid.filter(protein=protein)
    amino_acid_embeddings = await AminoAcidEmbedding.filter(protein=protein).prefetch_related('amino_acid')

    # Create a new list to hold the combined data
    combined_data = []
    
    # Add additional fields to AminoAcidEmbedding objects
    # Add additional fields to AminoAcidEmbedding objects
    for embedding in amino_acid_embeddings:
        if embedding.model_name == 'facebook/esm2_t6_8M_UR50D':
            embeddings = embedding.embeddings
            model_name = embedding.model_name
            amino_acid = embedding.amino_acid.amino_acid
            location = embedding.amino_acid.location
            aa_id = embedding.id
            binding_site = embedding.amino_acid.binding_site
            active_site = embedding.amino_acid.active_site

            combined_data.append({'amino_acid':amino_acid,
            'model_name':model_name,
            'amino_acid':amino_acid,
            'location':location,
            'id':aa_id,
            'binding_site':binding_site,
            'active_site':active_site,
            'embeddings':embeddings})
    combined_data = sorted(combined_data, key=lambda x: x['location'])

    return combined_data
    


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
@router.get("/protein_embeddings/{model_name}", responses={404: {"model": HTTPNotFoundError}})
async def get_protein_embeddings_by_model_name(model_name: str):
    try:
        embeddings = await ProteinEmbedding.filter(model_name=model_name).all()
        if not embeddings:
            raise HTTPException(status_code=404, detail="Embeddings not found")
        return embeddings
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Model not found")



@router.get("/protein_embeddings/unique_model_names")
async def get_unique_model_names():
    model_names = await ProteinEmbedding.all().values('model_name').distinct()
    return [item['model_name'] for item in model_names]



@router.get('/get_all_protein/')
async def get_all_protein():
    total_proteins = await Protein.all().count()
    proteins = await Protein.all()
    return proteins

@router.get('/proteins/')
async def get_proteins():
    total_proteins = await Protein.all().count()
    proteins = await Protein.all()
    return proteins
@router.get("/check-existence/")
async def check_existence(protein_id: int, model_name: str):
    exists = await ProteinEmbedding.filter(protein_id=protein_id, model_name=model_name).exists()
    return {"exists": exists}

@router.get('/protein/{protein_id}/amino_acids/')
async def get_amino_acids_for_protein(protein_id: int):
    try:
        # Ensure the protein with the given ID exists in the database
        protein = await Protein.get(id=protein_id)

        # Get the amino acids associated with the protein
        amino_acids = await AminoAcid.filter(protein=protein).all()

        return {
            'protein_id': protein_id,
            'amino_acids': list(amino_acids),
        }
        
    except Protein.DoesNotExist:
        raise HTTPException(status_code=404, detail="Protein not found")

@router.get('/amino_acids/')
async def get_amino_acids():
    total_amino_acids = await AminoAcid.all().count()
    amino_acids = await AminoAcid.all()
    return {
        'total_amino_acids': total_amino_acids,
        'amino_acids': list(amino_acids),
    }
@router.get('/amino_acids_with_binding_site/')
async def get_amino_acids_with_binding_site():
    amino_acids_with_binding_site_count = await AminoAcid.filter(binding_site__isnull=False).count()
    return {
        'amino_acids_with_binding_site_count': amino_acids_with_binding_site_count
    }
@router.get('/amino_acids_with_active_site/')
async def get_amino_acids_with_active_site():
    amino_acids_with_active_site_count = await AminoAcid.filter(active_site__isnull=False).count()
    return {
        'amino_acids_with_active_site_count': amino_acids_with_active_site_count
    }
@router.get('/protein_ids/')
async def get_protein_ids():
    proteins = await Protein.all().values('id')
    protein_ids = [protein['id'] for protein in proteins]
    return {
        'protein_ids': protein_ids
    }

@router.get('/umaps/')
async def get_umaps():
    total_amino_acids = await ProteinUMAP.all().count()
    amino_acids = await ProteinUMAP.all().limit(5)
    return {
        'total_amino_acids': total_amino_acids,
        'amino_acids': list(amino_acids),
    }

@router.get('/aa_embeds/')
async def get_basic_aa_embeds():
    total_amino_acids = await AminoAcidEmbedding.all().count()
    amino_acids = await AminoAcidEmbedding.all().limit(5)
    return {
        'total_amino_acids': total_amino_acids,
        'amino_acids': list(amino_acids),
    }

@router.get('/umap/')
async def get_umap_model(model_name:str):
    umap = await ProteinUMAP.all().limit(5)



@router.get('/model_umaps/')
async def get_umap_model(model_name: str):
    try:
        # Get ProteinUMAP entries where the model_name matches the given model_name
        umap = await ProteinUMAP.filter(model_name=model_name).all()

        if not umap:
            raise DoesNotExist

        return umap
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"No ProteinUMAP found for model_name: {model_name}")

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
from fastapi import HTTPException

from fastapi import HTTPException



@router.get("/amino_acid_embedding/protein/{protein_id}")
async def get_amino_acid_embedding_by_protein(protein_id: int):
    amino_acid_embeddings = await AminoAcidEmbedding.filter(protein=protein_id).prefetch_related("amino_acid")
    return amino_acid_embeddings

class EmbeddingRequest(BaseModel):
    protein_id: int
    model_name: str
@router.get("/amino_acid_embedding/protein")
async def get_amino_acid_embedding_by_protein_and_model(embedding_request: EmbeddingRequest):
    amino_acid_embeddings = await AminoAcidEmbedding.filter(
        protein_id=embedding_request.protein_id, model_name=embedding_request.model_name
    ).prefetch_related("amino_acid")
    return amino_acid_embeddings



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
        
        activeSite = None  # Initialize activeSite to empty string
        bs = None  # Initialize bs to empty string

        if 'Binding site' in x:
            bs = x['Binding site']

        if 'Active site' in x:
            activeSite = x['Active site']

        aa = await AminoAcid.create(
            amino_acid=payload.sequence[c],
            location=int(c),
            protein=protein,
            binding_site = bs,
            active_site = activeSite
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
    for c, i in enumerate(aa_embeddings):
        amino_acid = await AminoAcid.get(protein_id=protein_id, location=c)
        location = c
        aa_embedding = i
        aa = sequence[location]

        # Check if an entry with the same model_name and protein_id already exists
        is_existing = await AminoAcidEmbedding.filter(
            amino_acid=amino_acid,
            protein=protein,
            model_name=payload.model_name
        ).exists()

        if not is_existing:
            await AminoAcidEmbedding.create(
                amino_acid=amino_acid,
                protein=protein,
                model_name=payload.model_name,
                embeddings=i
            )
        else:
            errors += f"AminoAcidEmbedding entry for location {location} with model_name {payload.model_name} and protein_id {protein_id} already exists.\n"


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




@router.post("/upload_protein_umap/")
async def upload_protein_umap(payload: ProteinUMAPPayloadSchema):
    
    protein = await Protein.get_or_none(id=payload.protein_id)
    if not protein:
        raise HTTPException(status_code=404, detail="Protein not found")

    try:
        protein_umap_obj = await ProteinUMAP.create(
            protein=protein,
            model_name=payload.model_name,
            umap_component1=payload.umap_component1,
            umap_component2=payload.umap_component2,
            umap_component3=payload.umap_component3,
            umap_component4=payload.umap_component4,
        )
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Data already exists for this Protein and Model Name")
    
    return {"id": protein_umap_obj.id}

@router.delete('/delete_all_umaps/')
async def delete_all_umaps():
    await ProteinUMAP.all().delete()
    return {"status": "All ProteinUMAP entries deleted successfully"}

@router.delete('/delete_all_aa_embed/')
async def delete_all_aa_embed():
    await AminoAcidEmbedding.all().delete()
    return {"status": "All ProteinUMAP entries deleted successfully"}


@router.get('/get_aa_embeddings')
async def get_aa_embeddings():
    amino_acids = await AminoAcidEmbedding.all().limit(1000)
    return amino_acids
