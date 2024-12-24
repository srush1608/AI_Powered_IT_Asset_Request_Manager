import requests
from dotenv import load_dotenv
from typing import List, Dict, TypedDict
import os
import asyncio
from langgraph.graph import StateGraph
from dataclasses import dataclass
from typing import Any, Callable

# Load environment variables
load_dotenv()

class AssetAvailabilityTool:
    def __init__(self):
        self.bluetally_base_url = "https://app.bluetallyapp.com/api/v1"
        self.bluetally_api_key = os.getenv("BLUETALLY_API_KEY")

    def fetch_assets(self) -> List[dict]:
        assets = []
        offset = 0
        limit = 50

        while True:
            url = f"{self.bluetally_base_url}/assets"
            params = {"limit": limit, "sort": "asset_id", "order": "asc", "offset": offset}
            headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {self.bluetally_api_key}",
            }

            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                print("Failed to fetch assets.")
                break

            data = response.json()
            batch = data.get("assets", [])
            assets.extend(batch)

            if len(batch) < limit:
                break
            offset += limit

        return assets

    def check_availability(self, asset_type: str) -> bool:
        assets = self.fetch_assets()
        return any(asset_type.lower() in asset.get("name", "").lower() for asset in assets)

    def get_configurations(self, asset_type: str) -> List[str]:
        assets = self.fetch_assets()
        return [
            asset.get("configuration", "No configuration info")
            for asset in assets
            if asset_type.lower() in asset.get("name", "").lower()
        ]

class StateManager:
    def __init__(self):
        self.conversation_history = []
        self.conversation_stage = None
        self.current_request = {}
        self.user_message = ""

    def add_message(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})

    def set_user_message(self, message: str):
        self.user_message = message
        self.add_message("user", message)

    def set_stage(self, stage: str):
        self.conversation_stage = stage

    def to_dict(self):
        return {
            "conversation_history": self.conversation_history,
            "conversation_stage": self.conversation_stage,
            "current_request": self.current_request
        }

@dataclass
class Node:
    """Base class for all nodes in the graph."""
    name: str
    process_func: Callable

    async def process(self, state: StateManager) -> StateManager:
        return await self.process_func(state)

class GreetingNode(Node):
    """Node for greeting."""
    def __init__(self):
        super().__init__(
            name="Greeting",
            process_func=self.process_greeting
        )

    async def process_greeting(self, state: StateManager) -> StateManager:
        response = "Hello! What type of asset are you looking for?"
        state.set_stage("awaiting_asset_type")
        state.add_message("assistant", response)
        print(f"Assistant: {response}")
        return state

class AssetRequestNode(Node):
    """Node for asset type request."""
    def __init__(self, availability_tool: AssetAvailabilityTool):
        super().__init__(
            name="AssetRequest",
            process_func=self.process_asset_request
        )
        self.availability_tool = availability_tool

    async def process_asset_request(self, state: StateManager) -> StateManager:
        asset_types = ["laptop", "desktop", "mouse", "keyboard"]
        mentioned_assets = [asset for asset in asset_types if asset in state.user_message.lower()]

        if mentioned_assets:
            asset_type = mentioned_assets[0]
            is_available = self.availability_tool.check_availability(asset_type)
            configs = self.availability_tool.get_configurations(asset_type)

            if is_available:
                response = f"Available configurations for {asset_type}: {', '.join(configs)}."
                state.set_stage("awaiting_configuration")
                state.current_request["asset_type"] = asset_type
            else:
                response = f"{asset_type} is not available. Would you like to try another asset?"
                state.set_stage("awaiting_asset_type")
        else:
            response = "I didn't recognize the asset type. Please specify a laptop, desktop, mouse, or keyboard."
        
        state.add_message("assistant", response)
        print(f"Assistant: {response}")
        return state

class ConfigurationRequestNode(Node):
    """Node for configuration request."""
    def __init__(self):
        super().__init__(
            name="ConfigurationRequest",
            process_func=self.process_configuration
        )

    async def process_configuration(self, state: StateManager) -> StateManager:
        state.current_request["configuration"] = state.user_message
        response = "Please provide the reason for your request."
        state.set_stage("awaiting_reason")
        state.add_message("assistant", response)
        print(f"Assistant: {response}")
        return state

