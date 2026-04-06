from orch import logging


class ORCHApprentice:
    def __init__(self, mentors):
        self.mentors = mentors

    def learn(self, prompt):
        """Collect mentor responses and persist a simple audit trail."""
        logging.log_reasoning("ORCH", "start", f"Received prompt: {prompt}")
        responses = []
        for mentor in self.mentors:
            answer = mentor.respond(prompt)
            responses.append(answer)
            logging.log_execution("ORCH", f"mentor:{mentor.name}", answer)
        combined = " | ".join(responses)
        logging.log_reasoning("ORCH", "combine", f"Combined responses: {combined}")
        return combined
