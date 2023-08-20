from tortoise import fields, models

from tortoise import fields, models

class Annotations(models.Model):
    id = fields.IntField(pk=True)
    cell_id = fields.CharField(max_length=255, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    #adding the new fields
    assay = fields.CharField(max_length=255)
    cell_type = fields.CharField(max_length=255)
    disease = fields.CharField(max_length=255)
    donor_id = fields.CharField(max_length=255)
    self_reported_ethnicity = fields.CharField(max_length=255)
    age_group = fields.CharField(max_length=255)
    author_cell_type = fields.CharField(max_length=255)
    bmi_group = fields.CharField(max_length=255)
    procedure_group = fields.CharField(max_length=255)
    breast_density = fields.CharField(max_length=255)
    donor_menopausal_status = fields.CharField(max_length=255)
    sample_source = fields.CharField(max_length=255)
    sequencing_platform = fields.CharField(max_length=255)
    tissue_location = fields.CharField(max_length=255)

    #adding continuous fields
    donor_BMI_at_collection = fields.FloatField()
    suspension_percent_cell_viability = fields.FloatField()
    n_count_rna = fields.FloatField()
    n_feature_rna = fields.FloatField()
    percent_mito = fields.FloatField()
    percent_rb = fields.FloatField()

    #coordinates
    umap_x = fields.FloatField()
    umap_y = fields.FloatField()
