-- Create initial tables.
-- depends:

CREATE TABLE site (
    slug TEXT PRIMARY KEY,
    wikidot_id INTEGER NOT NULL,
    home_slug TEXT NOT NULL,
    domain TEXT NOT NULL,
    language TEXT NOT NULL,

    UNIQUE (wikidot_id)
);
