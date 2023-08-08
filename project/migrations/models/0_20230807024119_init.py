from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "protein" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "primary_accession" TEXT NOT NULL,
    "sequence" VARCHAR(10000) NOT NULL UNIQUE,
    "scientific_name" TEXT NOT NULL,
    "species_name" TEXT NOT NULL,
    "uniprot_id" TEXT NOT NULL,
    "biological_process" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "aminoacid" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "amino_acid" VARCHAR(1) NOT NULL,
    "location" INT NOT NULL,
    "binding_site" TEXT,
    "active_site" TEXT,
    "protein_id" INT NOT NULL REFERENCES "protein" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_aminoacid_locatio_7478a0" UNIQUE ("location", "protein_id")
);
CREATE TABLE IF NOT EXISTS "AminoAcidEmbedding" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "model_name" VARCHAR(255) NOT NULL,
    "embeddings" TEXT NOT NULL,
    "amino_acid_id" INT NOT NULL REFERENCES "aminoacid" ("id") ON DELETE CASCADE,
    "protein_id" INT NOT NULL REFERENCES "protein" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_AminoAcidEm_amino_a_4233a4" UNIQUE ("amino_acid_id", "model_name")
);
CREATE TABLE IF NOT EXISTS "protein_embedding" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "model_name" VARCHAR(255) NOT NULL,
    "embeddings" TEXT NOT NULL,
    "protein_id" INT NOT NULL REFERENCES "protein" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_protein_emb_protein_fc7d47" UNIQUE ("protein_id", "model_name")
);
CREATE TABLE IF NOT EXISTS "ProteinUMAP" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "umap_component1" DOUBLE PRECISION NOT NULL,
    "umap_component2" DOUBLE PRECISION NOT NULL,
    "umap_component3" DOUBLE PRECISION NOT NULL,
    "umap_component4" DOUBLE PRECISION NOT NULL,
    "model_name" VARCHAR(255) NOT NULL,
    "protein_id" INT NOT NULL REFERENCES "protein" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
