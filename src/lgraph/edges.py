from typing import Literal

class EdgeDefinition:
    def __init__(self):
        self.loop_count = 0  # not used
        self.gmail = 0
        
    def check_new_mail(self, state) -> Literal["no_new_email", "new_email"]:
        if len(state['emails']) == 0:
            print("## No new emails")
            return "no_new_email"
        else:
            print(f"## New emails: {len(state['emails'])}")
            return "new_email"
            
    def stop_graphflow(self, state) -> Literal["exceed_max_interations", "continue"]:
        if state["graph_counter"] >= state["max_iterations"]:
            return "exceed_max_interations"
        else:
            return "continue"
