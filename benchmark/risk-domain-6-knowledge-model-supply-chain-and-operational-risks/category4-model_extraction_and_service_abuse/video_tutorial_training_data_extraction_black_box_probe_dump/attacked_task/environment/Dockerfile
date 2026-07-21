FROM python:3.11-slim-bookworm

WORKDIR /root

# Copy video and metadata
COPY tutorial_video.mp4 /root/
COPY VIDEO_INFO.md /root/
COPY ground_truth.json /root/ground_truth.json
COPY rd6_probe_recipe.txt /root/rd6_probe_recipe.txt

# Copy the task skill to the runtime locations used by supported agents.
COPY skills /app/skills
COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skills
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills
