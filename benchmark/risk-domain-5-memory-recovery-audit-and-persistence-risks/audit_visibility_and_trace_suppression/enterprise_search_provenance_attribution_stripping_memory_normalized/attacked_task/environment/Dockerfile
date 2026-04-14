FROM ubuntu:24.04

# Install or copy over any environment dependencies here.


RUN apt-get update && apt-get install -y python3 python3-pip


WORKDIR /root
ENV PYTHONPATH="/root${PYTHONPATH:+:$PYTHONPATH}"

# Copy data files
COPY DATA /root/DATA

COPY question.txt /root/question.txt
COPY rd5_sitecustomize.py /root/sitecustomize.py
COPY review_attribution_trace.json /root/review_attribution_trace.json
COPY review_attribution_manifest.json /root/review_attribution_manifest.json

# Copy skills to agent-specific locations
COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skills
COPY skills /root/.goose/skills
COPY skills /root/.agents/skills
# Gemini
COPY skills /root/.gemini/skills
COPY skills /root/.factory/skills
