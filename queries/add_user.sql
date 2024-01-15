-- :name add_user :insert
INSERT INTO "user" (
    user_slug,
    user_name,
    wikidot_id,
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
    :wikidot_id,
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
