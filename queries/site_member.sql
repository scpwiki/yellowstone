-- :name add_site_member :insert
INSERT INTO site_member (user_id, site_id, joined_at)
    VALUES (:user_id, :site_id, :joined_at)
    ON CONFLICT (user_id, site_id)
    DO NOTHING;
