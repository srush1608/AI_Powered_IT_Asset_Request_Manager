# from langgraph.graph import StateGraph, START, END
# from pydantic import BaseModel, Field
# from typing import Optional, List, Dict, Any
# import logging
# import requests
# from dotenv import load_dotenv
# import os
# import asyncio

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
# load_dotenv()

# class ConversationState(BaseModel):
#     """
#     Represents the state of a conversation.
#     """
#     conversation_history: List[Dict[str, str]] = Field(default_factory=list, description="The conversation history.")
#     conversation_stage: Optional[str] = Field(default=None, description="Current stage of the conversation.")
#     user_message: str = Field(default="", description="The latest message from the user.")
#     current_asset_type: Optional[str] = Field(default=None, description="The type of asset being queried.")
#     assets: List[Dict] = Field(default_factory=list, description="List of fetched assets.")
#     valid_asset_types: List[str] = Field(default_factory=lambda: ["laptop", "desktop"], description="Supported asset types.")

# class AssetAvailabilityTool:
#     """
#     Tool for managing and retrieving asset availability from the Bluetally API.
#     """
#     def __init__(self):
#         self.bluetally_base_url = "https://app.bluetallyapp.com/api/v1/assets"
#         self.bluetally_api_key = os.getenv("BLUETALLY_API_KEY")
#         self.session = requests.Session()
#         logger.info(f"Initialized AssetAvailabilityTool with API key: {'Present' if self.bluetally_api_key else 'Missing'}")

#     def _make_request(self, params: Dict[str, Any]) -> Optional[List[Dict]]:
#         """
#         Makes a request to the Bluetally API.
#         """
#         headers = {
#             "accept": "application/json",
#             "authorization": f"Bearer {self.bluetally_api_key}",
#         }
#         try:
#             response = self.session.get(self.bluetally_base_url, headers=headers, params=params, timeout=30)
#             response.raise_for_status()
#             return response.json()
#         except requests.RequestException as e:
#             logger.error(f"API request failed: {e}")
#             return None

#     def fetch_all_assets(self) -> List[Dict]:
#         """
#         Retrieves all assets from the API.
#         """
#         all_assets = []
#         offset = 0
#         limit = 50

#         while True:
#             params = {"limit": limit, "offset": offset, "sort": "asset_id", "order": "asc"}
#             assets = self._make_request(params)
#             if not assets:
#                 break
#             all_assets.extend(assets)
#             if len(assets) < limit:
#                 break
#             offset += limit
        
#         return all_assets

#     def get_assets_by_type(self, asset_type: str) -> List[Dict]:
#         """
#         Filters assets by type.
#         """
#         all_assets = self.fetch_all_assets()
#         asset_type_lower = asset_type.lower()
#         return [
#             asset for asset in all_assets
#             if asset_type_lower in (
#                 asset.get("product_name", "").lower(),
#                 asset.get("category_name", "").lower(),
#                 asset.get("asset_name", "").lower()
#             )
#         ]

# class StateManager:
#     """
#     Manages conversation state and history.
#     """
#     def __init__(self):
#         logger.info("Initializing StateManager")
#         self.conversation_history = []
#         self.conversation_stage = None
#         self.user_message = ""
#         self.current_asset_type = None

#     def add_message(self, role: str, content: str):
#         self.conversation_history.append({"role": role, "content": content})

#     def set_user_message(self, message: str):
#         self.user_message = message
#         self.add_message("user", message)

#     def set_stage(self, stage: str):
#         valid_stages = {"awaiting_asset_type", "awaiting_configuration", "request_completed", None}
#         if stage not in valid_stages:
#             raise ValueError(f"Invalid stage: {stage}")
#         self.conversation_stage = stage

#     def to_dict(self) -> Dict[str, Any]:
#         return {
#             "conversation_history": self.conversation_history,
#             "conversation_stage": self.conversation_stage,
#             "current_asset": {"type": self.current_asset_type}
#         }

# class Graph:
#     """
#     Main graph for managing conversation and asset-related workflows.
#     """
#     def __init__(self, availability_tool: AssetAvailabilityTool):
#         logger.info("Initializing Graph")
#         self.availability_tool = availability_tool
#         self.state_manager = StateManager()

#     def process_message(self, message: str) -> Dict:
#         """
#         Processes user messages and manages state transitions.
#         """
#         self.state_manager.set_user_message(message)
#         response = ""
#         if not self.state_manager.conversation_stage:
#             response = "Hello! What type of asset are you looking for? (e.g., Laptop, Desktop)"
#             self.state_manager.set_stage("awaiting_asset_type")
#         elif self.state_manager.conversation_stage == "awaiting_asset_type":
#             assets = self.availability_tool.get_assets_by_type(message)
#             if assets:
#                 response = f"Found {len(assets)} {message}(s)."
#                 self.state_manager.set_stage("awaiting_configuration")
#             else:
#                 response = f"No {message}s available. Try another type."
#         elif self.state_manager.conversation_stage == "awaiting_configuration":
#             response = "Request recorded. Anything else?"
#             self.state_manager.set_stage("request_completed")
#         else:
#             response = "Conversation complete. Thank you!"

