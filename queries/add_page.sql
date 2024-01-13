-- :name add_page :insert
INSERT INTO page (site_slug, page_slug)
    VALUES (:site_slug, :page_slug)
