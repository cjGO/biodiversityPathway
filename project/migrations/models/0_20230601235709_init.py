from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "protein" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "primary_accession" TEXT NOT NULL,
    "sequence" VARCHAR(10000) NOT NULL UNIQUE,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "scientific_name" TEXT NOT NULL,
    "superkingdom" TEXT NOT NULL,
    "kingdom" TEXT NOT NULL,
    "order" TEXT NOT NULL,
    "genus" TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS "aminoacid" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "amino_acid" VARCHAR(1) NOT NULL,
    "location" INT NOT NULL,
    "embeddings" TEXT NOT NULL,
    "protein_id" INT NOT NULL REFERENCES "protein" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "protein_embeddings" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "model_name" VARCHAR(255) NOT NULL,
    "embeddings" TEXT NOT NULL,
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
