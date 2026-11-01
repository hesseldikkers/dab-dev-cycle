from databricks.bundles.core import Bundle, job_mutator
from databricks.bundles.jobs import Job


@job_mutator
def require_owner(bundle: Bundle, job: Job) -> Job:
    if "owner" not in job.tags:
        raise ValueError(
            f'Job "{job.name}" has no "owner" tag. '
            'Add the tag "owner" to the job in its resource file.'
        )
    return job
