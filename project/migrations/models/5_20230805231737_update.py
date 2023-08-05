from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "AminoAcidEmbeddings" ADD "embedding_size" INT NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "AminoAcidEmbeddings" DROP COLUMN "embedding_size";"""
