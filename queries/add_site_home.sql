-- :name add_site_home :affected
UPDATE site SET home = :home WHERE slug = :slug
