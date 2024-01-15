-- Create initial tables.
-- depends:

SET default_toast_compression=lz4;

CREATE TABLE site (
    site_slug TEXT PRIMARY KEY,
    wikidot_id INTEGER NOT NULL UNIQUE,
    home_slug TEXT NOT NULL,
    language TEXT NOT NULL
);

CREATE TABLE "user" (
    user_slug TEXT PRIMARY KEY,
    user_name TEXT NOT NULL,
    wikidot_id INTEGER NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL,
    real_name TEXT,
    gender TEXT,
    birthday DATE,
    location TEXT,
    website TEXT,
    bio TEXT,
    wikidot_pro BOOLEAN NOT NULL,
    karma SMALLINT NOT NULL CHECK (0 <= karma AND karma <= 5),
    avatar BYTEA CHECK (avatar IS NULL OR length(avatar) = 64)  -- SHA-512 hash size
);

CREATE TABLE site_member (
    user_id INTEGER NOT NULL,
    site_id INTEGER NOT NULL,
    joined_at TIMESTAMP WITH TIME ZONE NOT NULL,

    PRIMARY KEY (user_id, site_id)
);

-- Content-based hash using kangarootwelve
CREATE TABLE text (
    hash BYTEA PRIMARY KEY,
    contents TEXT NOT NULL,

    CHECK (length(hash) = 16)  -- KangarooTwelve hash size, 128 bits
);

CREATE TABLE page (
    site_slug TEXT REFERENCES site(site_slug),
    page_slug TEXT NOT NULL,
    page_id INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    created_by INTEGER NOT NULL REFERENCES "user"(wikidot_id),
    updated_by INTEGER REFERENCES "user"(wikidot_id),
    title TEXT NOT NULL,
    parent_page_slug TEXT,
    tags TEXT[] NOT NULL,
    wikitext BYTEA NOT NULL REFERENCES text(hash),
    html BYTEA NOT NULL REFERENCES text(hash),
    page_category_id INTEGER NOT NULL,
    discussion_thread_id INTEGER,
    rating REAL NOT NULL,
    comments INTEGER NOT NULL,

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
    job_object TEXT NOT NULL,
    data JSON NOT NULL
);
