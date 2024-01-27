-- :name add_job :insert
INSERT INTO job (job_type, data)
    VALUES (:job_type, :data)
    ON CONFLICT (job_type, data)
    DO NOTHING;

-- :name has_jobs :one
SELECT EXISTS (SELECT * FROM job LIMIT 1);

-- :name get_job :one
SELECT * FROM job ORDER BY random() LIMIT 1;

-- :name fail_job :affected
UPDATE job
    SET attempts = attempts + 1
    WHERE job_id = :job_id;

-- :name delete_job :affected
DELETE FROM job
    WHERE job_id = :job_id;

-- :name add_dead_job :insert
INSERT INTO job_dead (job_id, job_type, data)
    VALUES (:job_id, :job_type, :data);
