import asyncio
import json
import websockets
from websockets.exceptions import ConnectionClosed
from app.config import settings
from app.llm_client import LLMClient
from app.mcp_tools import MCPToolRegistry
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NanobotAgent:
    def __init__(self):
        self.llm_client = LLMClient()
        self.mcp_tools = MCPToolRegistry()
        self.conversation_history = []

    async def handle_connection(self, websocket):
        """Handle WebSocket connection from client"""
        logger.info("Client connected")
        
        try:
            # Authenticate
            access_key = websocket.request.headers.get("X-Access-Key", "")
            if access_key != settings.NANOBOT_ACCESS_KEY:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Invalid access key"
                }))
                await websocket.close()
                return

            # Send welcome message
            await websocket.send(json.dumps({
                "type": "welcome",
                "message": "Connected to TourStats AI Assistant"
            }))

            # Handle messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    response = await self.process_message(data)
                    await websocket.send(json.dumps(response))
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON"
                    }))
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": str(e)
                    }))

        except ConnectionClosed:
            logger.info("Client disconnected")
        except Exception as e:
            logger.error(f"Connection error: {e}")

    async def process_message(self, data: dict) -> dict:
        """Process incoming message and return response"""
        message_type = data.get("type", "chat")
        message = data.get("message", "")

        if message_type == "chat":
            return await self.handle_chat(message)
        elif message_type == "query_statistics":
            return await self.handle_statistics_query(message)
        else:
            return {
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            }

    async def handle_chat(self, message: str) -> dict:
        """Handle chat message with AI response"""
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Keep only last 10 messages
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]

        # Get AI response
        response = await self.llm_client.get_response(
            message,
            self.conversation_history[:-1],  # Exclude current message
            settings.NANOBOT_SYSTEM_PROMPT
        )

        # Add to history
        self.conversation_history.append({"role": "assistant", "content": response})

        return {
            "type": "chat_response",
            "message": response,
        }

    async def handle_statistics_query(self, message: str) -> dict:
        """Handle statistics query using MCP tools"""
        try:
            # Use MCP tools to get statistics
            result = await self.mcp_tools.execute_query(message)
            
            return {
                "type": "statistics_response",
                "data": result,
            }
        except Exception as e:
            return {
                "type": "error",
                "message": f"Error querying statistics: {str(e)}"
            }


async def main():
    """Start the Nanobot WebSocket server"""
    agent = NanobotAgent()
    
    logger.info(f"Starting Nanobot agent on port 8000")
    
    async with websockets.serve(
        agent.handle_connection,
        "0.0.0.0",
        8000,
    ):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
