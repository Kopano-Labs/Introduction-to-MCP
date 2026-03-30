# orch/orchestration.py
from orch import logging

class ORCHApprentice:
    def __init__(self, mentors):
        self.mentors = mentors

    def learn(self, prompt):
        # Record reasoning before asking mentors
        logging.log_reasoning("ORCH", "start", f"Received prompt: {prompt}")

        responses = []
        for mentor in self.mentors:
            answer = mentor.respond(prompt)
            responses.append(answer)

            # Log each mentor interaction
            logging.log_execution("ORCH", f"mentor:{mentor.name}", answer)

        # Combine mentor responses (simplified example)
        combined = " | ".join(responses)

        # Log ORCH’s reasoning about the combined result
        logging.log_reasoning("ORCH", "combine", f"Combined responses: {combined}")

        return combined
from orch import logging

class ORCHApprentice:
    def __init__(self, mentors):
        self.mentors = mentors

    def learn(self, prompt):
        logging.log_reasoning("ORCH", "start", f"Received prompt: {prompt}")
        responses = []
        for mentor in self.mentors:
            answer = mentor.respond(prompt)
            responses.append(answer)
            logging.log_execution("ORCH", f"mentor:{mentor.name}", answer)
        combined = " | ".join(responses)
        logging.log_reasoning("ORCH", "combine", f"Combined responses: {combined}")
        return combined
