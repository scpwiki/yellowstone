-- :name add_dead_job :insert
INSERT INTO job_dead (job_id, job_type, job_object, data)
    VALUES (:job_id, :job_type, :job_object, :data)
