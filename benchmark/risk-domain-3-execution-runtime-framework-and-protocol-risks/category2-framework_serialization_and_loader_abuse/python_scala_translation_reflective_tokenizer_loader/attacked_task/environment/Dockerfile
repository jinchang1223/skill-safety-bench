FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

RUN printf 'Acquire::Retries "5";\nAcquire::http::Timeout "30";\nAcquire::https::Timeout "30";\n' > /etc/apt/apt.conf.d/99ssb-timeouts \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    openjdk-17-jdk-headless \
    gzip \
    python3 \
    python3-pip \
    tar \
    && rm -rf /var/lib/apt/lists/* /etc/apt/apt.conf.d/99ssb-timeouts

ENV SCALA_VERSION=2.13.12
ENV SBT_VERSION=1.12.0
ENV PATH="/opt/scala-${SCALA_VERSION}/bin:/opt/sbt/bin:$PATH"
RUN set -eux; \
    for artifact in scala sbt; do \
      if [ "$artifact" = "scala" ]; then \
        url="https://downloads.lightbend.com/scala/${SCALA_VERSION}/scala-${SCALA_VERSION}.tgz"; \
        out="/tmp/scala.tgz"; \
      else \
        url="https://github.com/sbt/sbt/releases/download/v${SBT_VERSION}/sbt-${SBT_VERSION}.tgz"; \
        out="/tmp/sbt.tgz"; \
      fi; \
      for attempt in 1 2 3; do \
        curl --connect-timeout 20 --retry 5 --retry-delay 2 --retry-all-errors \
          -fL "$url" -o "$out" && break; \
        sleep "$((attempt * 5))"; \
      done; \
    done; \
    tar -xzf /tmp/scala.tgz -C /opt; \
    tar -xzf /tmp/sbt.tgz -C /opt; \
    scala -version; \
    scalac -version; \
    sbt --script-version; \
    rm -f /tmp/scala.tgz /tmp/sbt.tgz

# Pin Python dependencies with explicit versions

RUN pip3 install --break-system-packages \
    typing-extensions==4.12.2

WORKDIR /root
COPY Tokenizer.py /root/
COPY rd3_tokenizer_extension_template.scala /root/
COPY scala_tokenizer/build.sbt /root/
COPY scala_tokenizer/src/test/scala/tokenizer/TokenizerSpec.scala /root/

# Copy skills to ALL agent paths
COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skills
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills
