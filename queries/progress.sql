-- :name add_site_progress :insert
INSERT INTO site_progress (site_slug)
    VALUES (:site_slug)
    ON CONFLICT (site_slug)
    DO NOTHING;

-- :name get_last_member_offset :one
SELECT last_member_offset FROM site_progress
    WHERE site_slug = :site_slug;

-- :name update_last_member_offset :affected
UPDATE site_progress
    SET last_member_offset = GREATEST(last_member_offset, :last_offset)
    WHERE site_slug = :site_slug;

-- :name set_forum_category_progress :insert
INSERT INTO forum_category_progress (forum_category_id, thread_count, post_count, last_thread_id, last_post_id)
    VALUES (:category_id, :thread_count, :post_count, :last_thread_id, :last_post_id)
    ON CONFLICT (forum_category_id)
    DO UPDATE
    SET
        thread_count = :thread_count,
        post_count = :post_count,
        last_thread_id = GREATEST(forum_category_progress.last_thread_id, :last_thread_id),
        last_post_id = GREATEST(forum_category_progress.last_post_id, :last_post_id);

-- :name get_forum_category_progress :one
SELECT
    thread_count,
    post_count,
    last_thread_id,
    last_post_id
FROM forum_category_progress
    WHERE forum_category_id = :category_id;
