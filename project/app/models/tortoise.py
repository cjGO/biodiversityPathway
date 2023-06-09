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


    def __str__(self):
        return self.sequence

class AminoAcid(models.Model):
    id = fields.IntField(pk=True)
    amino_acid = fields.CharField(max_length=1)
    location = fields.IntField()
    embeddings = fields.TextField()
    protein = fields.ForeignKeyField(
        "models.Protein", related_name="amino_acids"
    )

    class Meta:
        unique_together = ("location", "protein")

class ProteinEmbeddings(models.Model):
    id = fields.IntField(pk=True)
    protein = fields.ForeignKeyField('models.Protein', related_name='protein_embeddings')
    model_name = fields.CharField(max_length=255)
    embeddings = fields.TextField()

    class Meta:
        table = "protein_embeddings"

    def __str__(self):
        return self.model_name


class ProteinUMAP(models.Model):
    id = fields.IntField(pk=True)
    protein = fields.ForeignKeyField('models.Protein', related_name='protein_umap')
    umap_component1 = fields.FloatField()
    umap_component2 = fields.FloatField()
    umap_component3 = fields.FloatField()
    umap_component4 = fields.FloatField()

    class Meta:
        table = "ProteinUMAP"

    def __str__(self):
        return f"{self.protein.primary_accession}: ({self.umap_component1}, {self.umap_component2} {self.umap_component3} {self.umap_component4})"


#todo AAfeatures table -> mark which aa are in functional domains 