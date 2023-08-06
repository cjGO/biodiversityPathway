from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "aminoacid" DROP COLUMN "active_site";
        ALTER TABLE "aminoacid" DROP COLUMN "binding_site";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "aminoacid" ADD "active_site" TEXT NOT NULL;
        ALTER TABLE "aminoacid" ADD "binding_site" TEXT NOT NULL;"""
