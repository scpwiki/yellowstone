-- :name add_user_avatar :affected
-- Sets a user's avatar after uploading to S3
UPDATE "user"
    SET avatar = :hash
    WHERE wikidot_id = :user_id;
