# schemas.py
from pydantic import BaseModel


class ProteinBase(BaseModel):
    primary_accession: str
    sequence: str
    scientific_name: str
    common_name: str
    superkingdom: str
    kingdom: str
    order: str
    family: str
    genus: str


class ProteinCreate(ProteinBase):
    pass


class Protein(ProteinBase):
    id: int

    class Config:
        orm_mode = True


class FeaturesBase(BaseModel):
    type: str
    description: str
    ligand: str
    start: int
    end: int


class FeaturesCreate(FeaturesBase):
    pass


class Features(FeaturesBase):
    id: int
    protein_id: int

    class Config:
        orm_mode = True


class EmbeddingsBase(BaseModel):
    embedding: str
    model_name: str


class EmbeddingsCreate(EmbeddingsBase):
    pass


class Embeddings(EmbeddingsBase):
    id: int
    protein_id: int

    class Config:
        orm_mode = True
