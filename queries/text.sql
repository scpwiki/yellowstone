-- :name add_text :insert
-- Inserts a text entry, if not already present
INSERT INTO text (hash, contents)
    VALUES (:hash, :contents)
    ON CONFLICT (hash)
    DO NOTHING;
