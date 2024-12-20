# backend/chatbot_graph.py

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import datetime

@dataclass
class ConversationState:
    employee_id: str
    user_email: str
    conversation_history: List[str] = None
    conversation_stage: str = "initial"
    current_request: Dict[str, Any] = None
    status: str = "active"
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []

class StateManager:
    def __init__(self):
        self.states: Dict[str, ConversationState] = {}
    
    def get_or_create(self, employee_id: str, user_email: str) -> ConversationState:
        if employee_id not in self.states:
            self.states[employee_id] = ConversationState(employee_id=employee_id, user_email=user_email)
        return self.states[employee_id]

class AssetAvailabilityTool:
    def check_availability(self, asset_type: str) -> bool:
        # In a real implementation, this would check against your asset management system
        available_assets = {
            "laptop": True,
            "monitor": False,
            "keyboard": True,
            "mouse": True
        }
        return available_assets.get(asset_type.lower(), False)
    
    def get_configurations(self, asset_type: str) -> List[str]:
        configurations = {
            "laptop": ["Dell i5 16GB", "MacBook Pro M1", "Lenovo ThinkPad"],
            "monitor": ["24inch Dell", "27inch LG", "32inch Samsung"],
            "keyboard": ["Mechanical", "Wireless", "Standard"],
            "mouse": ["Wireless", "Gaming", "Standard"]
        }
        return configurations.get(asset_type.lower(), [])

class DynamicChatNode:
    def __init__(self, availability_tool: AssetAvailabilityTool):
        self.availability_tool = availability_tool
    
    async def process(self, state: ConversationState, message: str) -> ConversationState:
        message_lower = message.lower()
        
        # Initial greeting
        if message_lower in ["hi", "hello", "hii"]:
            response = "Hello! I can help you with asset requests. What type of asset are you looking for? (e.g., laptop, monitor)"
            state.conversation_history.append({"role": "assistant", "content": response})
            state.conversation_stage = "awaiting_asset_type"
            return state
        
        # Asset type identification
        if state.conversation_stage == "awaiting_asset_type":
            asset_types = ["laptop", "monitor", "keyboard", "mouse"]
            mentioned_assets = [asset for asset in asset_types if asset in message_lower]
            
            if mentioned_assets:
                asset_type = mentioned_assets[0]
                is_available = self.availability_tool.check_availability(asset_type)
                configs = self.availability_tool.get_configurations(asset_type)
                
                if is_available:
                    response = f"I can help you with a {asset_type} request. Here are the available configurations:\n"
                    response += "\n".join(f"- {config}" for config in configs)
                    response += "\n\nPlease specify your preferred configuration and the reason for your request."
                    state.current_request = {"asset_type": asset_type}
                    state.conversation_stage = "awaiting_configuration"
                else:
                    response = f"I apologize, but {asset_type}s are currently not available. Would you like to request another asset or be notified when a {asset_type} becomes available?"
                    state.conversation_stage = "handle_unavailable"
                
                state.conversation_history.append({"role": "assistant", "content": response})
                return state
        
        # Configuration and reason collection
        if state.conversation_stage == "awaiting_configuration":
            state.current_request["configuration"] = message
            response = "Thank you for providing the configuration. Could you please specify the reason for your request?"
            state.conversation_stage = "awaiting_reason"
            state.conversation_history.append({"role": "assistant", "content": response})
            return state
        
        # Process reason and complete request
        if state.conversation_stage == "awaiting_reason":
            state.current_request["reason"] = message
            response = (f"I've recorded your request for a {state.current_request['asset_type']} "
                       f"with configuration: {state.current_request['configuration']}.\n"
                       f"Reason: {state.current_request['reason']}\n\n"
                       "Your request has been submitted and will be reviewed by the IT team. "
                       "Is there anything else you need help with?")
            state.conversation_stage = "request_completed"
            state.conversation_history.append({"role": "assistant", "content": response})
            return state
        
        # Default response for unhandled stages or unclear messages
        response = "I'm not sure I understand. Could you please clarify what you need help with? You can request assets like laptops, monitors, keyboards, or mice."
        state.conversation_history.append({"role": "assistant", "content": response})
        return state

class InvalidQueryNode:
    async def process(self, state: ConversationState, message: str) -> ConversationState:
        response = "I apologize, but I can only help with asset-related queries. Could you please specify what type of asset you're interested in?"
        state.conversation_history.append({"role": "assistant", "content": response})
        return state

class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
    
    def add_node(self, node_id: str, node: Any):
        self.nodes[node_id] = node
        self.edges[node_id] = []
    
    def add_edge(self, from_node: str, to_node: str, condition):
        self.edges[from_node].append((to_node, condition))
    
    async def arun(self, state: ConversationState, message: str) -> ConversationState:
        current_node = "dynamic_chat"
        
        while current_node:
            next_node = None
            for to_node, condition in self.edges[current_node]:
                if condition(state, message):
                    next_node = to_node
                    break
            
            if next_node is None:
                break
                
            state = await self.nodes[next_node].process(state, message)
            current_node = next_node
            
        return state