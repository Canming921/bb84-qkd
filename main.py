"""Command-line demonstration of the BB84 protocol.

Examples
--------
    python main.py                      # clean channel, no eavesdropper
    python main.py --eve                # full intercept-resend attack
    python main.py --eve --p-eve 0.5    # Eve attacks half the qubits
    python main.py --sweep              # QBER vs interception probability plot
"""
from __future__ import annotations

import argparse

import numpy as np

from bb84.protocol import run_bb84


def print_trace(res, k: int = 24) -> None:
    """Show the per-qubit basis-comparison process for the first k positions."""
    k = min(k, res.n_bits)
    print(f"\n--- First {k} transmitted qubits (basis reconciliation) ---")
    print("idx | A-bit A-basis | B-basis B-result | sifted | error")
    print("----+---------------+------------------+--------+------")
    for i in range(k):
        sifted = bool(res.sift_mask[i])
        err = sifted and (res.alice_bits[i] != res.bob_results[i])
        print(
            f"{i:>3} |   {res.alice_bits[i]}      {res.alice_bases[i]}    "
            f"|    {res.bob_bases[i]}       {res.bob_results[i]}      "
            f"|  {'kept' if sifted else ' -- '}  |  {'X' if err else ''}"
        )


def summarize(res) -> None:
    print("\n=============== SUMMARY ===============")
    print(f"Qubits transmitted   : {res.n_bits}")
    print(f"Sifted key length    : {res.n_sifted}  ({res.sift_ratio:.1%} retained)")
    print(f"Eavesdropper present : {res.eve_present}"
          + (f"  (intercepts {res.p_eve:.0%})" if res.eve_present else ""))
    print(f"Measured QBER        : {res.qber:.4f}  ({res.qber:.2%})")
    print(f"Theoretical QBER     : {res.theoretical_qber:.4f}  "
          f"({res.theoretical_qber:.2%})")
    if not res.eve_present:
        print("Channel looks clean -> key is safe to use after error correction.")
    elif res.qber > 0.11:
        print("QBER exceeds the ~11% security threshold -> eavesdropper detected, "
              "abort and discard the key.")
    print("======================================")


def sweep(n_bits: int = 20000, seed: int = 0, outfile: str = "qber_sweep.png") -> None:
    """Plot measured vs theoretical QBER across interception probabilities."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; run `pip install matplotlib` for --sweep.")
        return
    ps = np.linspace(0.0, 1.0, 11)
    measured = [run_bb84(n_bits, eve_present=True, p_eve=p, seed=seed).qber for p in ps]
    plt.figure(figsize=(7, 4.5))
    plt.plot(ps, measured, "o-", label="Simulated QBER")
    plt.plot(ps, ps / 4, "--", label="Theory: QBER = p_eve / 4")
    plt.axhline(0.11, color="red", ls=":", label="~11% security threshold")
    plt.xlabel("Eve interception probability  $p_{eve}$")
    plt.ylabel("Quantum bit error rate (QBER)")
    plt.title("Intercept-resend attack: QBER vs eavesdropping intensity")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(outfile, dpi=150)
    print(f"Saved {outfile}")


def main() -> None:
    parser = argparse.ArgumentParser(description="BB84 QKD simulation")
    parser.add_argument("-n", "--n-bits", type=int, default=2048)
    parser.add_argument("--eve", action="store_true", help="enable the eavesdropper")
    parser.add_argument("--p-eve", type=float, default=1.0,
                        help="fraction of qubits Eve intercepts")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--sweep", action="store_true",
                        help="produce the QBER-vs-p_eve figure and exit")
    args = parser.parse_args()

    if args.sweep:
        sweep(seed=args.seed or 0)
        return

    res = run_bb84(args.n_bits, eve_present=args.eve, p_eve=args.p_eve, seed=args.seed)
    print_trace(res)
    summarize(res)


if __name__ == "__main__":
    main()
