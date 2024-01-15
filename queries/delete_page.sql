-- :name delete_page :affected
UPDATE page SET deleted_at = now()
    WHERE site_slug = :site_slug
    AND page_slug = :page_slug
