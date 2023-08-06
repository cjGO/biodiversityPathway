from tortoise import fields, models


class Protein(models.Model):
    id = fields.IntField(pk=True)  # Added primary key field
    primary_accession = fields.TextField()
    sequence = fields.CharField(unique=True, max_length=10000)
    scientific_name = fields.TextField()
    species_name = fields.TextField()
    uniprot_id = fields.TextField()
    biological_process = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return self.sequence

class AminoAcid(models.Model):
    id = fields.IntField(pk=True)
    amino_acid = fields.CharField(max_length=1)
    location = fields.IntField()
    protein = fields.ForeignKeyField(
        "models.Protein", related_name="amino_acids"
    )
    class Meta:
        unique_together = ("location", "protein")


class AminoAcidEmbedding(models.Model):
    # model_name : str
    # embedding_str : str
    # protein_id : int
    # embedding_size : int
    id = fields.IntField(pk=True)
    amino_acid = fields.ForeignKeyField('models.AminoAcid', related_name='amino_acid_embedding')
    protein = fields.ForeignKeyField('models.Protein', related_name='protein_amino_acid_embedding')
    model_name = fields.CharField(max_length=255)
    embeddings = fields.TextField()
    embedding_size = fields.IntField()

    class Meta:
        table = "AminoAcidEmbedding"
        unique_together = ("amino_acid", "model_name")

    def __str__(self):
        return self.model_name



class ProteinEmbedding(models.Model):
    id = fields.IntField(pk=True)
    protein = fields.ForeignKeyField('models.Protein', related_name='protein_embedding')
    model_name = fields.CharField(max_length=255)
    embeddings = fields.TextField()

    class Meta:
        table = "protein_embeddings"
        unique_together = ("protein", "model_name")

    def __str__(self):
        return self.model_name



class ProteinUMAP(models.Model):
    id = fields.IntField(pk=True)
    protein = fields.ForeignKeyField('models.Protein', related_name='protein_umap', unique=True)
    umap_component1 = fields.FloatField()
    umap_component2 = fields.FloatField()
    umap_component3 = fields.FloatField()
    umap_component4 = fields.FloatField()
    model_name = fields.CharField(max_length=255)
    unique_together = ("protein", "model_name")

    class Meta:
        table = "ProteinUMAP"

    def __str__(self):
        return f"{self.protein.primary_accession}: ({self.umap_component1}, {self.umap_component2} {self.umap_component3} {self.umap_component4})"
