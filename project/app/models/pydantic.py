from pydantic import BaseModel


class ProteinPayloadSchema(BaseModel):
    primary_accession: str
    sequence: str
    scientific_name: str
    superkingdom: str
    kingdom: str
    order: str
    genus: str


class ProteinResponseSchema(ProteinPayloadSchema):
    id: int

class EmbeddingPayloadSchema(BaseModel):
    model_name : str
    embedding_str : str
    protein_id : int
    

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