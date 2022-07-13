-- upgrade --
CREATE TABLE IF NOT EXISTS "cards" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "content" TEXT NOT NULL,
    "creation" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_update" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
) /* ORM card model. */;
CREATE TABLE IF NOT EXISTS "collections" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,
    "is_private" INT NOT NULL  DEFAULT 1,
    "last_update" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
) /* ORM collection model. */;
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);
CREATE TABLE IF NOT EXISTS "collections_cards" (
    "collections_id" INT NOT NULL REFERENCES "collections" ("id") ON DELETE SET NULL,
    "cardtortoise_id" INT NOT NULL REFERENCES "cards" ("id") ON DELETE SET NULL
);
