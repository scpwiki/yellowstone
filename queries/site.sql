-- Adds or updates a site
-- :name add_site :insert
INSERT INTO site (site_slug, wikidot_id, home_slug, name, tagline, language)
    VALUES (:site_slug, :site_id, :home_slug, :name, :tagline, :language)
    ON CONFLICT (site_slug)
    DO UPDATE
        SET home_slug = :home_slug, name = :name, tagline = :tagline, language = :language;

-- Gets site by slug
-- :name get_site :one
SELECT * FROM site
    WHERE site_slug = :slug;
