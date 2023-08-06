from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "aminoacid" ALTER COLUMN "binding_site" SET NOT NULL;
        ALTER TABLE "aminoacid" ALTER COLUMN "binding_site" TYPE TEXT USING "binding_site"::TEXT;
        ALTER TABLE "aminoacid" ALTER COLUMN "binding_site" TYPE TEXT USING "binding_site"::TEXT;
        ALTER TABLE "aminoacid" ALTER COLUMN "binding_site" TYPE TEXT USING "binding_site"::TEXT;
        ALTER TABLE "aminoacid" ALTER COLUMN "active_site" SET NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "aminoacid" ALTER COLUMN "binding_site" TYPE VARCHAR(500) USING "binding_site"::VARCHAR(500);
        ALTER TABLE "aminoacid" ALTER COLUMN "binding_site" DROP NOT NULL;
        ALTER TABLE "aminoacid" ALTER COLUMN "binding_site" TYPE VARCHAR(500) USING "binding_site"::VARCHAR(500);
        ALTER TABLE "aminoacid" ALTER COLUMN "binding_site" TYPE VARCHAR(500) USING "binding_site"::VARCHAR(500);
        ALTER TABLE "aminoacid" ALTER COLUMN "active_site" DROP NOT NULL;"""
