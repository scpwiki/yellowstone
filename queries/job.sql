-- Add new job to queue
-- :name add_job :insert
INSERT INTO job (job_type, job_object, data)
    VALUES (:job_type, :job_object, :data)
    ON CONFLICT (job_type, job_object)
    DO NOTHING;

-- Quick check if there are pending jobs
-- :name has_jobs :one
SELECT EXISTS (SELECT * FROM job LIMIT 1)

-- Get a random job from the queue to work on
-- This selects jobs randomly to avoid bias or generation loops
-- :name get_job :one
SELECT * FROM job ORDER BY random() LIMIT 1

-- Mark that a job has failed, and so its attempt count is incremented
-- :name fail_job :affected
UPDATE job
    SET attempts = attempts + 1
    WHERE job_id = :job_id

-- Delete job from queue, either because it's finished or failed
-- :name delete_job :affected
DELETE FROM job
    WHERE job_id = :job_id;

-- Add job to dead letter queue
-- :name add_dead_job :insert
INSERT INTO job_dead (job_id, job_type, job_object, data)
    VALUES (:job_id, :job_type, :job_object, :data);
