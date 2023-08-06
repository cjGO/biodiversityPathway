from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "AminoAcidEmbedding" DROP COLUMN "embedding_size";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "AminoAcidEmbedding" ADD "embedding_size" INT NOT NULL;"""
