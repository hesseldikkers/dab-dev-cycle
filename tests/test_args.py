import pytest

from orders.args import parse_args


def test_parse_args_reads_named_parameters():
    args = parse_args(["--catalog=workspace", "--schema=orders_dev"])

    assert (args.catalog, args.schema) == ("workspace", "orders_dev")


def test_parse_args_requires_schema():
    with pytest.raises(SystemExit):
        parse_args(["--catalog=workspace"])
