# crud.py
from tortoise.contrib.pydantic import pydantic_model_creator

from .tortoise import Protein, Features, Embeddings

Protein_Pydantic = pydantic_model_creator(Protein)
Features_Pydantic = pydantic_model_creator(Features)
Embeddings_Pydantic = pydantic_model_creator(Embeddings)
