-- :name get_site :one
SELECT * FROM site
    WHERE site_slug = :slug
