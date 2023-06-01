from tortoise import fields, models


class Protein(models.Model):
    id = fields.IntField(pk=True)  # Added primary key field
    primary_accession = fields.TextField()
    sequence = fields.CharField(unique=True, max_length=10000)
    created_at = fields.DatetimeField(auto_now_add=True)
    scientific_name = fields.TextField()
    superkingdom = fields.TextField()
    kingdom = fields.TextField()
    order = fields.TextField()
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

class AminoAcid(models.Model):
    id = fields.IntField(pk=True)
    amino_acid = fields.CharField(max_length=1)
    location = fields.IntField()
    embedding = fields.TextField()
    protein = fields.ForeignKeyField(
        "models.Protein", related_name="amino_acid")
    protein_rel: fields.ForeignKeyRelation[Protein]  # Added type hint
