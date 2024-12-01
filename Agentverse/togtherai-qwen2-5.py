
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from uagents import Agent, Bureau, Context, Model

class Message(Model):
    api_key: str
    in_text: str

class Response(Model):
    response: str

@agent.on_message(Message, replies={Response})
async def handle_message(ctx: Context, sender: str, msg: Message):
    """Implement message handler here"""
    llm = ChatOpenAI(base_url="https://api.together.xyz/v1",
        api_key=msg.api_key,
        model='Qwen/Qwen2.5-7B-Instruct-Turbo')
        
    ctx.logger.info(f"Received request from {sender}: {msg.in_text}")
    response = llm.invoke(msg.in_text)
    final_response = Response(response=response.content)
    ctx.logger.info(f"Replying to {sender}: {response.content}")
    await ctx.send(sender, final_response)
