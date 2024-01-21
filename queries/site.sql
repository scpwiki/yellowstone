-- :name add_site :insert
-- Adds or updates a site
INSERT INTO site (site_slug, wikidot_id, home_slug, name, tagline, language)
    VALUES (:site_slug, :site_id, :home_slug, :name, :tagline, :language)
    ON CONFLICT (site_slug)
    DO UPDATE
        SET home_slug = :home_slug, name = :name, tagline = :tagline, language = :language;

-- :name get_site :one
-- Gets site by slug
SELECT * FROM site
    WHERE site_slug = :site_slug;
