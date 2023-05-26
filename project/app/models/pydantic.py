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


class ProteinJSON(BaseModel):
    primary_accession: str
    sequence: str
