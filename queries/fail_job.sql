-- :name fail_job :affected
UPDATE job
    SET attempts = attempts + 1
    WHERE job_id = :job_id
