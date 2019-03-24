# built-in
import subprocess
import sys
from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

# project
import attr

# app
from .converters import PIPConverter
from .models import Requirement


logger = getLogger('dephell')


@attr.s()
class PackageManager:
    executable = attr.ib(type=Path)

    def install(self, reqs: List[Requirement]) -> int:
        converter = PIPConverter(lock=True)
        with TemporaryDirectory() as path:
            path = Path(path) / 'requiements.txt'
            if path.exists():
                path.unlink()
            converter.dump(reqs=reqs, path=path, project=None)
            return self.run('install', '--no-deps', '-r', str(path))

    def run(self, *args) -> int:
        command_pip = [str(self.executable), '-m', 'pip'] + list(args)
        command_grep = [sys.executable, '-m', 'dephell.pip_cleaner']
        process_pip = subprocess.Popen(command_pip, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process_grep = subprocess.Popen(command_grep, stdin=process_pip.stdout, stdout=sys.stdout)
        with process_pip, process_grep:
            process_pip.wait()
            process_grep.wait()

            stderr = process_pip.stderr.read().decode()
            if process_pip.returncode != 0:
                logger.error(stderr)
            else:
                logger.debug(stderr)
            return process_pip.returncode
