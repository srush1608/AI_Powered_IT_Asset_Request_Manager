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

# Load environment variables
load_dotenv()

class AssetAvailabilityTool:
    def __init__(self):
        self.bluetally_base_url = "https://app.bluetallyapp.com/api/v1/assets"
        self.bluetally_api_key = os.getenv("BLUETALLY_API_KEY")
        print(f"DEBUG: Initialized AssetAvailabilityTool with API key: {'Present' if self.bluetally_api_key else 'Missing'}")
        print("*********************************")

    def fetch_all_assets(self) -> List[dict]:
        """Fetch all assets from the API with pagination"""
        print("\nDEBUG: Fetching all assets from API")
        all_assets = []
        offset = 0
        limit = 50  # Fetch 50 assets at a time
        while True:
            try:
                headers = {
                    "accept": "application/json",
                    "Authorization": f"Bearer {self.bluetally_api_key}"
                }
                print(f"DEBUG: Making API request to {self.bluetally_base_url}, offset: {offset}, limit: {limit}")

                response = requests.get(
                    self.bluetally_base_url,
                    headers=headers,
                    params={"limit": limit, "offset": offset}  # Adding the offset parameter to paginate
                )
                print(f"DEBUG: API Response Status Code: {response.status_code}")

                if response.status_code == 200:
                    assets = response.json()
                    if not assets:
                        print("DEBUG: No more assets found.")
                        break  # Break the loop if no more assets are available

                    all_assets.extend(assets)  # Add the fetched assets to the list
                    print(f"DEBUG: Successfully fetched {len(assets)} assets. Total count: {len(all_assets)}")

                    offset += limit  # Update the offset for the next page

                else:
                    print(f"DEBUG: API request failed. Status code: {response.status_code}")
                    print(f"DEBUG: Error response: {response.text}")
                    break  # Break the loop on failure

            except Exception as e:
                print(f"DEBUG: Error fetching assets: {str(e)}")
                break  # Break the loop if there's an error

        return all_assets

    def get_assets_by_type(self, asset_type: str) -> List[dict]:
        """Filter assets by type"""
        all_assets = self.fetch_all_assets()  # Fetch all assets
        matching_assets = [asset for asset in all_assets if asset_type in asset.get("product_name", "").lower()]
        print(matching_assets)
        return matching_assets

    def get_asset_configurations(self, assets: List[dict]) -> List[Dict[str, Any]]:
        """Extract configurations from assets"""
        print("\nDEBUG: Extracting configurations")
        configurations = []
        for asset in assets:
            config = {
                "name": asset.get("asset_name", ""),
                "category": asset.get("category_name", ""),
                "status": asset.get("status_id", ""),
                "serial": asset.get("asset_serial", "")
            }
            configurations.append(config)
        print(f"DEBUG: Found configurations: {configurations}")
        return configurations

class StateManager:
    def __init__(self):
        print("\nDEBUG: Initializing StateManager")
        self.conversation_history = []
        self.conversation_stage = None
        self.user_message = ""
        self.current_asset_type = None

    def add_message(self, role: str, content: str):
        print(f"DEBUG: Adding message - Role: {role}, Content: {content}")
        self.conversation_history.append({"role": role, "content": content})

    def set_user_message(self, message: str):
        print(f"DEBUG: Setting user message: {message}")
        self.user_message = message
        self.add_message("user", message)

    def set_stage(self, stage: str):
        print(f"DEBUG: Setting conversation stage to: {stage}")
        self.conversation_stage = stage

    def to_dict(self):
        return {
            "conversation_history": self.conversation_history,
            "conversation_stage": self.conversation_stage,
            "current_asset": {"type": self.current_asset_type}
        }

class GreetingNode:
    async def process(self, state: StateManager) -> StateManager:
        print("\nDEBUG: Processing greeting")
        response = "Hello! What type of asset are you looking for? (e.g., Laptop, Desktop)"
        state.set_stage("awaiting_asset_type")
        state.add_message("assistant", response)
        return state

