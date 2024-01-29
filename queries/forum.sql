-- :name add_forum_group :insert
INSERT INTO forum_group (site_slug, name, description, forum_category_ids)
    VALUES (:site_slug, :name, :description, :category_ids);

-- :name delete_forum_groups :affected
DELETE FROM forum_group
    WHERE site_slug = :site_slug;

-- :name add_forum_category :insert
INSERT INTO forum_category (forum_category_id, forum_group_internal_id, name, description)
    VALUES (:category_id, :group_id, :name, :description)
    ON CONFLICT (forum_category_id)
    DO UPDATE
    SET
        forum_group_internal_id = :group_id,
        name = :name,
        description = :description;
