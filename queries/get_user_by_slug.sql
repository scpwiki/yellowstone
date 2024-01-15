-- :name get_user_by_slug :one
SELECT * FROM "user"
    WHERE user_slug = :user_slug
