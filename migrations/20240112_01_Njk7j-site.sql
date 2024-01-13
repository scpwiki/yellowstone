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

-- Content-based hash using kangarootwelve
CREATE TABLE text (
    hash BYTEA PRIMARY KEY,
    contents TEXT COMPRESSION pglz NOT NULL,

    CHECK (length(hash) = 16)  -- KangarooTwelve hash size, 128 bits
);

