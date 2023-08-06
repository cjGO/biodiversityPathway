from pydantic import BaseModel
from typing import List,Dict, Optional

class ProteinPayloadSchema(BaseModel):
    primary_accession: str
    sequence: str
    scientific_name: str
    species_name: str
    uniprot_id: str
    biological_process: str
    aa_features:str


class ProteinResponseSchema(ProteinPayloadSchema):
    id: int

class EmbeddingPayloadSchema(BaseModel):
    model_name : str
    embedding_str : str
    protein_id : int
    embedding_size : int

class ProteinJSON(BaseModel):
    primary_accession: str
    sequence: str


class ProteinEmbeddingPayloadSchema(BaseModel):
    protein_id: int
    model_name: str
    embedding: str



class AminoAcidPayloadSchema(BaseModel):
    amino_acid: str
    location: int
    embeddings: str
    protein_id: int

class AminoAcidEmbeddingchema(BaseModel):
    amino_acid_id: int
    location: int
    embeddings: str
    protein_id: int

class ProteinUMAPPayloadSchema(BaseModel):
    protein_id: int
    umap_component1: float
    umap_component2: float
    umap_component3: float
    umap_component4: float

class AminoAcidBindingSiteSchema(BaseModel):
    ligand: str