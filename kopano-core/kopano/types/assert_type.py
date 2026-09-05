"""
Kopano Asserts Engine - Verifiable Claims & Sovereign Receipts
Governed by Kopano Context (KC) Protocol 13
"""
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import hashlib


class KopanoAssert(BaseModel):
    assert_id: str
    session_id: str
    rtc_identity: str
    intent_domain: str
    claim: str
    residency: str = "ZA-CPT (South Africa North)"
    proof_hash: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @classmethod
    def emit(
        cls,
        session_id: str,
        identity: str,
        domain: str,
        claim: str,
        residency: str = "ZA-CPT (South Africa North)"
    ) -> "KopanoAssert":
        ts = datetime.now(timezone.utc).timestamp()
        raw_seed = f"{session_id}:{identity}:{domain}:{claim}:{residency}:{ts}"
        proof = hashlib.sha256(raw_seed.encode("utf-8")).hexdigest()
        return cls(
            assert_id=f"AST-{proof[:8].upper()}",
            session_id=session_id,
            rtc_identity=identity,
            intent_domain=domain,
            claim=claim,
            residency=residency,
            proof_hash=proof,
        )
