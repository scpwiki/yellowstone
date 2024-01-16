-- Sets a user's avatar after uploading to S3
-- :name add_user_avatar :affected
UPDATE "user"
    SET avatar = :hash
    WHERE wikidot_id = :user_id;
