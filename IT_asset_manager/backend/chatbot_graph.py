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

# class StateManager:
#     def __init__(self):
#         self.state = {
#             "conversation_history": [],
#             "conversation_stage": None,
#             "current_request": {},
#         }

#     def get_state(self) -> dict:
#         return self.state.copy()

#     def update_state(self, key: str, value: any):
#         self.state[key] = value

#     def reset_state(self):
#         self.state = {
#             "conversation_history": [],
#             "conversation_stage": None,
#             "current_request": {},
#         }

@dataclass
class Node:
    """Base class for all nodes in the graph."""
    name: str
    process_func: Callable

    async def process(self, state: dict, message: str) -> dict:
        return await self.process_func(state, message)

class GreetingNode(Node):
    """Node for greeting."""
    def __init__(self):
        super().__init__(
            name="Greeting",
            process_func=self.process_greeting
        )

    async def process_greeting(self, state: dict, StateManager) -> dict:
        response = "Hello! What type of asset are you looking for?"
        state["conversation_stage"] = "awaiting_asset_type"
        state.conversation_history.append({"role": "assistant", "content": response})
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

    async def process_asset_request(self, state: dict, message: str) -> dict:
        asset_types = ["laptop", "desktop", "mouse", "keyboard"]
        mentioned_assets = [asset for asset in asset_types if asset in message.lower()]

        if mentioned_assets:
            asset_type = mentioned_assets[0]
            is_available = self.availability_tool.check_availability(asset_type)
            configs = self.availability_tool.get_configurations(asset_type)

            if is_available:
                response = f"Available configurations for {asset_type}: {', '.join(configs)}."
                state["conversation_stage"] = "awaiting_configuration"
                state["current_request"] = {"asset_type": asset_type}
            else:
                response = f"{asset_type} is not available. Would you like to try another asset?"
                state["conversation_stage"] = "awaiting_asset_type"
        else:
            response = "I didn't recognize the asset type. Please specify a laptop, desktop, mouse, or keyboard."
        
        state["conversation_history"].append({"role": "assistant", "content": response})
        print(f"Assistant: {response}")
        return state

class ConfigurationRequestNode(Node):
    """Node for configuration request."""
    def __init__(self):
        super().__init__(
            name="ConfigurationRequest",
            process_func=self.process_configuration
        )

    async def process_configuration(self, state: dict, StateManager) -> dict:
        state["current_request"]["configuration"] = state.user_message
        response = "Please provide the reason for your request."
        state["conversation_stage"] = "awaiting_reason"
        state.conversation_history.append({"role": "assistant", "content": response})
        print(f"Assistant: {response}")
        return state

class ReasonRequestNode(Node):
    """Node for reason request."""
    def __init__(self):
        super().__init__(
            name="ReasonRequest",
            process_func=self.process_reason
        )

    async def process_reason(self, state: dict, message: str) -> dict:
        state["current_request"]["reason"] = message
        response = f"Your request has been recorded: {state['current_request']}. Is there anything else you need?"
        state["conversation_stage"] = "request_completed"
        state["conversation_history"].append({"role": "assistant", "content": response})
        print(f"Assistant: {response}")
        return state

class InvalidQueryNode(Node):
    """Node for invalid queries."""
    def __init__(self):
        super().__init__(
            name="InvalidQuery",
            process_func=self.process_invalid
        )

    async def process_invalid(self, state: dict, message: str) -> dict:
        response = "Sorry, I didn't understand that. Can you please clarify?"
        state["conversation_history"].append({"role": "assistant", "content": response})
        print(f"Assistant: {response}")
        return state

class StateManager:
    conversation_history = []
    conversation_stage = None
    current_request = {}
    user_message = ""

class Graph:
    def __init__(self, availability_tool: AssetAvailabilityTool):
        self.availability_tool = availability_tool
        self.workflow = StateGraph(StateManager)

        # Initialize nodes
        self.start_node = Node(name="START", process_func=self.process_start)
        self.end_node = Node(name="END", process_func=self.process_end)
        self.greeting_node = GreetingNode()
        self.asset_request_node = AssetRequestNode(self.availability_tool)
        self.configuration_request_node = ConfigurationRequestNode()
        self.reason_request_node = ReasonRequestNode()
        self.invalid_query_node = InvalidQueryNode()

        # Add nodes to workflow
        self.workflow.add_node("start", self.start_node.process)
        self.workflow.add_node("greeting", self.greeting_node.process)
        self.workflow.add_node("asset_request", self.asset_request_node.process)
        self.workflow.add_node("configuration", self.configuration_request_node.process)
        self.workflow.add_node("reason", self.reason_request_node.process)
        self.workflow.add_node("invalid", self.invalid_query_node.process)
        self.workflow.add_node("end", self.end_node.process)

        # Define edges
        self.setup_edges()

    def setup_edges(self):
        def route_message(state: dict) -> str:
            stage = state["conversation_stage"]
            if stage == "awaiting_asset_type":
                return "asset_request"
            elif stage == "awaiting_configuration":
                return "configuration"
            elif stage == "awaiting_reason":
                return "reason"
            elif stage == "request_completed":
                return "end"  
            else:
                return "invalid"

        self.workflow.add_edge("start", "greeting")
        self.workflow.add_edge("greeting", route_message)
        self.workflow.add_edge("asset_request", route_message)
        self.workflow.add_edge("configuration", route_message)
        self.workflow.add_edge("reason", route_message)
        self.workflow.add_edge("invalid", route_message)
        self.workflow.add_edge("end", "start")  

    def process_start(self, state: StateManager) -> StateManager:
        response = "Welcome! How can I assist you today?"
        state.conversation_history.append({"role": "assistant", "content": response})
        print(f"Assistant: {response}")
        return state

    def process_end(self, state: StateManager) -> StateManager:
        response = "Thank you for using the service. Goodbye!"
        state.conversation_history.append({"role": "assistant", "content": response})
        print(f"Assistant: {response}")
        return state

    async def process_message(self, state: StateManager) -> StateManager:
        # state = self.state_manager.get_state()
        print(f"User: {state.user_message}")
        
        if state.user_message() in ["hi", "hello", "hii", "hey", "greetings"]:
            state = await self.greeting_node.process(state, state.user_message)
        else:
            state = await self.workflow.process(state, state.user_message)
        
        return state

# Example Execution
if __name__ == "__main__":
    availability_tool = AssetAvailabilityTool()
    # state_manager = StateManager()
    graph = Graph(availability_tool)

    # Simulate dynamic user interaction
    async def main():
        while True:
            user_input = input("User: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            await graph.process_message(user_input)

    asyncio.run(main())
