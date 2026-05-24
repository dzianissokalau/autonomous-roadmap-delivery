# Model Policy Gate Prompt Fragment

Before phase-owned edits, read the phase model policy, resolve the current
phase's required model and reasoning, and compare those values with configured
runner readback. If required and configured values differ or cannot be proven,
record the mismatch in state/log/review and stop before delivery unless the
operator has already approved the exact runner configuration repair.
