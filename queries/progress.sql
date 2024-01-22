-- :name add_site_progress :insert
INSERT INTO site_progress (site_slug)
    VALUES (:site_slug)
    ON CONFLICT (site_slug)
    DO NOTHING;

-- :name get_last_member_offset :one
SELECT get_last_member_offset FROM site_progress
    WHERE site_slug = :site_slug;

-- :name update_last_member_offset :affected
UPDATE site_progress
    SET last_member_offset = MAX(last_member_offset, :last_offset)
    WHERE site_slug = :site_slug;
