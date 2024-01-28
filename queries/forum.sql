-- :name add_forum_group :insert
INSERT INTO forum_group (site_slug, name, description)
    VALUES (:site_slug, :name, :description);

-- :name add_forum_category :insert
INSERT INTO forum_category (forum_category_id, forum_group_internal_id, name, description)
    VALUES (:category_id, :group_id, :name, :description);
