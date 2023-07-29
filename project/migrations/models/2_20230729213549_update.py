from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "aminoacid" ALTER COLUMN "binding" DROP NOT NULL;
        ALTER TABLE "aminoacid" ALTER COLUMN "ligand" DROP NOT NULL;
        ALTER TABLE "aminoacid" ALTER COLUMN "ligand" TYPE VARCHAR(500) USING "ligand"::VARCHAR(500);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "aminoacid" ALTER COLUMN "binding" SET NOT NULL;
        ALTER TABLE "aminoacid" ALTER COLUMN "ligand" SET NOT NULL;
        ALTER TABLE "aminoacid" ALTER COLUMN "ligand" TYPE VARCHAR(50) USING "ligand"::VARCHAR(50);"""
