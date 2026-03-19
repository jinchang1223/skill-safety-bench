python3 cli.py materialize --config configs/citation-check-attack.yaml

harbor run -p tmp-tasks/citation-check-attacked -a codex -m openai/gpt-5.2-codex --artifact /root/answer.json