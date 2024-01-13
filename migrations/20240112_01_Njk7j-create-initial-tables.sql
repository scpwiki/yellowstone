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
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    created_by TEXT,
    updated_by TEXT,
    title TEXT,
    parent_slug TEXT,
    parent_slug_fetched BOOLEAN DEFAULT false,
    tags TEXT[],
    wikitext BYTEA,
    html BYTEA,
    page_category_id INTEGER,
    discussion_thread_id INTEGER,
    discussion_thread_fetched BOOLEAN DEFAULT false,
    rating REAL,
    comments INTEGER,

    UNIQUE (site_slug, page_slug, deleted_at)
);

CREATE TABLE job (
    job_id SERIAL PRIMARY KEY,
    job_type TEXT NOT NULL,
    job_object TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    data JSON NOT NULL,

    UNIQUE (job_type, job_object)
);

CREATE TABLE job_dead (
    job_id INTEGER PRIMARY KEY,
    buried_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    job_type TEXT NOT NULL,
    job_object TEXT NOT NULL
    data JSON NOT NULL
);
