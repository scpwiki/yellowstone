-- :name add_page :insert
-- Adds a page
INSERT INTO page (site_slug, page_slug, page_id, page_category_id)
    VALUES (:site_slug, :page_slug, :page_id, :page_category_id);

-- :name delete_page :affected
-- Marks a page as deleted
UPDATE page SET deleted_at = now()
    WHERE site_slug = :site_slug
    AND page_slug = :page_slug;
