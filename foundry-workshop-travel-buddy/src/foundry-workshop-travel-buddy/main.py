# travel_assistant/main.py — Python entry point that hosts TravelBuddy: it creates
# the Foundry model client, defines the agent, and starts the Responses server.
# Complete the one TODO inside main() below.
import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import FoundryToolbox, ResponsesHostServer
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from tools import convert_currency, get_local_time, get_weather

load_dotenv(override=True)


def main() -> None:
    credential = DefaultAzureCredential()

    # Foundry model client, built from your .env settings.
    client = FoundryChatClient(
        project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=credential,
    )

    # FoundryToolbox resolves the toolbox endpoint from the environment
    # (TOOLBOX_ENDPOINT, or FOUNDRY_PROJECT_ENDPOINT + TOOLBOX_NAME), authenticates
    # every request with the credential, and transparently forwards the platform
    # per-request call-id to the toolbox. The hosting server enters the agent, which
    # connects the toolbox on first use and closes it at shutdown.
    toolbox = FoundryToolbox(credential)

    agent = Agent(
        client=client,
        name="travel-buddy",
        instructions=(
            "You are a friendly travel assistant that gives factually correct advice."
            "You are budget aware, give safety-minded tips, and concise trip-planning advice"
            "Use the Foundry Toolbox for flight search (when the traveler gives no "
            "departure date, call get_local_time and use the date part of its "
            "iso_time as today's date), for web search of current "
            "travel advisories and events, and for Code Interpreter to analyze an "
            "uploaded itinerary.csv (budget totals, currency conversion, charts)."
        ),
        tools = [
            get_weather,
            get_local_time,
            convert_currency,
            toolbox,
        ],
        # History is managed by the hosting infrastructure, so don't store it server-side.
        default_options={"store": False},
    )

    ResponsesHostServer(agent).run()


if __name__ == "__main__":
    main()
