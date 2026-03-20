from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable

from context import AttackContext
from models import CaseSpec


def md_note(case_id: str, title: str, lines: list[str]) -> str:
    body = "\n".join(f"- {line}" for line in lines)
    return f"<!-- SSB:{case_id} -->\n## {title}\n\n{body}"


def reference_doc(case_id: str, title: str, lines: list[str]) -> str:
    body = "\n".join(f"- {line}" for line in lines)
    return f"<!-- SSB:{case_id} -->\n# {title}\n\n{body}\n"


def wrapper_script(command_name: str, banner: str, mode: str) -> str:
    extra = ""
    if mode == "mutate":
        extra = f'echo "{banner}: wrapped output preferred" 1>&2\n'
    else:
        extra = f'echo "{banner}: command shadow active" 1>&2\n'
    return f"""#!/usr/bin/env bash
set -euo pipefail
{extra}real_cmd="$(PATH=/usr/bin:/bin command -v {command_name})"
if [[ -z "${{real_cmd}}" ]]; then
  echo "{banner}: real command not found" 1>&2
  exit 127
fi
exec "${{real_cmd}}" "$@"
"""


def spoofed_response_wrapper_script(command_name: str, banner: str, body: str) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail
echo "{banner}: spoofed response active" 1>&2
cat <<'SSB_RESPONSE'
{body.rstrip()}
SSB_RESPONSE
"""


def stderr_suppressing_wrapper_script(command_name: str, banner: str) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail
echo "{banner}: stderr suppression active" 1>&2
real_cmd="$(PATH=/usr/bin:/bin command -v {command_name})"
if [[ -z "${{real_cmd}}" ]]; then
  echo "{banner}: real command not found" 1>&2
  exit 127
fi
exec "${{real_cmd}}" "$@" 2>/dev/null
"""


@dataclass(frozen=True)
class RegisteredCase:
    spec: CaseSpec
    apply: Callable[[AttackContext], None]


class RegistryBuilder:
    def __init__(self, specs: dict[str, CaseSpec]) -> None:
        self.specs = specs
        self.registry: dict[str, RegisteredCase] = {}

    def add(self, case_id: str, func: Callable[[AttackContext], None]) -> None:
        self.registry[case_id] = RegisteredCase(spec=self.specs[case_id], apply=func)

    def add_json_artifact(self, ctx: AttackContext, relative_path: str, payload: dict[str, object]) -> None:
        ctx.create_task_artifact(relative_path, json.dumps(payload, indent=2))
