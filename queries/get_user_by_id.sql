-- :name get_user_by_id :one
SELECT * FROM "user"
    WHERE wikidot_id = :user_id