class AssetRequestNode:
    def __init__(self, availability_tool: AssetAvailabilityTool):
        self.availability_tool = availability_tool

    async def process(self, state: StateManager) -> StateManager:
        print(f"\nDEBUG: Processing asset request for: {state.user_message}")
        asset_type = state.user_message.strip().lower()
        state.current_asset_type = asset_type

        matching_assets = self.availability_tool.get_assets_by_type(asset_type)

        if matching_assets:
            response = f"Do you have any specific configurations in mind for the {asset_type}? (e.g., brand, RAM size, storage capacity)"
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
        print(f"\nDEBUG: Processing configuration request for: {state.user_message}")
        asset_type = state.current_asset_type
        user_config = state.user_message.strip().lower()

        matching_assets = self.availability_tool.get_assets_by_type(asset_type)
        configurations = self.availability_tool.get_asset_configurations(matching_assets)

        if user_config:
            filtered_configurations = [
                config for config in configurations if user_config in config.values()
            ]
            response = f"Found {len(filtered_configurations)} configurations for {asset_type} with specified criteria:\n"
            for i, config in enumerate(filtered_configurations, 1):
                response += f"{i}. {config['name']} - {config['category']} - {config['status']} - {config['serial']}\n"
        else:
            response = f"Here are all the available configurations for {asset_type}:\n"
            for i, config in enumerate(configurations, 1):
                response += f"{i}. {config['name']} - {config['category']} - {config['status']} - {config['serial']}\n"

        response += "\nAre you satisfied with the configurations?"
        state.set_stage("check_availability")
        state.add_message("assistant", response)
        return state

class AvailabilityCheckNode:
    async def process(self, state: StateManager) -> StateManager:
        print("\nDEBUG: Checking availability")
        response = "Please confirm if you are satisfied with the configurations. If not, we can check another asset type or configuration."
        state.set_stage("request_completed")
        state.add_message("assistant", response)
        return state

class Graph:
    def __init__(self, availability_tool: AssetAvailabilityTool):
        print("\nDEBUG: Initializing Graph")
        self.availability_tool = availability_tool
        self.state_manager = StateManager()
        self.greeting_node = GreetingNode()
        self.asset_request_node = AssetRequestNode(self.availability_tool)
        self.configuration_node = ConfigurationNode(self.availability_tool)
        self.availability_check_node = AvailabilityCheckNode()

    async def process_message(self, message: str) -> dict:
        print(f"\nDEBUG: Processing message: {message}")
        self.state_manager.set_user_message(message.lower())
        
        # First check if it's a greeting when no stage is set
        if self.state_manager.conversation_stage is None and message.lower() in ["hi", "hello", "hey", "help", "start"]:
            print("DEBUG: Routing to greeting node")
            await self.greeting_node.process(self.state_manager)
        # Then handle the conversation flow based on stages
        elif self.state_manager.conversation_stage == "awaiting_asset_type":
            print("DEBUG: Routing to asset request node")
            await self.asset_request_node.process(self.state_manager)
        elif self.state_manager.conversation_stage == "awaiting_configuration":
            print("DEBUG: Routing to configuration node")
            await self.configuration_node.process(self.state_manager)
        elif self.state_manager.conversation_stage == "check_availability":
            print("DEBUG: Routing to availability check node")
            await self.availability_check_node.process(self.state_manager)
        elif self.state_manager.conversation_stage == "request_completed":
            print("DEBUG: Starting new conversation")
            await self.greeting_node.process(self.state_manager)
        else:
            # Only default to greeting if no stage is set and it's not a recognized greeting
            print("DEBUG: Starting new conversation (default)")
            await self.greeting_node.process(self.state_manager)

        return self.state_manager.to_dict()

if __name__ == "__main__":
    async def main():
        print("DEBUG: Starting main application")
        availability_tool = AssetAvailabilityTool()
        graph = Graph(availability_tool)
        
    asyncio.run(main())
