from datetime import datetime

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

from email_crew.tools.create_draft import CreateDraftTool
from email_crew.tools.get_thread import GetThreadTool
from email_crew.tools.query_knowledge import QueryToolManager
from email_crew.schemas import ParsedEmails

from langchain_openai import ChatOpenAI

from utils.config_loader import app_config
get_thread_tool = GetThreadTool()
create_draft_tool =  CreateDraftTool()
query_tool = QueryToolManager()

####################################################################
# Workaround for Local Local
# Ref to https://community.crewai.com/t/error-at-running-crewai-using-ollama-llm/2666/4

from crewai.cli.constants import ENV_VARS

# Override the key name dynamically
for entry in ENV_VARS.get("ollama", []):
    if "API_BASE" in entry:
        entry["BASE_URL"] = entry.pop("API_BASE")  # Rename the key

###################################################################3

@CrewBase
class AiCrew():
  def __init__(self):
    self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    if app_config.CREWAI_OPENAI:
      self.llm = LLM(model="gpt-4o-mini")
    
    if app_config.CREWAI_LOCALLLM:
      self.llm = LLM(
      #model="ollama/llama3.1:latest",
      #model="ollama/deepseek-r1:32b",
      model="ollama/llama2:7b",
      base_url="http://localhost:11434",
      api_key=None,
      )
    
    ## Based on my experience, the alternative methods such as chatopenI, and OllamaLLM
    ## are not working well with crewai. 
    # When using Ollama, LiteLLM assumes the port is 11434, and will default to that if not specified 
    # or when the crew is long running
    
    
    
    self.agents_config = 'config/agents.yaml'
    self.tasks_config = 'config/tasks.yaml'
  
    
    
    


    
  @agent
  def inbox_monitor(self) -> Agent:
    return Agent(
      config=self.agents_config['inbox_monitor'],
      verbose=True,
      llm=self.llm,
    )
  
  @agent
  def shipping_analyst(self) -> Agent:
    return Agent(
      config=self.agents_config['shipping_analyst'],
      verbose=True,
      llm=self.llm,
      tools=[get_thread_tool.get_thread],
    )    

  @agent
  def ops_coordinator(self) -> Agent:
    return Agent(
      config=self.agents_config['ops_coordinator'],
      verbose=True,
      llm=self.llm,
      tools=[query_tool.get_query_tool()]
    ) 
  
  @agent
  def email_writer(self) -> Agent:
    return Agent(
      config=self.agents_config['email_writer'],
      verbose=True,
      llm=self.llm,
      tools=[create_draft_tool],
    )

  @task
  def inbox_monitor_task(self, emails=None) -> Task:
    return Task(
      config=self.tasks_config['inbox_monitor_task'],   
      output_file=f"outputs/crew/{self.timestamp}/inbox_monitor_task.txt", 
    )
  
  @task
  def shipping_analysis_task(self, emails=None) -> Task:
    return Task(
      config=self.tasks_config['shipping_analysis_task'],   
      output_file=f"outputs/crew/{self.timestamp}/shipping_analysis_task.json",
      #output_json=EmailList,
      output_pydantic=ParsedEmails, 
    )
  
  @task
  def action_support_task(self) -> Task:
    return Task(
      config=self.tasks_config['action_support_task'],
      context=[self.shipping_analysis_task()],  # 👈 Get results from shipping_analyst
      #output_json=EmailList,
      output_pydantic=ParsedEmails,
      output_file=f"outputs/crew/{self.timestamp}/action_support_task.json",
      ##async_execution=True  ## this will cause hallucination
    )
  
  @task
  def email_drafting_task(self) -> Task:
    output_file = f"outputs/crew/{self.timestamp}/email_drafting_task.jsonl"  #email_draft_output.jsonl
    return Task(
      config=self.tasks_config['email_drafting_task'],   
      context=[self.action_support_task()],
      output_file=output_file 
    )

  @crew
  def crew(self) -> Crew:
     """Creates the AiCrew crew"""
    # To learn how to add knowledge sources to your crew, check out the documentation:
    # https://docs.crewai.com/concepts/knowledge#what-is-knowledge
     return Crew(
      agents=self.agents, # Automatically created by the @agent decorator
      tasks=self.tasks, # Automatically created by the @task decorator
      process=Process.sequential,
      verbose=False,
      # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/,      
    )
