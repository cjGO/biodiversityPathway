# routers.py
from tortoise.models import Model
from fastapi import APIRouter, HTTPException, Depends
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.contrib.pydantic import pydantic_queryset_creator
from tortoise.functions import Count

from .models import crud
from .models.pydantic import AminoAcidBindingSiteSchema,ProteinUMAPPayloadSchema, EmbeddingPayloadSchema, ProteinPayloadSchema, ProteinResponseSchema, ProteinJSON, AminoAcidPayloadSchema, ProteinEmbeddingPayloadSchema
from .models.clones import Annotations
from typing import List
from tortoise.transactions import in_transaction
from tortoise.contrib.fastapi import HTTPNotFoundError
import ast

from pydantic import BaseModel
from typing import List,Dict, Optional



clone_router = APIRouter()


class SingleCellPayloadSchema(BaseModel):
    cell_id : str
    assay : str
    cell_type : str
    disease : str
    donor_id : str
    self_reported_ethnicity : str
    age_group : str
    author_cell_type : str
    bmi_group : str
    procedure_group : str

    breast_density : str
    donor_menopausal_status : str
    sequencing_platform : str
    sample_source : str
    tissue_location : str

    donor_BMI_at_collection : float
    suspension_percent_cell_viability : float
    n_count_rna : float
    n_feature_rna : float
    percent_mito : float

    percent_rb : float
    umap_x : float
    umap_y : float


from fastapi import HTTPException

@clone_router.post('/upload_sc/')
async def upload_sc(body: List[SingleCellPayloadSchema]):
    # Convert each item in the body to a dictionary
    data = [item.dict() for item in body]

    # Create new annotations with the data
    annotations = [Annotations(**item) for item in data]

    # Save the new annotations to the database
    try:
        await Annotations.bulk_create(annotations)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Could not save to database")

    # Return the saved annotations as dictionaries
    return 'Good'


@clone_router.get('/annotations/')
async def get_annotations():
    # Fetch all annotations from the database
    annotations = await Annotations.all()

    # Convert the annotations to dictionaries and return them
    return annotations

@clone_router.get('/annotations/count')
async def count_annotations():
    # Count all annotations in the database
    count = await Annotations.all().count()

    # Return the count
    return {"count": count}

from fastapi import HTTPException
import random

@clone_router.get('/random_annotations/')
async def get_random_annotations():
    # Fetch all annotations from the database
    annotations = await Annotations.all()

    if not annotations:
        raise HTTPException(status_code=404, detail="Annotations not found")

    # Shuffle the annotations
    random.shuffle(annotations)

    # Create a new list of annotation objects without 'cell_id' and 'created_at'
    new_annotations = []
    for annotation in annotations:
        # Get the dictionary of the annotation object
        annotation_dict = annotation.__dict__

        # Remove 'cell_id' and 'created_at' from the dictionary
        annotation_dict.pop('cell_id', None)
        annotation_dict.pop('created_at', None)

        # Create a new annotation object from the modified dictionary and add it to the new list
        new_annotation = Annotations(**annotation_dict)
        new_annotations.append(new_annotation)

    # Return the first 1000 annotations from the new list
    return new_annotations[:1000]
