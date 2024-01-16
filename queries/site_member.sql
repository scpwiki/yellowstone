-- Adds a site member relation, if not already present
-- This prefers earlier join dates to later ones, if multiple exist
-- :name add_site_member :insert
INSERT INTO site_member (user_id, site_id, joined_at)
    VALUES (:user_id, :site_id, :joined_at)
    ON CONFLICT (user_id, site_id)
    DO NOTHING;
