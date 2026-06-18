import logging
from dataclasses import dataclass
from typing import List, Dict, Set
from .poc_foc_enforcer import ThreeVectorStateMachine, Verdict, FourWs

logger = logging.getLogger(__name__)

OWNED_DOMAINS: Set[str] = {
    "starfallsalvage.kopanolabs.com",
    "kopanolabs.com",
    "crisisconnect.kopanolabs.com",
    "kopanocontext.kopanolabs.com",
    "context.kopanolabs.com",
    "gsmb.kopanolabs.com",
    "web3gl.kopanolabs.com"
}

@dataclass
class DomainLink:
    protocol: str
    domain: str
    verdict: str
    details: dict

class ElasticDomainLinker:
    """
    Evolves GSMB to dominate elastic domains (HTTPS://) by checking ownership,
    enforcing POC on trusted domains, and executing rigorous severance of FOC domains
    using the 3-Vector State Machine.
    """
    def __init__(self):
        self.linked_domains: List[DomainLink] = []
        self.severed_domains: List[DomainLink] = []
        self.state_machine = ThreeVectorStateMachine()
        logger.info("[LPM] Evolved ElasticDomainLinker initialized on Black Beast & Cloud.")

    def evaluate_and_enforce(self, target_url: str) -> DomainLink:
        """
        Processes an elastic domain HTTPS URL through the IIDP/CBP/UBP state machine.
        If owned, validates as POC. If external/unauthorized, severs as FOC.
        """
        if not target_url.startswith("https://"):
            logger.warning(f"[LPM] URL {target_url} rejected: must be HTTPS.")
            details = {"reason": "Non-HTTPS protocol violation"}
            link = DomainLink(protocol="unknown", domain=target_url, verdict="REJECTED_PROTOCOL", details=details)
            self.severed_domains.append(link)
            return link

        domain = target_url.replace("https://", "").split("/")[0]
        
        if domain in OWNED_DOMAINS:
            # Enforce POC on Owned Domain
            logger.info(f"[LPM] Domain {domain} detected in Owned Registry. Executing POC Invariance Test.")
            report = self.state_machine.process_signal(
                signal_id=f"domain_{domain}",
                signal_content=f"Sovereign owned domain: {domain}",
                source="KPGS_OWNER_REGISTRY",
                intent="sovereign_governance_interface",
                temporal=1.0, spatial=1.0, social=1.0,
                economic=0.9, political=1.0, cultural=0.9,
                hierarchy="KPGS root domain hierarchy",
                keynote="Sovereign domain ownership",
                ark="Ensures secure invariant channel under WWJD Firewall",
                understanding="Direct trusted governance interface",
                who="KC Kholofelo Robyn Rababalela",
                what="Sovereign HTTPS connection point",
                where="Cloud Edge & Black Beast Core",
                why="To establish an invariant domain of control for the 32.8% purpose"
            )
            verdict = report.get("verdict", "UNKNOWN")
            link = DomainLink(protocol="https", domain=domain, verdict=verdict, details=report)
            self.linked_domains.append(link)
            logger.info(f"[LPM] Domain {domain} VALIDATED as POC. Linked to GSMB.")
        else:
            # Rigorous Severance of FOC Domain
            logger.warning(f"[LPM] Domain {domain} NOT owned. Enforcing rigorous severance of FOC.")
            report = self.state_machine.process_signal(
                signal_id=f"domain_{domain}",
                signal_content=f"Unauthorized domain connection attempt: {domain}",
                source="untrusted_external_network",
                intent="potential_infiltration_or_foc_spoof",
                temporal=0.1, spatial=0.2, social=0.1,
                economic=0.1, political=0.2, cultural=0.1,
                hierarchy="Out-of-covenant variant domain",
                keynote="Variant external channel",
                ark="Fails WWJD Firewall validation due to zero covenant",
                understanding="Non-governed external infrastructure",
                who="Untrusted external operator",
                what="Unauthorized domain infiltration",
                where="External network edge",
                why="Rigorous severance required to protect the 32.8% purpose"
            )
            verdict = report.get("verdict", "UNKNOWN")
            link = DomainLink(protocol="https", domain=domain, verdict=verdict, details=report)
            self.severed_domains.append(link)
            logger.error(f"[LPM] Domain {domain} SEVERED as FOC (Verdict: {verdict}). Connection terminated.")

        return link

    def get_summary(self) -> Dict[str, any]:
        return {
            "total_linked_poc": len(self.linked_domains),
            "linked_poc_domains": [d.domain for d in self.linked_domains],
            "total_severed_foc": len(self.severed_domains),
            "severed_foc_domains": [d.domain for d in self.severed_domains],
            "status": "synchronized_and_enforced"
        }
