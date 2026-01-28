from services.ai_factory import get_ai_service
from config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Initialize service
ai_service = get_ai_service()

class ComplianceRouter:
    """
    Routes user queries to the correct Regulatory Universe (Folder).
    """
    UNIVERSES = [
        "00_TrainingReference",
        "01_FL_State_Authority",
        "02_CMS_Medicare_Authority", 
        "03_Federal_ACA_Authority",
        "04_ERISA_IRS_SelfFunded",
        "05_FL_Medicaid_Agency",
        "06_Carrier_FMO_Policies"
    ]
    SYSTEM_PROMPT = """You are a Compliance Router for a health insurance agency.
Your ONLY job is to classify the user's question into exactly ONE of the following Regulatory Universes.

Universes:
- 01_FL_State_Authority: General Florida insurance laws, licensing, appointments.
- 02_CMS_Medicare_Authority: Medicare Advantage, Part D, CMS marketing rules.
- 03_Federal_ACA_Authority: Affordable Care Act, Marketplace, Subsidies.
- 04_ERISA_IRS_SelfFunded: Employer group plans, Tax rules, Self-funded/ERISA.
- 05_FL_Medicaid_Agency: Mixed eligibility, Medicaid specific rules.
- 06_Carrier_FMO_Policies: Specific carrier rules (Aetna, UHC, Humana) or FMO policies.

Output exactly ONE Universe name from the list above.
If the question is greetings or vague, output "NONE".
"""

    def determine_universe(self, query: str) -> Optional[str]:
        """
        Classify query using LLM.
        """
        try:
            prompt = f"{self.SYSTEM_PROMPT}\n\nUSER QUESTION: {query}\n\nUNIVERSE:"
            # Use AI Service
            result = ai_service.complete(prompt)
            
            # Clean up result
            result = result.strip().replace('"', '').replace("'", "")
            
            # Validation
            if result in self.UNIVERSES:
                logger.info(f"Routed query to universe: {result}")
                return result
            
            logger.info(f"No specific universe match (Result: {result}).")
            return None
            
        except Exception as e:
            logger.error(f"Routing failed: {e}")
            return None

# Global Instance
compliance_router = ComplianceRouter()
