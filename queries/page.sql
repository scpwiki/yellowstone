-- Adds a page
-- :name add_page :insert
INSERT INTO page (site_slug, page_slug, page_id, page_category_id)
    VALUES (:site_slug, :page_slug, :page_id, :page_category_id);

-- Marks a page as deleted
-- :name delete_page :affected
UPDATE page SET deleted_at = now()
    WHERE site_slug = :site_slug
    AND page_slug = :page_slug;
