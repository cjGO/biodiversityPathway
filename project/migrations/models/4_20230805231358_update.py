from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "AminoAcidEmbeddings" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "model_name" VARCHAR(255) NOT NULL,
    "embeddings" TEXT NOT NULL,
    "amino_acid_id" INT NOT NULL REFERENCES "aminoacid" ("id") ON DELETE CASCADE,
    "protein_id" INT NOT NULL REFERENCES "protein" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_AminoAcidEm_protein_5b2dca" UNIQUE ("protein_id", "model_name")
);;
        DROP TABLE IF EXISTS "aminoacidembeddings";
        CREATE UNIQUE INDEX "uid_protein_emb_protein_15669a" ON "protein_embeddings" ("protein_id", "model_name");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "uid_protein_emb_protein_15669a";
        DROP TABLE IF EXISTS "AminoAcidEmbeddings";"""