#         self.state_manager.add_message("assistant", response)
#         return self.state_manager.to_dict()

# if __name__ == "__main__":
#     async def main():
#         logger.info("Starting main application")
#         availability_tool = AssetAvailabilityTool()
#         graph = Graph(availability_tool)

#     asyncio.run(main())



















































import requests
from dotenv import load_dotenv
import os
from typing import List, Dict, Any
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AssetAvailabilityTool:
    def __init__(self):
        self.bluetally_base_url = "https://try.readme.io/https://app.bluetallyapp.com/api/v1/assets"
        self.bluetally_api_key = os.getenv("BLUETALLY_API_KEY")
        # Initialize session for persistent headers
        self.session = requests.Session()
        logger.info(f"Initialized AssetAvailabilityTool with API key: {'Present' if self.bluetally_api_key else 'Missing'}")
        
    def fetch_all_assets(self) -> List[dict]:
        """Fetch all assets from the API with pagination"""
        logger.info("Fetching all assets from API")
        all_assets = []
        offset = 0
        limit = 50
        
        try:
            # Set up headers for Cloudflare
            headers = {
                "accept": "application/json",
                "authorization": f"Bearer {self.bluetally_api_key}",
                "origin":"https://developers.bluetallyapp.com"
              
            }
            
            # Update session headers
            self.session.headers.update(headers)

            # Make first request to get total count
            params = {
                "limit": limit,
                "sort": "asset_id",
                "order": "asc",
                "offset": offset
            }
            
            logger.debug(f"Making initial API request with params: {params}")
            
            response = self.session.get(
                self.bluetally_base_url,
                params=params,
                timeout=30  # Add timeout
            )
            
            # Handle response codes
            if response.status_code == 200:
                try:
                    assets = response.json()
                    if assets:
                        all_assets.extend(assets)
                        while len(assets) == limit:
                            offset += limit
                            params["offset"] = offset
                            response = self.session.get(
                                self.bluetally_base_url,
                                params=params,
                                timeout=30
                            )
                            if response.status_code == 200:
                                assets = response.json()
                                all_assets.extend(assets)
                            else:
                                logger.error(f"Pagination request failed: {response.status_code}")
                                break
                except ValueError as e:
                    logger.error(f"JSON decode error: {str(e)}")
                    logger.error(f"Response content: {response.text[:200]}...")
            elif response.status_code == 403:
                logger.error("Access forbidden - Cloudflare protection detected")
                logger.error(f"Response headers: {dict(response.headers)}")
            else:
                logger.error(f"Initial API request failed: {response.status_code}")
                logger.error(f"Response content: {response.text[:200]}...")

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
        
        logger.info(f"Retrieved {len(all_assets)} assets in total")
        return all_assets

    def get_assets_by_type(self, asset_type: str) -> List[dict]:
        """Filter assets by type"""
        all_assets = self.fetch_all_assets()
        logger.info(f"Filtering {len(all_assets)} assets for type: {asset_type}")
        
        # Make search case-insensitive and more flexible
        asset_type_lower = asset_type.lower()
        matching_assets = [
            asset for asset in all_assets 
            if any(
                asset_type_lower in field.lower() 
                for field in [
                    asset.get("product_name", ""),
                    asset.get("category_name", ""),
                    asset.get("asset_name", "")
                ]
                if field
            )
        ]
        
        logger.info(f"Found {len(matching_assets)} matching assets for type: {asset_type}")
        return matching_assets

    def get_asset_configurations(self, assets: List[dict]) -> List[Dict[str, Any]]:
        """Extract configurations from assets"""
        logger.info(f"Extracting configurations for {len(assets)} assets")
        configurations = []
        for asset in assets:
            config = {
                "name": asset.get("asset_name", "Unknown"),
                "category": asset.get("category_name", "Uncategorized"),
                "status": asset.get("status_id", "Unknown"),
                "serial": asset.get("asset_serial", "N/A"),
                "type": asset.get("product_name", "Unknown")
            }
            configurations.append(config)
        return configurations

class StateManager:
    def __init__(self):
        logger.info("Initializing StateManager")
        self.conversation_history = []
        self.conversation_stage = None
        self.user_message = ""
        self.current_asset_type = None

    def add_message(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})

    def set_user_message(self, message: str):
        self.user_message = message
        self.add_message("user", message)

    def set_stage(self, stage: str):
        valid_stages = {
            "awaiting_asset_type",
            "awaiting_configuration",
            "request_completed",
            None
        }
        if stage not in valid_stages:
            raise ValueError(f"Invalid stage: {stage}")
        self.conversation_stage = stage

    def to_dict(self):
        return {
            "conversation_history": self.conversation_history,
            "conversation_stage": self.conversation_stage,
            "current_asset": {"type": self.current_asset_type}
        }
    
