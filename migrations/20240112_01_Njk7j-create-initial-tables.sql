-- Create initial tables.
-- depends:

CREATE TABLE site (
    site_slug TEXT PRIMARY KEY,
    wikidot_id INTEGER NOT NULL,
    home_slug TEXT NOT NULL,
    language TEXT NOT NULL,

    UNIQUE (wikidot_id)
);

-- Content-based hash using kangarootwelve
CREATE TABLE text (
    hash BYTEA PRIMARY KEY,
    contents TEXT COMPRESSION pglz NOT NULL,

    CHECK (length(hash) = 16)  -- KangarooTwelve hash size, 128 bits
);

CREATE TABLE page (
    site_slug TEXT FOREIGN KEY site(site_slug),
    page_slug TEXT NOT NULL,
    page_id INTEGER,
    deleted_at TIMESTAMP WITH TIME ZONE,
    wikitext BYTEA,
    html BYTEA,
    page_category_id INTEGER,
    discussion_thread_id INTEGER,
    discussion_thread_fetched BOOLEAN DEFAULT false,

    UNIQUE (site_slug, page_slug, deleted_at)
);
