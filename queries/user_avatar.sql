-- :name add_user_avatar :affected
UPDATE "user"
    SET avatar = :hash
    WHERE user_id = :user_id;
