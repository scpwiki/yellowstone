-- :name add_text :insert
INSERT INTO text (hash, contents) VALUES (:hash, :contents) ON CONFLICT DO NOTHING;
