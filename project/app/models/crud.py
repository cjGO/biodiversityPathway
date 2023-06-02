# crud.py
from tortoise.contrib.pydantic import pydantic_model_creator

from .tortoise import Protein

Protein_Pydantic = pydantic_model_creator(Protein)
