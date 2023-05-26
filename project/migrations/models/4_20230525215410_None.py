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
CREATE TABLE IF NOT EXISTS "embeddings" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "embedding" TEXT NOT NULL,
    "model_name" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "protein_id" INT NOT NULL REFERENCES "protein" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "features" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "type" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "ligand" TEXT NOT NULL,
    "start" INT NOT NULL,
    "end" INT NOT NULL,
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
