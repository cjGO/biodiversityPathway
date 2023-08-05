from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "aminoacid" DROP COLUMN "embeddings";
        CREATE TABLE IF NOT EXISTS "aminoacidembeddings" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "model_name" VARCHAR(255) NOT NULL,
    "embeddings" TEXT NOT NULL,
    "amino_acid_id" INT NOT NULL REFERENCES "aminoacid" ("id") ON DELETE CASCADE,
    "protein_id" INT NOT NULL REFERENCES "protein" ("id") ON DELETE CASCADE
);;
        ALTER TABLE "ProteinUMAP" ADD "model_name" VARCHAR(255) NOT NULL  DEFAULT 'esm2_t6_8M_UR50D';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "aminoacid" ADD "embeddings" TEXT NOT NULL;
        ALTER TABLE "ProteinUMAP" DROP COLUMN "model_name";
        DROP TABLE IF EXISTS "aminoacidembeddings";"""
