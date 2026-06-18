# continuous_gsmb_runner.py
"""
Continuous GSM‑B Proof‑of‑Concept runner.

Keeps the full GSM‑B workflow alive (activation gate → protocol stack → spawn‑swarm validation → telemetry) until the process is stopped.
"""

import logging
import time
from datetime import datetime

# Import the existing POC entry‑point
from kopano.gsmb_poc import main as gsmb_main

logger = logging.getLogger(__name__)

def _iso_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def run_continuous(interval_seconds: int = 60) -> None:
    """Execute the GSM‑B POC in a loop.

    Parameters
    ----------
    interval_seconds : int
        Seconds to wait between successive runs. Default = 60 s.
    """
    logger.info("[ContinuousRunner] START – interval %s s", interval_seconds)
    iteration = 0
    try:
        while True:
            iteration += 1
            logger.info("[ContinuousRunner] Iteration %d – start %s", iteration, _iso_now())
            try:
                result = gsmb_main()
                logger.info(
                    "[ContinuousRunner] Iteration %d – completed %s – gate=%s, telemetry=%s",
                    iteration,
                    _iso_now(),
                    result.get("gate", {}).get("activation_allowed"),
                    bool(result.get("telemetry")),
                )
            except Exception as exc:
                logger.exception("[ContinuousRunner] Iteration %d – error %s", iteration, exc)
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        logger.info("[ContinuousRunner] STOPPED by user at %s", _iso_now())

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s – %(message)s",
    )
    run_continuous()
