-- :name has_jobs :one
-- Quick check if a job table is empty
SELECT EXISTS (SELECT * FROM job LIMIT 1)
