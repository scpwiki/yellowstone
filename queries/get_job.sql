-- :name get_job :one
-- Select jobs randomly to avoid bias or potential loops
SELECT * FROM job ORDER BY random() LIMIT 1
