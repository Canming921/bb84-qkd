"""Automated tests: they double as physical sanity checks.

Each test asserts a property the quantum mechanics *must* satisfy, so a green
suite is evidence the simulation is physically correct, not just runnable.
"""
import numpy as np

from bb84.protocol import run_bb84
from bb84.qubit import measure, prepare


def test_matching_basis_is_deterministic():
    """Same-basis measurement returns Alice's bit with certainty."""
    rng = np.random.default_rng(0)
    q = prepare(1, "Z")
    assert all(measure(q, "Z", rng)[0] == 1 for _ in range(100))


def test_mismatched_basis_is_uniform():
    """|0> measured in the X basis is a fair coin:  |<+|0>|^2 = 1/2."""
    rng = np.random.default_rng(0)
    q = prepare(0, "Z")
    outcomes = [measure(q, "X", rng)[0] for _ in range(5000)]
    assert 0.46 < np.mean(outcomes) < 0.54


def test_measurement_collapses_state():
    """After measuring, the qubit is in the reported eigenstate."""
    rng = np.random.default_rng(1)
    out, collapsed = measure(prepare(0, "Z"), "X", rng)
    redo, _ = measure(collapsed, "X", rng)
    assert redo == out


def test_no_eve_zero_qber():
    """Clean channel: sifted keys are identical, QBER = 0."""
    res = run_bb84(n_bits=4000, eve_present=False, seed=1)
    assert res.qber == 0.0
    assert np.array_equal(res.sifted_alice, res.sifted_bob)


def test_sift_ratio_near_half():
    """Two random bases agree ~50% of the time."""
    res = run_bb84(n_bits=8000, eve_present=False, seed=2)
    assert 0.46 < res.sift_ratio < 0.54


def test_full_eve_qber_near_quarter():
    """Full intercept-resend attack -> QBER -> 1/4."""
    res = run_bb84(n_bits=8000, eve_present=True, p_eve=1.0, seed=3)
    assert 0.22 < res.qber < 0.28


def test_partial_eve_scales_linearly():
    """Half-strength attack -> QBER -> 1/8."""
    res = run_bb84(n_bits=20000, eve_present=True, p_eve=0.5, seed=4)
    assert 0.10 < res.qber < 0.15
