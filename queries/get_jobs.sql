-- :name get_job :many
-- Select jobs randomly to avoid bias or potential loops
SELECT * FROM job TABLESAMPLE SYSTEM (2);
