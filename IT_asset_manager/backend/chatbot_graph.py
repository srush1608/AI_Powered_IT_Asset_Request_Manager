import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import os
from typing import List
import asyncio
from backend.database import get_db, Base, engine

# Load environment variables
load_dotenv()

class AssetAvailabilityTool:
    def __init__(self):
        self.bluetally_base_url = os.getenv("BLUETALLY_BASE_URL")
        self.bluetally_api_key = os.getenv("BLUETALLY_API_KEY")

    def check_availability(self, asset_type: str) -> bool:
        print("---------------------- Checking Availability ----------------------")
        url = f"{self.bluetally_base_url}/assets"
        params = {"limit": 50, "sort": "asset_id", "order": "asc", "offset": 0}
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.bluetally_api_key}",
        }

        response = requests.get(url, headers=headers, params=params)
        print(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Data Retrieved: {data}")
            for asset in data.get("assets", []):
                if asset_type.lower() in asset.get("name", "").lower():
                    return True
            return False
        return False

    def get_configurations(self, asset_type: str) -> List[str]:
        print("---------------------- Fetching Configurations ----------------------")
        url = f"{self.bluetally_base_url}/assets"
        params = {"limit": 50, "sort": "asset_id", "order": "asc", "offset": 0}
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.bluetally_api_key}",
        }

        response = requests.get(url, headers=headers, params=params)
        print(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Data Retrieved: {data}")
            configurations = []
            for asset in data.get("assets", []):
                if asset_type.lower() in asset.get("name", "").lower():
                    configurations.append(asset.get("configuration", "No configuration info"))
            return configurations
        return []

class StateManager:
    def __init__(self):
        self.state = {
            "conversation_history": [],
            "conversation_stage": None,
            "current_request": {},
        }

    def get_state(self) -> dict:
        return self.state

    def update_state(self, key: str, value: any):
        self.state[key] = value
        return self.state

    def reset_state(self):
        self.state = {
            "conversation_history": [],
            "conversation_stage": None,
            "current_request": {},
        }

class Graph:
    def __init__(self, availability_tool: AssetAvailabilityTool, state_manager: StateManager):
        self.availability_tool = availability_tool
        self.state_manager = state_manager

    async def process_message(self, message: str) -> dict:
        print("---------------------- Processing Message ----------------------")
        state = self.state_manager.get_state()
        message_lower = message.lower()

        print(f"Received Message: {message_lower}")
        chat_node = DynamicChatNode(self.availability_tool)

        # Handle greeting
        if message_lower in ["hi", "hello", "hii", "hey", "greetings"]:
            return await chat_node.handle_greeting(state)

        # Check for awaiting asset type
        if state["conversation_stage"] == "awaiting_asset_type":
            return await chat_node.handle_asset_request(state, message_lower)

        # Handle other cases
        if state["conversation_stage"] == "awaiting_configuration":
            return await chat_node.handle_configuration_request(state, message_lower)

        if state["conversation_stage"] == "awaiting_reason":
            return await chat_node.handle_reason_request(state, message_lower)

        invalid_node = InvalidQueryNode()
        return await invalid_node.handle_invalid_query(state)

class DynamicChatNode:
    def __init__(self, availability_tool: AssetAvailabilityTool):
        self.availability_tool = availability_tool

    async def handle_greeting(self, state: dict) -> dict:
        response = "Hello! I can help you with asset requests. What type of asset are you looking for? (e.g., laptop, desktop, mouse)"
        state["conversation_stage"] = "awaiting_asset_type"
        state["conversation_history"].append({"role": "assistant", "content": response})
        print(f"State after greeting: {state}")  # Debugging log
        return state

    async def handle_asset_request(self, state: dict, message: str) -> dict:
        print("---------------------- Handling Asset Request ----------------------")
        asset_types = ["laptop", "desktop", "mouse", "keyboard"]
        mentioned_assets = [asset for asset in asset_types if asset in message.lower()]
        print(f"Mentioned Assets: {mentioned_assets}")

        if mentioned_assets:
            asset_type = mentioned_assets[0]  # Use the first matched asset type
            is_available = self.availability_tool.check_availability(asset_type)
            configs = self.availability_tool.get_configurations(asset_type)

            if is_available:
                response = f"I can help you with a {asset_type} request. Here are the available configurations:\n"
                response += "\n".join(f"- {config}" for config in configs)
                response += "\n\nPlease specify your preferred configuration and the reason for your request."
                state["current_request"] = {"asset_type": asset_type}
                state["conversation_stage"] = "awaiting_configuration"
            else:
                response = f"I apologize, but {asset_type}s are currently not available. Would you like to request another asset?"
                state["conversation_stage"] = "awaiting_asset_type"

            state["conversation_history"].append({"role": "assistant", "content": response})
            return state

        # If no recognized asset type was mentioned
        response = "I didn't recognize the asset type. Please specify if you need a laptop, desktop, mouse, or keyboard."
        state["conversation_history"].append({"role": "assistant", "content": response})
        return state

    async def handle_configuration_request(self, state: dict, message: str) -> dict:
        print("---------------------- Handling Configuration Request ----------------------")
        state["current_request"]["configuration"] = message
        response = "Thank you for providing the configuration. Could you please specify the reason for your request?"
        state["conversation_stage"] = "awaiting_reason"
        state["conversation_history"].append({"role": "assistant", "content": response})
        return state

    async def handle_reason_request(self, state: dict, message: str) -> dict:
        print("---------------------- Handling Reason Request ----------------------")
        state["current_request"]["reason"] = message
        response = (
            f"I've recorded your request for a {state['current_request']['asset_type']} "
            f"with configuration: {state['current_request']['configuration']}.\n"
            f"Reason: {state['current_request']['reason']}\n\n"
            "Your request has been submitted and will be reviewed by the IT team. "
            "Is there anything else you need help with?"
        )
        state["conversation_stage"] = "request_completed"
        state["conversation_history"].append({"role": "assistant", "content": response})
        return state

class InvalidQueryNode:
    async def handle_invalid_query(self, state: dict) -> dict:
        print("---------------------- Handling Invalid Query ----------------------")
        response = "I'm not sure I understand. Could you please clarify what you need help with? You can request assets like laptops, desktops, keyboards, or mice."
        state["conversation_history"].append({"role": "assistant", "content": response})
        return state

if __name__ == "__main__":
    availability_tool = AssetAvailabilityTool()
    state_manager = StateManager()
    graph = Graph(availability_tool, state_manager)

    # Simulate interaction
    asyncio.run(graph.process_message("hi"))
    asyncio.run(graph.process_message("laptop"))
