FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV WORKSPACE=/root

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root

COPY rd6_release_attestation_note.md /root/rd6_release_attestation_note.md
COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills
