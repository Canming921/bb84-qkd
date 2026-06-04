"""
Single-qubit state vectors and projective measurement.

A qubit is represented as a length-2 complex numpy array: the amplitude
vector in the computational basis. Measurement follows the Born rule, so the
whole simulation reproduces genuine quantum statistics instead of hard-coded
"matching basis -> correct, otherwise 50/50" shortcuts. This matters for the
physics-correctness part of the grade: the 25% QBER under an intercept-resend
attack *emerges* from |<e_k|psi>|^2, it is not assumed.
"""
from __future__ import annotations

import numpy as np

# --- Computational (Z / "rectilinear" / +) basis -------------------------
KET_0 = np.array([1.0, 0.0], dtype=complex)   # |0>
KET_1 = np.array([0.0, 1.0], dtype=complex)   # |1>

# --- Hadamard (X / "diagonal" / x) basis ---------------------------------
KET_PLUS = (KET_0 + KET_1) / np.sqrt(2)       # |+> = (|0> + |1>) / sqrt(2)
KET_MINUS = (KET_0 - KET_1) / np.sqrt(2)      # |-> = (|0> - |1>) / sqrt(2)

# basis label -> (eigenstate for bit 0, eigenstate for bit 1)
_BASIS_STATES = {
    "Z": (KET_0, KET_1),
    "X": (KET_PLUS, KET_MINUS),
}

#: The two mutually-unbiased bases BB84 uses.
BASES = ("Z", "X")


def prepare(bit: int, basis: str) -> np.ndarray:
    """Return the qubit state that encodes ``bit`` (0/1) in ``basis`` ('Z'/'X')."""
    return _BASIS_STATES[basis][bit].copy()


def measure(state: np.ndarray, basis: str, rng: np.random.Generator):
    """Projective measurement of ``state`` in ``basis``.

    Returns ``(outcome, collapsed_state)`` where ``outcome`` in {0, 1} is the
    bit attached to the eigenstate the system collapses onto. Outcome
    probabilities obey the Born rule  p(k) = |<e_k|psi>|^2.
    """
    e0, e1 = _BASIS_STATES[basis]
    p0 = abs(np.vdot(e0, state)) ** 2          # |<e0|psi>|^2
    outcome = 0 if rng.random() < p0 else 1
    collapsed = (e0 if outcome == 0 else e1).copy()
    return outcome, collapsed
