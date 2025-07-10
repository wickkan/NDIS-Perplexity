"""
Context Manager for NDIS Decoder
Stores and manages user session context to maintain continuity between related questions
"""
import json
import os
import time
from pathlib import Path
import uuid
from datetime import datetime

class NDISContextManager:
    def __init__(self, storage_dir=None):
        """
        Initialize the NDIS context manager
        
        Args:
            storage_dir (str, optional): Directory for storing context data
        """
        if storage_dir is None:
            storage_dir = os.path.join(Path(__file__).parent.parent, "data/context")
        
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # In-memory cache of active sessions
        self.active_sessions = {}
        
    def create_session(self, session_id=None):
        """
        Create a new session for tracking context
        
        Args:
            session_id (str, optional): Existing session ID to use
            
        Returns:
            bool: Success status
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
            
        timestamp = datetime.now().isoformat()
        
        session_data = {
            "session_id": session_id,
            "created_at": timestamp,
            "last_updated": timestamp,
            "context": {
                "queries": [],
                "pinned_items": [],
                "support_codes_mentioned": [],
                "relevant_policies": [],
                "recent_topics": []
            }
        }
        
        try:
            # Save to both memory and disk
            self.active_sessions[session_id] = session_data
            saved = self._save_session(session_id, session_data)
            return saved
        except Exception as e:
            print(f"Error creating session {session_id}: {e}")
            return False
        
    def get_session(self, session_id):
        """
        Retrieve a session context
        
        Args:
            session_id (str): Session ID
            
        Returns:
            dict: Session data or None if not found
        """
        # Try memory first, then disk
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
            
        session_file = os.path.join(self.storage_dir, f"{session_id}.json")
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                    
                # Cache in memory for future use
                self.active_sessions[session_id] = session_data
                return session_data
            except Exception as e:
                print(f"Error loading session {session_id}: {e}")
                
        return None
        
    def update_session(self, session_id, query=None, response=None, pinned_item=None):
        """
        Update a session with new information
        
        Args:
            session_id (str): Session ID
            query (str, optional): New query to add to context
            response (dict, optional): Response data to extract context from
            pinned_item (dict, optional): Item to pin for future reference
            
        Returns:
            bool: Success status
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return False
            
        session_data["last_updated"] = datetime.now().isoformat()
        
        # Add new query to context history
        if query:
            # Keep only the last 5 queries for context
            session_data["context"]["queries"].append({
                "query": query,
                "timestamp": datetime.now().isoformat()
            })
            if len(session_data["context"]["queries"]) > 5:
                session_data["context"]["queries"] = session_data["context"]["queries"][-5:]
        
        # Extract relevant information from response
        if response:
            # Extract support codes if present
            if "support_codes" in response:
                for code in response["support_codes"]:
                    if code not in session_data["context"]["support_codes_mentioned"]:
                        session_data["context"]["support_codes_mentioned"].append(code)
            
            # Extract policy references if present
            if "policies" in response:
                for policy in response["policies"]:
                    if policy not in session_data["context"]["relevant_policies"]:
                        session_data["context"]["relevant_policies"].append(policy)
            
            # Extract topic if present
            if "topic" in response:
                # Add to recent topics if not already there
                topics = session_data["context"]["recent_topics"]
                if response["topic"] not in topics:
                    topics.append(response["topic"])
                    # Keep only the 3 most recent topics
                    session_data["context"]["recent_topics"] = topics[-3:]
        
        # Add pinned item
        if pinned_item:
            session_data["context"]["pinned_items"].append({
                "content": pinned_item,
                "pinned_at": datetime.now().isoformat()
            })
        
        # Update both memory and disk
        self.active_sessions[session_id] = session_data
        self._save_session(session_id, session_data)
        
        return True
        
    def get_relevant_context(self, session_id, query=None):
        """
        Get relevant context for a new query
        
        Args:
            session_id (str): Session ID
            query (str, optional): Current query to match against context
            
        Returns:
            dict: Relevant context information
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return {}
            
        context = {
            "recent_queries": [],
            "pinned_items": session_data["context"]["pinned_items"],
            "relevant_codes": [],
            "relevant_policies": []
        }
        
        # Add recent queries for context
        if session_data["context"]["queries"]:
            context["recent_queries"] = [q["query"] for q in session_data["context"]["queries"][-2:]]
        
        # If we have a query, try to find relevant codes and policies
        if query:
            # Simple matching - could be enhanced with more sophisticated relevance
            for code in session_data["context"]["support_codes_mentioned"]:
                if code in query:
                    context["relevant_codes"].append(code)
            
            for policy in session_data["context"]["relevant_policies"]:
                # Check if policy keywords are in the query
                policy_keywords = policy.lower().split()
                query_words = query.lower().split()
                if any(keyword in query_words for keyword in policy_keywords):
                    context["relevant_policies"].append(policy)
        
        return context
        
    def pin_item(self, session_id, item):
        """
        Pin an item for future reference
        
        Args:
            session_id (str): Session ID
            item (dict): Item to pin
            
        Returns:
            bool: Success status
        """
        return self.update_session(session_id, pinned_item=item)
        
    def clean_old_sessions(self, max_age_days=7):
        """
        Clean up old sessions
        
        Args:
            max_age_days (int): Maximum age in days
            
        Returns:
            int: Number of sessions cleaned
        """
        cleaned = 0
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.storage_dir, filename)
                
                # Check file age
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > max_age_seconds:
                    try:
                        os.remove(file_path)
                        session_id = filename[:-5]  # Remove .json
                        if session_id in self.active_sessions:
                            del self.active_sessions[session_id]
                        cleaned += 1
                    except Exception as e:
                        print(f"Error cleaning session file {filename}: {e}")
                        
        return cleaned
        
    def _save_session(self, session_id, session_data):
        """
        Save session data to disk
        
        Args:
            session_id (str): Session ID
            session_data (dict): Session data
            
        Returns:
            bool: Success status
        """
        try:
            session_file = os.path.join(self.storage_dir, f"{session_id}.json")
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving session {session_id}: {e}")
            return False
