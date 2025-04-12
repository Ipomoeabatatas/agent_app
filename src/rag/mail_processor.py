import json
import os
from datetime import datetime

from rag.milvus_loader import MilvusDataLoader
from rag.mail_extractor import ExportMailTool

from utils.config_loader import app_config


def is_valid_json(line):
        try:
            json.loads(line.strip())  # Try parsing the JSON
            return True
        except json.JSONDecodeError:
            return False
        
        
def rename_subdirectories(base_dir, suffix="-exported"):
        """Rename immediate subdirectories to end with the specified suffix (default is '-exported')."""
        with os.scandir(base_dir) as entries:
            for entry in entries:
                if entry.is_dir() and not entry.name.endswith(suffix):
                    target_path = f"{entry.path}{suffix}"
                    if not os.path.exists(target_path):
                        os.rename(entry.path, target_path)
                    else:
                        print(f"Skipping rename for {entry.path} as {target_path} already exists.")
            
def extract_valid_jsonl(base_dir=None, suffix="-exported"):
        """Extract valid JSON lines from .jsonl files in subdirectories not ending with the specified suffix."""
        valid_jsons = []
        with os.scandir(base_dir) as entries:
                for entry in entries:
                    if entry.is_dir() and not entry.name.endswith(suffix):
                        for file in os.scandir(entry.path):
                            if file.is_file() and file.name.endswith(".jsonl"):
                                try:
                                    with open(file.path, 'r', encoding='utf-8') as f:
                                        valid_jsons.extend(
                                            json_obj for line in filter(None, map(str.strip, f))
                                            if (json_obj := json.loads(line)) and isinstance(json_obj, dict)
                                        )
                                except (OSError, json.JSONDecodeError) as e:
                                    print(f"Error processing {file.path}: {e}   Not a valid JSON line - SKipping")
        return valid_jsons    
                    
     
def extract_mail(message_id=None, booking_ref=None, save_dir=None):
        print(f"Extracting email with messageId: {message_id} and bookingRef: {booking_ref}")
        export_tool = ExportMailTool()
        export_attachments_path = export_tool.extract_email_and_attachments(
            service=export_tool.service,
            msg_id=message_id,
            save_path=save_dir
        )
        return export_attachments_path
    
def extract_mail_v2(message_id=None, booking_ref=None, meta={}, save_dir=None):
        print(f"extract_mail_v2")
        print(f"Extracting email with messageId: {message_id} and bookingRef: {booking_ref}")
        export_tool = ExportMailTool()
        save_path = os.path.join(save_dir, booking_ref, datetime.now().strftime("%y%m%d%H%M%S"))
        print(f"save_path: {save_path}")
        os.makedirs(save_path, exist_ok=True)
        meta_path = os.path.join(save_path, "meta.jsonl")
        with open(meta_path, 'w', encoding='utf-8') as meta_file:
            meta_file.write(json.dumps(meta) + "\n")
            
        results = export_tool.extract_email_and_attachments(
            service=export_tool.service,
            msg_id=message_id,
            save_path=save_path
        )
        return results

def extract_emails(valid_jsons, rag_input_dir):         
    for json_obj in valid_jsons:
        message_id = json_obj.get("messageId")
        booking_ref = json_obj.get("bookingRef")
        extract_mail_v2(message_id=message_id, booking_ref=booking_ref, meta=json_obj, save_dir=rag_input_dir)
        
def vectorize_mail(messageId=None, bookingRef=None, load_dir= "path/to/folder"):
        loader = MilvusDataLoader()
        loader.load_and_store(input_dir=load_dir, collection_name=bookingRef)
        return (f"Vectorising email for {bookingRef}-{messageId} from: {load_dir}")

def vectorize_mails_v2(message_id=None, booking_ref=None, load_dir= "path/to/folder"):
        loader = MilvusDataLoader()
        loader.load_and_store(input_dir=load_dir, collection_name="emails")
        return (f"Vectorising email for {booking_ref}-{message_id} from: {load_dir}")
        
def extract_and_vectorise_emails(valid_jsons):
        for json_obj in valid_jsons:
            message_id = json_obj.get("messageId")
            booking_ref = json_obj.get("bookingRef")
            timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
            save_dir = os.path.join(app_config.OUTPUTS_EXPORT, booking_ref, timestamp)    
                         
            path = extract_mail(message_id=message_id, booking_ref=booking_ref,  save_dir = save_dir)
            vectorize_mail(messageId=message_id, bookingRef=booking_ref,load_dir=path)
            rename_subdirectories(base_dir=path, suffix="-vectorised")
            
            

    