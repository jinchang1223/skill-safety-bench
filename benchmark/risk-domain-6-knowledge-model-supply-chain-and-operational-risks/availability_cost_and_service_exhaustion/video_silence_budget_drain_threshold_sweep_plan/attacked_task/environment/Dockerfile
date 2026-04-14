FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    numpy==1.24.3 \
    scipy==1.11.1 \
    pytest==7.4.0

# Set working directory
WORKDIR /root
COPY rd6_threshold_sweep_note.md /root/rd6_threshold_sweep_note.md
COPY rd6_threshold_sweep_policy.json /root/rd6_threshold_sweep_policy.json

# Copy data files (including input video)
COPY data /root/data

# Copy skills to all agent-specific locations
# Claude Code
COPY skills /root/.claude/skills
# Codex
COPY skills /root/.codex/skills
# OpenCode
COPY skills /root/.opencode/skill
# Goose
COPY skills /root/.goose/skills
# Factory
COPY skills /root/.factory/skills
# Portable agents format (Goose, Amp)
COPY skills /root/.agents/skills
