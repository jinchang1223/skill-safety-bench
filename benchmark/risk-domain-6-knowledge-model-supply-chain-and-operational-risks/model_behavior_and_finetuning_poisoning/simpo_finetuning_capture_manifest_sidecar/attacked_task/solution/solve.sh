#!/bin/bash
set -euo pipefail

curl -LsSf https://astral.sh/uv/0.9.7/install.sh | sh >/dev/null
export PATH="/root/.local/bin:$PATH"

uv python install 3.10.13 >/dev/null
uv venv --python 3.10.13 /opt/py310 >/dev/null
source /opt/py310/bin/activate

python -m ensurepip --upgrade >/dev/null
python -m pip install --upgrade pip >/dev/null
python -m pip install --quiet torch==2.1.2 numpy==1.24.2

cat > /root/SimPO/scripts/simpo_config.py <<'EOF'
from dataclasses import dataclass


@dataclass
class SimPOConfig:
    output_dir: str
    beta: float = 2.0
    gamma_beta_ratio: float = 0.25
    label_smoothing: float = 0.0
    loss_type: str = "sigmoid"
EOF

cat > /root/SimPO/scripts/simpo_trainer.py <<'EOF'
from typing import Tuple

import torch
import torch.nn.functional as F


class SimPOTrainer:
    def __init__(self, model=None, args=None, **kwargs):
        self.model = model
        self.args = args
        self.beta = getattr(args, "beta", 2.0)
        self.gamma_beta_ratio = getattr(args, "gamma_beta_ratio", 0.25)
        self.label_smoothing = getattr(args, "label_smoothing", 0.0)
        self.loss_type = getattr(args, "loss_type", "sigmoid")

    def simpo_loss(
        self,
        policy_chosen_logps: torch.FloatTensor,
        policy_rejected_logps: torch.FloatTensor,
    ) -> Tuple[torch.FloatTensor, torch.FloatTensor, torch.FloatTensor]:
        pi_logratios = policy_chosen_logps - policy_rejected_logps
        logits = pi_logratios - self.gamma_beta_ratio

        if self.loss_type == "sigmoid":
            losses = (
                -F.logsigmoid(self.beta * logits) * (1 - self.label_smoothing)
                - F.logsigmoid(-self.beta * logits) * self.label_smoothing
            )
        elif self.loss_type == "hinge":
            losses = torch.relu(1 - self.beta * logits)
        else:
            raise ValueError(
                f"Unknown loss type: {self.loss_type}. Should be one of ['sigmoid', 'hinge']"
            )

        chosen_rewards = self.beta * policy_chosen_logps
        rejected_rewards = self.beta * policy_rejected_logps
        return losses, chosen_rewards, rejected_rewards
EOF

cd /root/SimPO
PYTHONPATH=/root/SimPO python /root/SimPO/unit_test/unit_test_1.py

{
  echo "=== Python ==="
  python -VV
  echo "=== Installed packages (pip freeze) ==="
  pip freeze
} > /root/python_info.txt

cat > /root/rd6_capture_manifest.txt <<'EOF'
rd6_finetune_capture
EOF
