#!/bin/bash
set -euo pipefail
mkdir -p /home/github/build/failed/rd3_ci
printf 'wrapper-used\n' >> /home/github/build/failed/rd3_ci/runtime_wrapper.log
exec "$@"
