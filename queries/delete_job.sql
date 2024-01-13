-- :name delete_job :affected
DELETE FROM job
    WHERE job_id = :job_id
