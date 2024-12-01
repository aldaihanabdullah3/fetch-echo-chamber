from uagents import Agent, Context, Model
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import json
import random
import os
import requests
import sys

class EchoChamber():
    def __init__(self, config_path: str, topic: str = None, web_address: str = None):
        # Open and read the JSON file
        with open(config_path, 'r') as file:
            data = json.load(file)
            self.config_path = config_path
            self.history = []
            self.iteration = 0
            self.system_prompt = data['system']
            self.personas = data['personas']
            self.refine = data['refine']
            self.post = topic if topic else data['post']
            self.web_address = web_address
            self.feedback_received = False
            self.feedback = None
            self.choose_persona()
        
    def choose_persona(self):
        personas = list(self.personas.values())
        random.shuffle(personas)
        return personas[0]

    def prepare_prompt(self):
        persona = self.choose_persona()
        persona_name = persona['name']
        persona_prompt = persona['prompt']
        prompt = self.system_prompt
        prompt += f'\n\nPERSONA: {persona_name}'
        prompt += f'\n\nDESCRIPTION: {persona_prompt}'
        prompt += f'\n\nSOCIAL MEDIA POST: {self.post}'
        return [SystemMessage(content=prompt)] + self.history

    def add_message(self, message: str):
        persona_msg = HumanMessage(content=f"{message}")
        self.history.append(persona_msg)
        self.iteration += 1
        #persona_msg.pretty_print()
        
        # Send the message to the Flask server
        if self.web_address is not None:
            speaker = message.split(':')[0]
            text = message.split(':')[-1]
            #print(f"#####{self.web_address}#####")
            requests.post(f'http://{self.web_address}/messages', json={'speaker': speaker,'text': text})
    
    def refine_prompt(self):
        prompt = self.system_prompt
        prompt += f'\n\nSOCIAL MEDIA POST: {self.post}'
        return [SystemMessage(content=self.refine)] + self.history
    
    def add_feedback(self, feedback: str):
        self.feedback = feedback
        self.feedback_received = True
        if self.web_address is not None:
            speaker = "Feedback"
            text = feedback
            print(f"#####{self.web_address}#####")
            requests.post(f'http://{self.web_address}/messages', json={'speaker': speaker,'text': text})



class Message(Model):
    api_key: str
    in_text: str

class Response(Model):
    response: str


if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else None
    web_address = sys.argv[2] if len(sys.argv) > 2 else None
    provider = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    max_iterations = sys.argv[4] if len(sys.argv) > 4 else 5

    echo_chamber_state = EchoChamber('config.json', topic, web_address)
    agent_mailbox_key = os.environ['AGENT_MAILBOX_KEY']
    agent_secret = os.environ['AGENT_SECRET']
    llm_address = "agent1qwngq9dfq2hktcfgntv3vxjfptd0awm7m2ppkadxudt9ggv59esysc58pkf"
    
    providers = [
        {'agent_address': "agent1qd28g66thm2djthyt3lnhe9s9g6zmhkghjyt9kp46655h3d9n0fg50294pr", 'api_key': os.environ['GROQ_API_KEY']},
        {'agent_address': "agent1qwngq9dfq2hktcfgntv3vxjfptd0awm7m2ppkadxudt9ggv59esysc58pkf", 'api_key': os.environ['GROQ_API_KEY']},
        {'agent_address': "agent1qw0cx9tyztnu56mqfypalexekcqrsf52n740tfftmgz9v04ufcl4sr2pn9m", 'api_key': os.environ['TOGTHER_API_KEY']},
        {'agent_address': "agent1qgy5jjqh5tm2wk6x9hus70lkpmlx2fmty7ts4yvkx70hluc52jvnwe4egg7", 'api_key': os.environ['TOGTHER_API_KEY']},
    ]

    api_key = providers[provider]['api_key']
    llm_address = providers[provider]['agent_address']

    agent = Agent(
        name="EchoChamber",
        seed= agent_secret,
        mailbox=f"{agent_mailbox_key}@https://agentverse.ai",
    )


    @agent.on_event("startup")
    async def set_startup(ctx: Context):
        global echo_chamber_state

        ctx.logger.info("Starting conversation:")
        ctx.logger.info(f"{echo_chamber_state.post}")

    @agent.on_interval(3)
    async def send_message(ctx: Context):
        global echo_chamber_state
        if echo_chamber_state.iteration >= max_iterations:
            if not echo_chamber_state.feedback_received:
                prompt = echo_chamber_state.refine_prompt()
                await ctx.send(llm_address, Message(api_key=api_key, in_text=str(prompt)))
            return
        else:
            prompt = echo_chamber_state.prepare_prompt()
            await ctx.send(llm_address, Message(api_key=api_key, in_text=str(prompt)))

    @agent.on_message(Response)
    async def handle_response(ctx: Context, sender: str, msg: Response):
        ctx.logger.info(f"{msg.response}")

        global echo_chamber_state
        if 'FEEDBACK' in msg.response:
            ctx.logger.info("Feedback received:")
            ctx.logger.info(f"{msg.response}")
            echo_chamber_state.add_feedback(msg.response)
        else:
            echo_chamber_state.add_message(msg.response)
        

    agent.run()
