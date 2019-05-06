import random
import subprocess

import config


class Comcast:
    BANDWIDTH_LOWER_BOUND = 0.2     # 0.2 Mbps
    BANDWIDTH_UPPER_NOUND = 10      # 10 Mbps
    LATENCY_LOWER_BOUND = 30        # 30 ms
    LATENCY_UPPER_BOUND = 1000      # 1000 ms
    LOSS_LOWER_BOUND = 0.1          # 0.1%
    LOSS_UPPER_BOUND = 10           # 10%
    CORRUPT_LOWER_BOUND = 0.1       # 0.1%
    CORRUPT_UPPER_BOUND = 2         # 2%
    REORDERING_LOWER_BOUND = 0.1    # 0.1%
    REORDERING_UPPER_BOUND = 10     # 10%

    def __init__(self):
        self._rng = random.Random()
        self.bandwidth = None
        self.latency = None
        self.loss_rate = None
        self.corrupt_rate = None
        self.reordering_rate = None

    def coin_toss(self, true_prob = 0.5):
        if self._rng.uniform(0, 1) <= true_prob:
            return True
        else:
            return False

    def beta_random_range(self,alpha, beta, lower, upper):
        return self._rng.betavariate(alpha=alpha, beta=beta) * (upper - lower) + lower

    def generate_random_network_condition(self):
        # random generate bandwidth in 0.2 - 10 Mbps
        if self.coin_toss():
            self.bandwidth = self._rng.uniform(self.BANDWIDTH_LOWER_BOUND, self.BANDWIDTH_UPPER_NOUND)
        else:
            self.bandwidth = None

        # random generate latency in 30 - 1000 ms
        if self.coin_toss():
            self.latency = self.beta_random_range(alpha=1, beta=3,
                                                  lower=self.LATENCY_LOWER_BOUND, upper=self.LATENCY_UPPER_BOUND)
            self.latency = int(self.latency)
        else:
            self.latency = None

        # random generate packet loss
        if self.coin_toss(true_prob=0.3):
            self.loss_rate = self.beta_random_range(alpha=0.7, beta=3,
                                                    lower=self.LOSS_LOWER_BOUND, upper=self.LOSS_UPPER_BOUND)
        else:
            self.loss_rate = None

        # random generate corrupt rate
        if self.coin_toss(true_prob=0.1):
            self.corrupt_rate = self.beta_random_range(alpha=0.7, beta=3,
                                                       lower=self.CORRUPT_LOWER_BOUND, upper=self.CORRUPT_UPPER_BOUND)
        else:
            self.corrupt_rate = None

        # random generate reordering rate
        if self.coin_toss(true_prob=0.1):
            self.reordering_rate = self.beta_random_range(alpha=0.7, beta=3,
                                                          lower=self.REORDERING_LOWER_BOUND,
                                                          upper=self.REORDERING_UPPER_BOUND)
        else:
            self.reordering_rate = None

    def apply(self, dry_run: bool=False):
        cmd = ["tcset", config.NIC]

        if self.bandwidth is not None:
            cmd.extend(["--rate", f"{self.bandwidth:.1f}Mbps"])

        if self.latency is not None:
            cmd.extend(["--delay", f"{self.latency}ms"])

        if self.loss_rate is not None:
            cmd.extend(["--loss", f"{self.loss_rate:.1f}%"])

        if self.corrupt_rate is not None:
            cmd.extend(["--corrupt", f"{self.corrupt_rate:.1f}%"])

        if self.reordering_rate is not None:
            cmd.extend(["--reordering", f"{self.reordering_rate:.1f}%"])

        cmd.extend(["--direction", "incoming"])

        if dry_run:
            print(cmd)
        else:
            if len(cmd) > 4:
                subprocess.check_call(cmd)

        return cmd

    def reset(self):
        cmd = ["tcdel", config.NIC, "--all"]
        subprocess.call(cmd)


if __name__ == "__main__":
    comcast = Comcast()
    comcast.generate_random_network_condition()
    comcast.apply(dry_run=True)
