-- :name add_job :insert
INSERT INTO job (job_type, job_object, data)
    VALUES (:job_type, :job_object, :data)
    ON CONFLICT (job_type, job_object)
    DO NOTHING