class GreetingNode:
    async def process(self, state: StateManager) -> StateManager:
        logger.info("Processing greeting")
        response = "Hello! What type of asset are you looking for? (e.g., Laptop, Desktop)"
        state.set_stage("awaiting_asset_type")
        state.add_message("assistant", response)
        return state

class AssetRequestNode:
    def __init__(self, availability_tool: AssetAvailabilityTool):
        self.availability_tool = availability_tool

    async def process(self, state: StateManager) -> StateManager:
        logger.info(f"Processing asset request: {state.user_message}")
        asset_type = state.user_message.strip().lower()
        state.current_asset_type = asset_type

        matching_assets = self.availability_tool.get_assets_by_type(asset_type)
        
        if matching_assets:
            configurations = self.availability_tool.get_asset_configurations(matching_assets)
            response = f"Found {len(matching_assets)} {asset_type}(s). Available configurations:\n"
            for i, config in enumerate(configurations, 1):
                response += f"{i}. {config['name']} - {config['category']} - Status: {config['status']}\n"
            response += "\nWould you like to request any of these configurations? (Reply with the number)"
            state.set_stage("awaiting_configuration")
        else:
            response = f"No {asset_type}s are currently available. Would you like to check another asset type?"
            state.set_stage("awaiting_asset_type")

        state.add_message("assistant", response)
        return state

class ConfigurationNode:
    def __init__(self, availability_tool: AssetAvailabilityTool):
        self.availability_tool = availability_tool

    async def process(self, state: StateManager) -> StateManager:
        logger.info(f"Processing configuration request: {state.user_message}")
        response = "Your request has been recorded. Is there anything else you need?"
        state.set_stage("request_completed")
        state.add_message("assistant", response)
        return state

class Edge:
    def __init__(self, from_node: str, to_node: str, condition: callable):
        self.from_node = from_node
        self.to_node = to_node
        self.condition = condition

class Graph:
    def __init__(self, availability_tool: AssetAvailabilityTool):
        logger.info("Initializing Graph")
        self.availability_tool = availability_tool
        self.state_manager = StateManager()
        
        # Initialize nodes
        self.nodes = {
            "greeting": GreetingNode(),
            "asset_request": AssetRequestNode(self.availability_tool),
            "configuration": ConfigurationNode(self.availability_tool)
        }
        
        # Define valid asset types
        self.valid_asset_types = {"laptop", "desktop"}
        
        # Initialize edges
        self.edges = self._setup_edges()

    def _setup_edges(self) -> List[Edge]:
        """Setup the edges defining valid transitions between nodes"""
        return [
            Edge(
                from_node="greeting",
                to_node="asset_request",
                condition=lambda msg: msg.lower() in self.valid_asset_types
            ),
            Edge(
                from_node="asset_request",
                to_node="configuration",
                condition=lambda msg: msg.isdigit()
            ),
            Edge(
                from_node="configuration",
                to_node="greeting",
                condition=lambda _: True  
            )
        ]

    def _get_next_node(self, current_stage: str, message: str) -> str:
        """Determine the next node based on current stage and message"""
        for edge in self.edges:
            if edge.from_node == current_stage and edge.condition(message):
                return edge.to_node
        return current_stage  # Stay in current node if no valid transition

    async def process_message(self, message: str) -> dict:
        logger.info(f"Processing message: {message}")
        self.state_manager.set_user_message(message.lower())
        
        try:
            # Handle initial state
            if self.state_manager.conversation_stage is None:
                if message.lower() in ["hi", "hello", "hey", "help", "start"]:
                    await self.nodes["greeting"].process(self.state_manager)
                    return self.state_manager.to_dict()

            # Map conversation stages to node names
            stage_to_node = {
                "awaiting_asset_type": "greeting",
                "awaiting_configuration": "asset_request",
                "request_completed": "configuration"
            }

            current_node = stage_to_node.get(self.state_manager.conversation_stage, "greeting")
            
            # Handle invalid asset type
            if current_node == "greeting" and message.lower() not in self.valid_asset_types:
                response = "Invalid asset type. Please specify either 'Laptop' or 'Desktop'."
                self.state_manager.add_message("assistant", response)
                self.state_manager.set_stage("awaiting_asset_type")
                return self.state_manager.to_dict()

            # Get next node based on edges
            next_node = self._get_next_node(current_node, message)
            
            # Process the message in the appropriate node
            if next_node == "greeting":
                await self.nodes["greeting"].process(self.state_manager)
            elif next_node == "asset_request":
                await self.nodes["asset_request"].process(self.state_manager)
            elif next_node == "configuration":
                await self.nodes["configuration"].process(self.state_manager)

            return self.state_manager.to_dict()
            
        except Exception as e:
            logger.error(f"Error in process_message: {str(e)}")
            raise


if __name__ == "__main__":
    async def main():
        logger.info("Starting main application")
        availability_tool = AssetAvailabilityTool()
        graph = Graph(availability_tool)
        

    
    asyncio.run(main())