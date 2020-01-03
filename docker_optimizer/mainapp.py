from typing import List, Optional
import json

import click
import dockerfile  # type: ignore


class DockerCommand:
    def __init__(self,
                 *,
                 original: str,
                 cmd: str,
                 flags: List[str],
                 value: List[str]) -> None:
        self.original = original
        self.cmd = cmd
        self.flags = list(flags)
        self.value = list(value)


def optimize_multiple_runs(commands: List[DockerCommand]) -> List[DockerCommand]:
    result: List[DockerCommand] = []

    last_command: Optional[DockerCommand] = None
    for command in commands:
        new_command = DockerCommand(
            original=command.original,
            cmd=command.cmd,
            flags=command.flags,
            value=command.value)

        if last_command and last_command.cmd == 'run' and command.cmd == 'run':
            if last_command.value[0] != '(':
                last_command.value.insert(0, '(')
                last_command.value.append(')')

            last_command.value.append("&&")
            last_command.value.append("(")
            last_command.value.extend(command.value)
            last_command.value.append(")")
            continue

        last_command = new_command
        result.append(new_command)

    return result


def optimize_env_variables(commands: List[DockerCommand]) -> List[DockerCommand]:
    result: List[DockerCommand] = []

    last_command = None
    for command in commands:
        new_command = DockerCommand(
            original=command.original,
            cmd=command.cmd,
            flags=command.flags,
            value=command.value)

        if last_command and last_command.cmd == 'env' and command.cmd == 'env':
            last_command.value.extend(command.value)
            continue

        last_command = new_command
        result.append(new_command)

    return result


@click.command()
@click.argument("dockerfile_in_name")
@click.argument("dockerfile_out_name")
def main(dockerfile_in_name: str, dockerfile_out_name: str) -> None:
    commands: List[DockerCommand] = dockerfile.parse_file(dockerfile_in_name)
    optimized_commands = optimize_docker_commands(commands)

    with open(dockerfile_out_name, 'w', encoding='utf-8') as f:
        write_docker_commands(f, optimized_commands)


def optimize_docker_commands(commands: List[DockerCommand]) -> List[DockerCommand]:
    """
    Optimizes the command list.
    :param commands:
    :return:
    """
    optimizations = [
        optimize_multiple_runs,
        optimize_env_variables,
    ]

    for optimization in optimizations:
        commands = optimization(commands)

    return commands


def write_docker_commands(output_stream, commands: List[DockerCommand]) -> None:
    """
    Write the commands to an output stream.
    :param output_stream:
    :param commands:
    :return:
    """
    output_stream.write(
        "# compiled by docker-optimizer\n"
        "# https://github.com/bmustiata/docker-optimizer\n")

    for command in commands:
        if command.cmd in {"entrypoint", "cmd"}:
            command_value = parse_array(command)
        elif command.cmd in {"env"}:
            command_value = parse_env(command)
        else:
            command_value = " ".join(command.value)

        command_flags = " ".join(command.flags)
        if command_flags:
            command_flags = f" {command_flags}"

        output_stream.write(f"{command.cmd}{command_flags} {command_value}\n")


def parse_env(command: DockerCommand) -> str:
    variables = []

    for i in range(0, len(command.value), 2):
        variables.append(f"{command.value[i]}={command.value[i + 1]}")

    return " ".join(variables)


def parse_array(command: DockerCommand) -> str:
    command_value_strings = [json.dumps(it) for it in command.value]
    command_value = f"[{', '.join(command_value_strings)}]"
    return command_value


if __name__ == '__main__':
    main()
