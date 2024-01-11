-- :name add_site :affected
UPDATE site SET id = :id WHERE slug = :slug
