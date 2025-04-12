import os
import tomli  # Use 'import toml' if Python <3.11
from dotenv import load_dotenv

# Load the ENV_PATH environment variable
env_path = os.getenv("ENV_PATH")
load_dotenv(env_path)

# Load the APP_CONFIG_PATH environment variable
config_path = os.getenv("APPCONFIG_PATH")
                        
class AppConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Load the app_config.toml configuration file."""
        config_path = os.getenv("APP_CONFIG_PATH", "/home/tanpohkeam/ubts/agent_app/config/app_config.toml")
        #print(config_path)

        try:
            with open(config_path, "rb") as file:
                config = tomli.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found at {config_path}")
        except tomli.TOMLDecodeError:
            raise ValueError(f"Error parsing TOML file: {config_path}")


       # Access environment variables securely
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.ENV_PATH = os.getenv("ENV_PATH")
        self.APPCONFIG_PATH = os.getenv("APPCONFIG_PATH")
 
        # Load directory paths
        self.OUTPUTS = config["folders"]["outputs"]
        self.LOGS = config["folders"]["logs"]
        self.SECRETS =  config["folders"]["secrets"]
        #self.OUTPUTS_EXPORT = config["folders"]["outputs_export"]   ## not used
        self.OUTPUTS_CREW = config["folders"]["outputs_crew"]
        self.OUTPUTS_RAG = config["folders"]["outputs_rag"]
        
        # Load Gmail credentials
        self.CREDENTIALS =  config["gmail"]["credential"]
        self.TOKEN = config["gmail"]["token"]
        self.TOKEN_PICKLE =  config["gmail"]["token_pickle"]
        self.SCOPE = config["gmail"]["scope"]
        
        #Load App settings
        self.CREWAI_OPENAI = config['crew']['use_openai']
        self.CREWAI_LOCALLLM = config['crew']['use_localllm']
      
        
        self.MILVUS_URL = config["milvus"]["url"]
        self.MILVUS_DIM = config["milvus"]["dim"]
        self.MILVUS_OVERRIDE = config["milvus"]["override"]
        self.MILVUS_HOSTIP = config["milvus"]["host_ip"]
        self.MILVUS_PORT = config["milvus"]["port"]
        self.MILVUS_COLLECTION = config["milvus"]["collection"]
        

        self.LLAMAINDEX_MODEL = config["llamaindex"]["model"]
        self.LLAMAINDEX_EMBEDDING = config["llamaindex"]["embedding"]
        self.LLAMAINDEX_DOCDIR = config["llamaindex"]["docs_dir"]
        self.LLAMINDEX_INPUTDIR = config["llamaindex"]["input_dir"]    
        
        self.LANGCHAIN_MAX_INTERATION = config["langchain"]["max_iterations"]
        self.LANGCHAIN_WAIT_DURATION = config["langchain"]["wait_duration"]

        # Ensure directories exist
        for path in [self.OUTPUTS, self.SECRETS, self.LOGS, self.OUTPUTS_RAG, self.OUTPUTS_CREW]:
            os.makedirs(path, exist_ok=True)

# Create a global config instance
app_config = AppConfig()

if __name__ == "__main__":
    print(app_config.OPENAI_API_KEY)
    
    # print(app_config.APP_HOME)
    print(app_config.OUTPUTS)
    print(app_config.LOGS)
    print(app_config.CREDENTIALS)
    print(app_config.SCOPE)
    
    print(app_config.MILVUS_URL)
    print(app_config.MILVUS_DIM)
    print(app_config.MILVUS_OVERRIDE)
    print(app_config.MILVUS_COLLECTION)
    
    print (app_config.LLAMAINDEX_MODEL)
    print (app_config.LLAMAINDEX_EMBEDDING)
    print (app_config.LLAMAINDEX_DOCDIR)
    print (app_config.LLAMINDEX_INPUTDIR)
   
        