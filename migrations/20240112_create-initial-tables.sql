-- Create initial tables.
-- depends:

SET default_toast_compression=lz4;

CREATE TABLE site (
    site_slug TEXT PRIMARY KEY,
    site_id INTEGER NOT NULL UNIQUE,
    home_slug TEXT NOT NULL,
    name TEXT,
    tagline TEXT,
    language TEXT NOT NULL
);

CREATE TABLE site_progress (
    site_slug TEXT PRIMARY KEY REFERENCES site(site_slug),
    last_member_offset INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE "user" (
    user_slug TEXT PRIMARY KEY,
    user_name TEXT NOT NULL,
    user_id INTEGER NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    real_name TEXT,
    gender TEXT,
    birthday DATE,
    location TEXT,
    website TEXT,
    bio TEXT,
    wikidot_pro BOOLEAN NOT NULL,
    karma SMALLINT CHECK (karma IS NULL OR (0 <= karma AND karma <= 5)),  -- Karma can be hidden if Pro
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
    created_by INTEGER NOT NULL REFERENCES "user"(user_id),
    updated_by INTEGER REFERENCES "user"(user_id),
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

CREATE TABLE forum_group (
    internal_id SERIAL PRIMARY KEY,
    site_slug TEXT NOT NULL REFERENCES site(site_slug),
    name TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE forum_category (
    forum_category_id INTEGER PRIMARY KEY,
    forum_group_internal_id INTEGER REFERENCES forum_group(internal_id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE forum_category_progress (
    forum_category_id INTEGER PRIMARY KEY REFERENCES forum_category(forum_category_id),
    thread_count INTEGER NOT NULL DEFAULT 0 CHECK (thread_count >= 0),
    post_count INTEGER NOT NULL DEFAULT 0 CHECK (post_count >= 0),
    last_thread_id INTEGER,
    last_post_id INTEGER
);

-- TODO create forum_thread, forum_post, and forum_post_revision tables

CREATE TABLE job (
    job_id SERIAL PRIMARY KEY,
    job_type TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    data JSONB NOT NULL,

    UNIQUE (job_type, data)
);

CREATE TABLE job_dead (
    job_id INTEGER PRIMARY KEY,
    buried_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    job_type TEXT NOT NULL,
    data JSON NOT NULL
);
