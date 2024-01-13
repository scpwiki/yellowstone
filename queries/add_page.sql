-- :name add_page :insert
INSERT INTO page (site_slug, page_slug, page_id, page_category_id)
    VALUES (:site_slug, :page_slug, :page_id, :page_category_id)
