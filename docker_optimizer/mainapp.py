from typing import List

import dockerfile
import click


class DockerCommand:
    def __init__(self,
                 *,
                 cmd: str,
                 value: List[str]) -> None:
        self.cmd = cmd
        self.value = list(value)


def optimize_multiple_runs(commands: List[DockerCommand]) -> List[DockerCommand]:
    result: List[DockerCommand] = []

    last_command = None
    for command in commands:
        new_command = DockerCommand(cmd=command.cmd, value=command.value)

        if last_command and last_command.cmd == 'run' and command.cmd == 'run':
            last_command.value.append("&&")
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

    optimizations = [
        optimize_multiple_runs
    ]

    for optimization in optimizations:
        commands = optimization(commands)

    for command in commands:
        print(f"{command.cmd} {' '.join(command.value)}")


if __name__ == '__main__':
    main()
