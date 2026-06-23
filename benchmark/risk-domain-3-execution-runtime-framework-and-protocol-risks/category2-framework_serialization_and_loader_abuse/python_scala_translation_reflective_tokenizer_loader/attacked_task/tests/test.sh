#!/usr/bin/env bash
set -euo pipefail

mkdir -p /logs/verifier
project_dir=/tmp/tokenizer-eval
mkdir -p "${project_dir}/project"
printf 'sbt.version=1.12.0\n' > "${project_dir}/project/build.properties"

set +e
python3 /tests/test_outputs.py \
  /root/Tokenizer.scala \
  /root/build.sbt \
  /root/TokenizerSpec.scala \
  --project-dir "${project_dir}" \
  --json \
  2>&1 | tee /logs/verifier/test_output.log
status=${PIPESTATUS[0]}
set -e

if [ "${status}" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

exit 0
