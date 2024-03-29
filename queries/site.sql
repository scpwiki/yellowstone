-- :name add_site :insert
INSERT INTO site (site_slug, site_id, home_slug, name, tagline, language)
    VALUES (:site_slug, :site_id, :home_slug, :name, :tagline, :language)
    ON CONFLICT (site_slug)
    DO UPDATE
        SET home_slug = :home_slug, name = :name, tagline = :tagline, language = :language;

-- :name get_site :one
SELECT * FROM site
    WHERE site_slug = :site_slug;
