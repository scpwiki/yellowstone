-- :name add_job :insert
-- Add new job to queue
INSERT INTO job (job_type, data)
    VALUES (:job_type, :data)
    ON CONFLICT (job_type, data)
    DO NOTHING;

-- :name has_jobs :one
-- Quick check if there are pending jobs
SELECT EXISTS (SELECT * FROM job LIMIT 1)

-- :name get_job :one
-- Get a random job from the queue to work on
-- This selects jobs randomly to avoid bias or generation loops
SELECT * FROM job ORDER BY random() LIMIT 1

-- :name fail_job :affected
-- Mark that a job has failed, and so its attempt count is incremented
UPDATE job
    SET attempts = attempts + 1
    WHERE job_id = :job_id

-- :name delete_job :affected
-- Delete job from queue, either because it's finished or failed
DELETE FROM job
    WHERE job_id = :job_id;

-- :name add_dead_job :insert
-- Add job to dead letter queue
INSERT INTO job_dead (job_id, job_type, data)
    VALUES (:job_id, :job_type, :data);
