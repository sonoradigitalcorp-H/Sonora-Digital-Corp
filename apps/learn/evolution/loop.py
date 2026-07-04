"""Evolution Loop — orquestador del ciclo completo [FR3-FR4]"""
import json
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from .store import EvolutionStore
from .proposer import EvolutionProposer
from .simulator import EvolutionSimulator

REPO = Path(__file__).resolve().parent.parent.parent.parent
EMIT_SCRIPT = REPO / "scripts" / "emit-event.py"
log = logging.getLogger("evolution")


class EvolutionLoop:
    def __init__(self):
        self.store = EvolutionStore()
        self.proposer = EvolutionProposer()
        self.simulator = EvolutionSimulator()

    def run_once(self, dry_run: bool = False) -> dict:
        log.info("Evolution Loop: starting cycle")
        self._emit("evolution.started", {})

        # 1. Measure
        current_score = self.simulator._compute_current_score()
        log.info(f"  Current score: {current_score['score']}")
        self._emit("evolution.measured", {"score": current_score})

        # 2. Propose
        proposals = self.proposer.analyze()
        log.info(f"  Generated {len(proposals)} proposals")

        accepted = []
        for proposal in proposals:
            pid = self.store.save_proposal(proposal)
            proposal["id"] = pid
            self._emit("evolution.improvement_proposed", {"proposal_id": pid, "title": proposal["title"]})

            # 3. Simulate
            simulation = self.simulator.simulate(proposal)
            self._emit("evolution.simulated", {
                "proposal_id": pid,
                "current_score": simulation["current_score"]["score"],
                "proposed_score": simulation["proposed_score"],
            })

            # 4. Approve
            if simulation["recommendation"] == "approve" and not dry_run:
                self.store.update_status(pid, "approved", f"Score improvement: +{simulation['delta']}")
                self.store.save_decision(pid, "approved", reason=simulation.get("recommendation"))
                log.info(f"  Approved: {proposal['title']} (+{simulation['delta']} score)")
                accepted.append(proposal)

                # 5. Implement (register the improvement)
                self._implement_proposal(proposal)
                self._emit("evolution.implemented", {"proposal_id": pid, "title": proposal["title"]})
            elif simulation["recommendation"] == "approve" and dry_run:
                self.store.update_status(pid, "simulated_approved", f"[DRY RUN] Would approve. Impact: +{simulation['delta']}")
                log.info(f"  [DRY RUN] Would approve: {proposal['title']} (+{simulation['delta']} score)")
            else:
                self.store.update_status(pid, "rejected", f"Simulation: {simulation['recommendation']} (delta: {simulation['delta']})")
                log.info(f"  Rejected: {proposal['title']} (delta: {simulation['delta']}, rec: {simulation['recommendation']})")

        # 6. Record
        result = {
            "cycle": datetime.now(timezone.utc).isoformat(),
            "current_score": current_score["score"],
            "proposals_generated": len(proposals),
            "proposals_accepted": len(accepted),
            "dry_run": dry_run,
        }

        self._emit("evolution.completed", result)
        return result

    def _implement_proposal(self, proposal: dict):
        try:
            from apps.learn.heuristics import extract_heuristics, update_truth_learned
            heuristics = extract_heuristics()
            update_truth_learned(heuristics)
            log.info(f"  Updated truth/90-learned.yaml from {len(heuristics)} heuristics")
        except Exception as e:
            log.warning(f"  Failed to update heuristics: {e}")

    def _emit(self, event: str, payload: dict):
        try:
            subprocess.run(
                [sys.executable, str(EMIT_SCRIPT),
                 "--event", event,
                 "--kernel", "learning",
                 "--agent", "evolution",
                 "--subject-type", "evolution",
                 "--subject-id", "loop",
                 "--payload", json.dumps(payload)],
                capture_output=True, timeout=5
            )
        except Exception:
            pass


def run_evolution_cycle(dry_run: bool = False) -> dict:
    loop = EvolutionLoop()
    return loop.run_once(dry_run=dry_run)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Self-Evolution Loop")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without implementing")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
    result = run_evolution_cycle(dry_run=args.dry_run)
    print(json.dumps(result, indent=2))
