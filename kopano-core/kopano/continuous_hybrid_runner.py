# continuous_hybrid_runner.py
"""
KPGS Autonomous Hybrid Evolution Continuous Runner.
Runs the 15 Commands and 5 Pillars audit loop continuously to validate autonomous CF operations while the user is away.
"""

import logging
import time
from datetime import datetime, timezone
from kopano.hybrid_evolution import HybridEvolutionEngine

logger = logging.getLogger(__name__)

def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def run_continuous(interval_seconds: int = 30) -> None:
    logger.info("[LPM-AUTONOMOUS] Starting continuous Hybrid Evolution loop. Interval = %s s", interval_seconds)
    engine = HybridEvolutionEngine()
    iteration = 0
    
    try:
        while True:
            iteration += 1
            logger.info(f"[LPM-AUTONOMOUS] Starting Iteration {iteration} at {_utc_now()}")
            
            try:
                # Execute key sequence commands autonomously
                # 1. Sync mesh
                engine.run_command(7, {"description": "Autonomous mesh synchronization"})
                
                # 2. Link starfallsalvage in Cloud mode
                engine.run_command(1, {"url": "https://starfallsalvage.kopanolabs.com", "description": "Auto cloud link"})
                
                # 3. Link web3gl in Offline mode
                engine.run_command(2, {"url": "https://web3gl.kopanolabs.com", "description": "Auto offline link"})
                
                # 4. Drill Pillars
                engine.run_command(3, {"domain": "starfallsalvage.kopanolabs.com", "description": "Auto 5 Pillars drill"})
                
                # 5. Audit Commandments
                engine.run_command(4, {"domain": "web3gl.kopanolabs.com", "description": "Auto 15 Commandments audit"})
                
                # 6. Sever FOC attempt
                engine.run_command(6, {"url": f"https://unauthorized-node-{iteration}.net", "description": "Auto sever FOC"})
                
                # 7. Scale test
                scale_res = engine.run_command(15, {"description": "Auto empire scale readiness test"})
                
                logger.info(
                    "[LPM-AUTONOMOUS] Iteration %d complete at %s. Verified: 5 Pillars / 15 Commands / Empire Scale %s",
                    iteration,
                    _utc_now(),
                    scale_res.get("scale_test", {}).get("status")
                )
            except Exception as e:
                logger.exception("[LPM-AUTONOMOUS] Exception occurred during iteration %d: %s", iteration, e)
                
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        logger.info("[LPM-AUTONOMOUS] Stopped by user signal.")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s"
    )
    run_continuous()
