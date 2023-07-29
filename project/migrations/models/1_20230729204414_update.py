from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "aminoacid" ADD "ligand" VARCHAR(50) NOT NULL;
        ALTER TABLE "aminoacid" ADD "binding" BOOL NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "aminoacid" DROP COLUMN "ligand";
        ALTER TABLE "aminoacid" DROP COLUMN "binding";"""
