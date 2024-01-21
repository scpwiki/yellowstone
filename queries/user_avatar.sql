-- :name add_user_avatar :affected
UPDATE "user"
    SET avatar = :hash
    WHERE wikidot_id = :user_id;