class ReasonRequestNode(Node):
    """Node for reason request."""
    def __init__(self):
        super().__init__(
            name="ReasonRequest",
            process_func=self.process_reason
        )

    async def process_reason(self, state: StateManager) -> StateManager:
        state.current_request["reason"] = state.user_message
        response = f"Your request has been recorded: {state.current_request}. Is there anything else you need?"
        state.set_stage("request_completed")
        state.add_message("assistant", response)
        print(f"Assistant: {response}")
        return state

class InvalidQueryNode(Node):
    """Node for invalid queries."""
    def __init__(self):
        super().__init__(
            name="InvalidQuery",
            process_func=self.process_invalid
        )

    async def process_invalid(self, state: StateManager) -> StateManager:
        response = "Sorry, I didn't understand that. Can you please clarify?"
        state.add_message("assistant", response)
        print(f"Assistant: {response}")
        return state

class Graph:
    def __init__(self, availability_tool: AssetAvailabilityTool):
        self.availability_tool = availability_tool
        self.state_manager = StateManager()
        self.workflow = Graph(StateManager)

        
        # Initialize nodes
        self.greeting_node = GreetingNode()
        self.asset_request_node = AssetRequestNode(self.availability_tool)
        self.configuration_request_node = ConfigurationRequestNode()
        self.reason_request_node = ReasonRequestNode()
        self.invalid_query_node = InvalidQueryNode()

    #     # Add nodes to workflow
    #     # self.workflow.add_node("start", self.start_node.process)
        self.workflow.add_node("greeting", self.greeting_node.process)
        self.workflow.add_node("asset_request", self.asset_request_node.process)
        self.workflow.add_node("configuration", self.configuration_request_node.process)
        self.workflow.add_node("reason", self.reason_request_node.process)
        self.workflow.add_node("invalid", self.invalid_query_node.process)
        self.workflow.add_node("end", self.end_node.process)

    #     self.workflow.add_edge("start", "greeting")
        self.workflow.add_edge("greeting","asset_request")
        self.workflow.add_edge("asset_request", "configuration")
        self.workflow.add_edge("configuration", "reason")
        self.workflow.add_edge("reason", "invalid")
        self.workflow.add_edge("invalid","end")
        self.workflow.add_edge("end", "greeting")  

    # async def process_start(self, state: StateManager) -> StateManager:
    #     response = "Welcome! How can I assist you today?"
    #     state.add_message("assistant", response)
    #     print(f"Assistant: {response}")
    #     return state

    async def process_end(self, state: StateManager) -> StateManager:
        response = "Thank you for using the service. Goodbye!"
        state.add_message("assistant", response)
        print(f"Assistant: {response}")
        return state

    async def process_message(self, message: str) -> dict:
        self.state_manager.set_user_message(message)
        print(f"User: {message}")
        
        if message.lower() in ["hi", "hello", "hii", "hey", "greetings"]:
            await self.greeting_node.process(self.state_manager)
        else:
            await self.process_workflow(self.state_manager)

        return self.state_manager.to_dict()

    async def process_workflow(self, state: StateManager) -> StateManager:
        stage = state.conversation_stage
        if stage is None or stage == "":
            await self.greeting_node.process(state)
        elif stage == "awaiting_asset_type":
            await self.asset_request_node.process(state)
        elif stage == "awaiting_configuration":
            await self.configuration_request_node.process(state)
        elif stage == "awaiting_reason":
            await self.reason_request_node.process(state)
        elif stage == "request_completed":
            response = "Is there anything else you need help with?"
            state.add_message("assistant", response)
            state.set_stage("awaiting_asset_type")
        else:
            await self.invalid_query_node.process(state)
        return state

# Example usage if running standalone
if __name__ == "__main__":
    async def main():
        availability_tool = AssetAvailabilityTool()
        graph = Graph(availability_tool)
        
        while True:
            user_input = input("User: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            result = await graph.process_message(user_input)
            print(f"State: {result['conversation_stage']}")

    asyncio.run(main())