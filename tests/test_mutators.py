import pytest
from databricks.bundles.core import Bundle
from databricks.bundles.jobs import Job

from mutators import require_owner

BUNDLE = Bundle(target="dev")


def test_require_owner_passes_job_with_owner():
    job = Job(name="orders_gold", tags={"owner": "orders-team"})

    assert require_owner.function(BUNDLE, job) == job


def test_require_owner_rejects_job_without_owner():
    job = Job(name="orders_gold", tags={"layer": "gold"})

    with pytest.raises(ValueError, match='"orders_gold" has no "owner"'):
        require_owner.function(BUNDLE, job)
