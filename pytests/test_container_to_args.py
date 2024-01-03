from unittest import mock
from podman_compose import container_to_args


def create_compose_mock():
    compose = mock.Mock()
    compose.project_name = "test_project_name"
    compose.dirname = "test_dirname"
    compose.container_names_by_service.get = mock.Mock(return_value=None)
    compose.prefer_volume_over_mount = False
    compose.default_net = None
    compose.networks = {}
    return compose


def get_minimal_container():
    return {
        "name": "project_name_service_name1",
        "service_name": "service_name",
        "image": "busybox",
    }


def test_container_to_args_minimal() -> None:
    c = create_compose_mock()

    cnt = get_minimal_container()

    args = container_to_args(c, cnt)
    assert args == [
        "--name=project_name_service_name1",
        "-d",
        "--net",
        "",
        "--network-alias",
        "service_name",
        "busybox",
    ]


def test_container_to_args_runtime() -> None:
    c = create_compose_mock()

    cnt = get_minimal_container()
    cnt["runtime"] = "runsc"

    args = container_to_args(c, cnt)
    assert args == [
        "--name=project_name_service_name1",
        "-d",
        "--net",
        "",
        "--network-alias",
        "service_name",
        "--runtime",
        "runsc",
        "busybox",
    ]
