from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise import fields, models


class Protein(models.Model):
    id = fields.IntField(pk=True)  # Added primary key field
    primary_accession = fields.TextField()
    sequence = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    scientific_name = fields.TextField()
    common_name = fields.TextField()
    superkingdom = fields.TextField()
    kingdom = fields.TextField()
    order = fields.TextField()
    family = fields.TextField()
    genus = fields.TextField()

    features: fields.ReverseRelation["Features"]  # Added type hint

    def __str__(self):
        return self.sequence


class Features(models.Model):
    id = fields.IntField(pk=True)  # Added primary key field
    protein = fields.ForeignKeyField(
        "models.Protein", related_name="features")  # Changed related_name
    type = fields.TextField()
    description = fields.TextField()
    ligand = fields.TextField()
    start = fields.IntField()
    end = fields.IntField()

    protein_rel: fields.ForeignKeyRelation[Protein]  # Added type hint


class Embeddings(models.Model):  # Changed models.Models to models.Model
    id = fields.IntField(pk=True)  # Added primary key field
    protein = fields.ForeignKeyField(
        "models.Protein", related_name="embeddings")
    embedding = fields.TextField()
    model_name = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    protein_rel: fields.ForeignKeyRelation[Protein]  # Added type hint


Protein_Pydantic = pydantic_model_creator(Protein, name="Protein")
ProteinIn_Pydantic = pydantic_model_creator(
    Protein, name="ProteinIn", exclude_readonly=True)

Features_Pydantic = pydantic_model_creator(Features, name="Features")
FeaturesIn_Pydantic = pydantic_model_creator(
    Features, name="FeaturesIn", exclude_readonly=True)

Embeddings_Pydantic = pydantic_model_creator(Embeddings, name="Embeddings")
EmbeddingsIn_Pydantic = pydantic_model_creator(
    Embeddings, name="EmbeddingsIn", exclude_readonly=True)
