-- :name add_user :insert
INSERT INTO "user" (
    user_slug,
    user_name,
    user_id,
    created_at,
    real_name,
    gender,
    birthday,
    location,
    website,
    bio,
    wikidot_pro,
    karma
) VALUES (
    :user_slug,
    :user_name,
    :user_id,
    :created_at,
    :real_name,
    :gender,
    :birthday,
    :location,
    :website,
    :bio,
    :wikidot_pro,
    :karma
)
    ON CONFLICT (user_id)
    DO UPDATE
        SET user_slug = :user_slug,
            user_name = :user_name,
            real_name = :real_name,
            gender = :gender,
            birthday = :birthday,
            location = :location,
            website = :website,
            bio = :bio,
            wikidot_pro = :wikidot_pro,
            karma = :karma;


-- :name get_user_by_id :one
SELECT * FROM "user"
    WHERE user_id = :user_id;

-- :name get_user_by_slug :one
SELECT * FROM "user"
    WHERE user_slug = :user_slug;
