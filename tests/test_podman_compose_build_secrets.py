"""Test how secrets in files are passed to podman.
"""
import os
import subprocess
import pytest


@pytest.fixture(name="compose_yaml_path")
def fixture_compose_yaml_path(test_path):
    """ "Returns the path to the compose file used for this test module"""
    return os.path.join(test_path, "build_secrets")


def test_run_secret(podman_compose_path, compose_yaml_path):
    """podman run should receive file secrets as --volume

    See build_secrets/docker-compose.yaml for secret names and mount points (aka targets)

    """
    # This command *will* eventually fail with an AttributeError exception (maybe a bug related to
    # "--dry-run"?), but it prints the arguments that would be passed to podman, which is sufficient
    # for this test
    cmd = (
        podman_compose_path,
        "--dry-run",
        "-f",
        os.path.join(compose_yaml_path, "docker-compose.yaml"),
        "run",
        "test",
    )
    p = subprocess.run(
        cmd, stdout=subprocess.PIPE, check=False, stderr=subprocess.STDOUT, text=True
    )
    secret_path = os.path.join(compose_yaml_path, "my_secret")
    assert (
        f"--volume {secret_path}:/run/secrets/run_secret:ro,rprivate,rbind" in p.stdout
    )
    assert f"--volume {secret_path}:/tmp/run_secret2:ro,rprivate,rbind" in p.stdout


def test_build_secret(podman_compose_path, compose_yaml_path):
    """podman build should receive secrets as --secret, so that they can be used inside the
    Dockerfile in "RUN --mount=type=secret ..." commands.

    """
    cmd = (
        podman_compose_path,
        "--dry-run",
        "-f",
        os.path.join(compose_yaml_path, "docker-compose.yaml"),
        "build",
    )
    p = subprocess.run(
        cmd, stdout=subprocess.PIPE, check=False, stderr=subprocess.STDOUT, text=True
    )
    secret_path = os.path.join(compose_yaml_path, "my_secret")
    assert f"--secret id=build_secret,src={secret_path}" in p.stdout
    assert f"--secret id=build_secret2,src={secret_path}" in p.stdout


def test_invalid_build_secret(podman_compose_path, compose_yaml_path):
    """build secrets in docker-compose file can only have a target argument without directory
    component

    """
    cmd = (
        podman_compose_path,
        "--dry-run",
        "-f",
        os.path.join(compose_yaml_path, "docker-compose.yaml.invalid"),
        "build",
    )
    p = subprocess.run(
        cmd, stdout=subprocess.PIPE, check=False, stderr=subprocess.STDOUT, text=True
    )
    assert (
        'ValueError: ERROR: Build secret "build_secret" has invalid target "/build_secret"'
        in p.stdout
    )
