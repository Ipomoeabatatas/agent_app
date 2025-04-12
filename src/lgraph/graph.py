# Standard Libraries

# Langchain Modules

# Langgraph Modules

# Custom Modules
from langgraph.graph import StateGraph
from lgraph.state import State
from lgraph.nodes import NodeDefinition
from lgraph.edges import EdgeDefinition


class Workflow:
    def __init__(self):
        self.nodes = NodeDefinition()
        self.edges = EdgeDefinition()
        self.graph = self.build_workflow()

    def build_workflow(self):
        builder = StateGraph(State)
        
        builder.add_node("check_email", self.nodes.check_email)
        builder.add_node("handoff_to_aicrew", self.nodes.handoff_to_aicrew)
        builder.add_node("save_to_kb", self.nodes.save_to_kb)
        builder.add_node("wait_next_run", self.nodes.wait_next_run)
        builder.add_node("end", self.nodes.end_workflow)
        
        builder.set_entry_point("check_email")
        builder.add_conditional_edges("check_email", 
                                      self.edges.check_new_mail,
                                      {
                                          "new_email": 'handoff_to_aicrew',
                                          "no_new_email": 'wait_next_run'
                                      })
        builder.add_edge("handoff_to_aicrew", "save_to_kb")
        builder.add_edge("save_to_kb", "wait_next_run")
        builder.add_conditional_edges("wait_next_run",
                                      self.edges.stop_graphflow,
                                      {
                                          "exceed_max_interations": 'end',
                                          "continue": 'check_email'
                                      })
        return builder.compile()

if __name__ == "__main__":
    # Usage
    graph_instance = Workflow()
    graph = graph_instance.graph
