# import requests
# from dotenv import load_dotenv
# from typing import List, Dict
# import os
# import asyncio
# from dataclasses import dataclass
# from typing import Any, Callable

# # Load environment variables
# load_dotenv()

# # Configuration for AssetAvailabilityTool
# def fetch_assets(product: str = None) -> List[dict]:
#     assets = []
#     offset = 0
#     limit = 50
#     bluetally_base_url = "https://app.bluetallyapp.com/api/v1"
#     bluetally_api_key = os.getenv("BLUETALLY_API_KEY")

#     while True:
#         url = f"{bluetally_base_url}/assets"
#         params = {"limit": limit, "sort": "asset_id", "order": "asc", "offset": offset}
#         if product:
#             params["product"] = product

#         headers = {
#             "accept": "application/json",
#             "Authorization": f"Bearer {bluetally_api_key}",
#         }

#         response = requests.get(url, headers=headers, params=params)
#         if response.status_code != 200:
#             print("Failed to fetch assets.")
#             break

#         data = response.json()
#         batch = data.get("assets", [])
#         assets.extend(batch)

#         if len(batch) < limit:
#             break
#         offset += limit

#     return assets

# def check_availability(asset_type: str) -> bool:
#     assets = fetch_assets()
#     return any(asset_type.lower() in asset.get("name", "").lower() for asset in assets)

# def get_configurations(asset_type: str) -> List[str]:
#     assets = fetch_assets()
#     return [
#         asset.get("configuration", "No configuration info")
#         for asset in assets
#         if asset_type.lower() in asset.get("name", "").lower()
#     ]

# # State Manager Functions
# def create_state_manager():
#     return {
#         "conversation_history": [],
#         "conversation_stage": None,
#         "user_message": ""
#     }

# def add_message(state, role: str, content: str):
#     state["conversation_history"].append({"role": role, "content": content})

# def set_user_message(state, message: str):
#     state["user_message"] = message
#     add_message(state, "user", message)

# def set_stage(state, stage: str):
#     state["conversation_stage"] = stage

# def to_dict(state):
#     return {
#         "conversation_history": state["conversation_history"],
#         "conversation_stage": state["conversation_stage"]
#     }

# # Node Processing Functions
# async def process_greeting(state):
#     response = "Hello! What type of asset are you looking for?"
#     set_stage(state, "awaiting_asset_type")
#     add_message(state, "assistant", response)
#     return state

# async def process_asset_request(state):
#     asset_types = ["laptop", "desktop", "mouse", "keyboard"]
#     mentioned_assets = [asset for asset in asset_types if asset in state["user_message"].lower()]

#     if mentioned_assets:
#         asset_type = mentioned_assets[0]
#         is_available = check_availability(asset_type)
#         configs = get_configurations(asset_type)

#         if is_available:
#             response = f"Available configurations for {asset_type}: {', '.join(configs)}."
#             set_stage(state, "awaiting_configuration")
#         else:
#             response = f"{asset_type} is not available. Would you like to try another asset?"
#             set_stage(state, "awaiting_asset_type")
#     else:
#         response = "I didn't recognize the asset type. Please specify a laptop, desktop, mouse, or keyboard."

#     add_message(state, "assistant", response)
#     return state

# async def process_configuration(state):
#     set_stage(state, "awaiting_reason")
#     response = "Please provide the reason for your request."
#     add_message(state, "assistant", response)
#     return state

# async def process_reason(state):
#     set_stage(state, "request_completed")
#     response = f"Your request has been recorded: {to_dict(state)}. Is there anything else you need?"
#     add_message(state, "assistant", response)
#     return state

# async def process_invalid(state):
#     response = "Sorry, I didn't understand that. Can you please clarify?"
#     add_message(state, "assistant", response)
#     return state

# # Main Processing Function
# async def process_message(state, message: str) -> dict:
#     set_user_message(state, message)

#     if message.lower() in ["hi", "hello", "hii", "hey", "greetings"]:
#         await process_greeting(state)
#     elif state["conversation_stage"] == "awaiting_asset_type":
#         await process_asset_request(state)
#     elif state["conversation_stage"] == "awaiting_configuration":
#         await process_configuration(state)
#     elif state["conversation_stage"] == "awaiting_reason":
#         await process_reason(state)
#     elif state["conversation_stage"] == "request_completed":
#         response = "Is there anything else you need help with?"
#         add_message(state, "assistant", response)
#     else:
#         await process_invalid(state)

#     return to_dict(state)

# # Example usage if running standalone
# if __name__ == "__main__":
#     async def main():
#         state = create_state_manager()

#         while True:
#             user_input = input("User: ")
#             if user_input.lower() in ["exit", "quit"]:
#                 break
#             result = await process_message(state, user_input)
#             print(f"State: {result['conversation_stage']}")

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
        self.bluetally_base_url = "https://app.bluetallyapp.com/api/v1/assets"
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
                # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                # "Accept-Language": "en-US,en;q=0.9",
                # "Accept-Encoding": "gzip, deflate, br",
                # "Connection": "keep-alive",
                # "Cache-Control": "no-cache",
                # "Pragma": "no-cache"
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

# class StateManager:
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
#         valid_stages = {
#             "awaiting_asset_type",
#             "awaiting_configuration",
#             "request_completed",
#             None
#         }
#         if stage not in valid_stages:
#             raise ValueError(f"Invalid stage: {stage}")
#         self.conversation_stage = stage

#     def to_dict(self):
#         return {
#             "conversation_history": self.conversation_history,
#             "conversation_stage": self.conversation_stage,
#             "current_asset": {"type": self.current_asset_type}
#         }
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
                condition=lambda _: True  # Always allow return to greeting after configuration
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