from datetime import datetime

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from langchain_community.tools.gmail.get_thread import GmailGetThread
from langchain_community.agent_toolkits import GmailToolkit

#from .tools import GetGmailThreadTool
#from .tools import GetGmailThreadTool
#from .tools import GetThreadTool
#from .tools import CreateDraftTool

#from tools import GetThreadTool, CreateDraftTool
from email_crew.tools.create_draft import CreateDraftTool
from email_crew.tools.get_thread import GetThreadTool
#from crewai_module.schemas import  EmailMessage, EmailList
from email_crew.schemas import ParsedEmail, ParsedEmails

from msg_app.src.utils.config import config


## Pydantic Models
#from .model import EmailMessage, EmailList

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

# Create a CSV knowledge source
from crewai.knowledge.source.csv_knowledge_source import CSVKnowledgeSource
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource


csv_source = CSVKnowledgeSource(
    file_paths=["Portnet.csv"]
     )

# # Create a PDF knowledge source
pdf_source = PDFKnowledgeSource(
    file_paths=["kb_sample_policy_sop_regulations_ELVIN.pdf"]
     )



get_thread_tool = GetThreadTool()
create_draft_tool =  CreateDraftTool()


@CrewBase
class AiCrew():
  def __init__(self):
    self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

  llm = LLM(model="gpt-4o-mini")
  agents_config = 'config/agents.yaml'
  tasks_config = 'config/tasks.yaml'

  
  @agent
  def inbox_monitor(self) -> Agent:
    return Agent(
      config=self.agents_config['inbox_monitor'],
      verbose=True,
      llm=LLM(model="gpt-4o-mini"),
    )
  
  @agent
  def shipping_analyst(self) -> Agent:
    return Agent(
      config=self.agents_config['shipping_analyst'],
      verbose=True,
      llm=LLM(model="gpt-4o-mini"),
      tools=[get_thread_tool.get_thread],
  #       knowledge_sources=[pdf_source],
    )    

  @agent
  def ops_coordinator(self) -> Agent:
    return Agent(
      config=self.agents_config['ops_coordinator'],
      verbose=True,
      llm=LLM(model="gpt-4o-mini"),
      knowledge_sources=[pdf_source, csv_source],
    ) 
  
  @agent
  def email_writer(self) -> Agent:
    return Agent(
      config=self.agents_config['email_writer'],
      verbose=True,
      llm=LLM(model="gpt-4o"),
      tools=[create_draft_tool],
       ## tools=[GmailToolkit().get_tool("gmail_create_draft")]  # testing as per chatgpt
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
      output_file=f"outputs//crew/{self.timestamp}/action_support_task.json",
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
      verbose=True,
      # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/,
      
    )
