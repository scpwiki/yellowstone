-- :name add_site :insert
INSERT INTO site (site_slug, wikidot_id, home_slug, language)
    VALUES (:site_slug, :wikidot_id, :home_slug, :language)
