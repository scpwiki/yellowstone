-- :name add_site_id :affected
UPDATE site SET id = :id WHERE slug = :slug
