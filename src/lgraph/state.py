from typing_extensions import TypedDict

class State(TypedDict):
	emails: list[dict]
	checked_emails_ids: list[str]
	action_required_emails: dict
	graph_counter: int  # Tracks the number of times "wait_next_run" is executed
	max_iterations: int  # Define max cycles before terminating
