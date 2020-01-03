import io
import textwrap
import unittest
from typing import List

import dockerfile  # type: ignore

from docker_optimizer.mainapp import DockerCommand, optimize_docker_commands, write_docker_commands


class TestDockerOptimizer(unittest.TestCase):
    def test_FROM_command(self):
        self._parse_content("FROM ubuntu:18.04", "from ubuntu:18.04")

    def test_COPY_command(self):
        self._parse_content("COPY --chown=100:100 /tmp /tmp", "copy --chown=100:100 /tmp /tmp")

    def test_ENTRYPOINT_command(self):
        self._parse_content('ENTRYPOINT ["/a", "b"]', 'entrypoint ["/a", "b"]')

    def test_RUN_command_collapse(self):
        self._parse_content('RUN this\nRUN that', 'run ( this ) && ( that )')

    def test_RUN_command_with_or_collapses_correctly(self):
        self._parse_content('RUN this\nRUN that || something-else', 'run ( this ) && ( that || something-else )')

    def test_ENV_command(self):
        self._parse_content('ENV AA "A B"', 'env AA="A B"')

    def test_ENV_equals(self):
        self._parse_content("ENV LE_AUTO_SUDO=", "env LE_AUTO_SUDO=")

    def test_ENV_equals_value(self):
        self._parse_content("ENV LE_AUTO_SUDO=sudo", "env LE_AUTO_SUDO=sudo")

    def test_ENV_equals_multiple_values(self):
        self._parse_content('ENV A="a b" B= C=c', 'env A="a b" B= C=c')

    def test_ENV_multiple_values_collapse(self):
        self._parse_content('ENV A="a b"\nENV B=\nENV C c', 'env A="a b" B= C=c')

    def _parse_content(
            self,
            input: str,
            expected: str) -> None:
        input_text = textwrap.dedent(input)
        expected_text = textwrap.dedent(expected)

        expected_text = f"# compiled by docker-optimizer\n" \
                        f"# https://github.com/bmustiata/docker-optimizer\n" \
                        f"{expected_text}"

        commands: List[DockerCommand] = dockerfile.parse_string(input_text)
        optimized_commands = optimize_docker_commands(commands)

        with io.StringIO() as output:
            write_docker_commands(output, optimized_commands)
            self.assertEqual(output.getvalue().strip(), expected_text.strip())
