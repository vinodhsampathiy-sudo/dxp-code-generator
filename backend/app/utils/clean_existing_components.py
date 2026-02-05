#!/usr/bin/env python3
"""
Database migration script to clean escaped newlines from existing components.
This script will update all existing components in the database to have properly formatted code.
"""

import sys
import os
import re
from pymongo import MongoClient

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_newlines_for_preview(data):
    """
    Recursively clean escaped newlines from data structure.
    Converts '\\n' to actual newlines for better preview display.
    """
    if isinstance(data, str):
        # Replace escaped newlines with actual newlines
        return data.replace('\\n', '\n')
    elif isinstance(data, dict):
        return {key: clean_newlines_for_preview(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [clean_newlines_for_preview(item) for item in data]
    else:
        return data

def migrate_existing_components():
    """
    Clean escaped newlines from all existing components in the database.
    """
    try:
        # Connect to MongoDB directly
        MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        DATABASE_NAME = os.getenv("DATABASE_NAME", "dxp_component_generator")
        
        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        sessions_collection = db['chat_sessions']
        
        logger.info("Starting migration to clean escaped newlines from existing components...")
        
        # Get all sessions with generated components
        sessions = list(sessions_collection.find({'generated_components': {'$exists': True, '$ne': []}}))
        total_sessions = len(sessions)
        total_components_updated = 0
        
        logger.info(f"Found {total_sessions} sessions with components to process")
        
        for i, session in enumerate(sessions):
            session_id = str(session['_id'])
            logger.info(f"Processing session {i+1}/{total_sessions}: {session_id}")
            
            if 'generated_components' in session and session['generated_components']:
                components = session['generated_components']
                logger.info(f"  Found {len(components)} components in session {session_id}")
                
                session_updated = False
                
                for j, component in enumerate(components):
                    component_id = component.get('component_id', f'component_{j}')
                    logger.info(f"    Processing component {j+1}/{len(components)}: {component_id}")
                    
                    # Clean each field that might contain escaped newlines
                    fields_to_clean = [
                        'htl_code', 'sling_model_code', 'dialog_code', 
                        'content_xml', 'client_lib'
                    ]
                    
                    component_updated = False
                    for field in fields_to_clean:
                        if field in component and component[field]:
                            original_value = component[field]
                            
                            # Check if field contains escaped newlines
                            if isinstance(original_value, str) and '\\n' in original_value:
                                cleaned_value = clean_newlines_for_preview(original_value)
                                component[field] = cleaned_value
                                component_updated = True
                                session_updated = True
                                logger.info(f"      Cleaned field: {field}")
                            elif isinstance(original_value, dict):
                                # For client_lib which might be a dict
                                cleaned_value = clean_newlines_for_preview(original_value)
                                if cleaned_value != original_value:
                                    component[field] = cleaned_value
                                    component_updated = True
                                    session_updated = True
                                    logger.info(f"      Cleaned nested field: {field}")
                    
                    if component_updated:
                        total_components_updated += 1
                        logger.info(f"      ✅ Component {component_id} cleaned")
                    else:
                        logger.info(f"      ⏭️  Component {component_id} already clean, skipping")
                
                # Update the entire session if any components were updated
                if session_updated:
                    try:
                        sessions_collection.update_one(
                            {'_id': session['_id']},
                            {'$set': {'generated_components': components}}
                        )
                        logger.info(f"  ✅ Session {session_id} updated in database")
                    except Exception as e:
                        logger.error(f"  ❌ Failed to update session {session_id}: {str(e)}")
                else:
                    logger.info(f"  ⏭️  Session {session_id} had no changes, skipping database update")
            else:
                logger.info(f"  No components found in session {session_id}")
        
        client.close()
        logger.info(f"Migration completed! Updated {total_components_updated} components across {total_sessions} sessions.")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    migrate_existing_components()
