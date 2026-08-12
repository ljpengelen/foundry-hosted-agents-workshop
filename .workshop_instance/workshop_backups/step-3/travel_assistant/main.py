# travel_assistant/main.py — Python entry point that hosts TravelBuddy: it creates
# the Foundry model client, defines the agent, and starts the Responses server.
# Complete the one TODO inside main() below.
import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from tools import convert_currency, get_local_time, get_weather

load_dotenv(override=True)


def main() -> None:
    # Foundry model client, built from your .env settings.
    client = FoundryChatClient(
        project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=DefaultAzureCredential(),
    )

    agent = Agent(
        client=client,
        name="travel-buddy",
        instructions=(
            "You are a friendly travel assistant that gives factually correct advice."
            "You are budget aware, give safety-minded tips, and concise trip-planning advice"
            "Use the OctoTrip Flights MCP server when the traveler asks about "
            "flights, routes, fares, or schedules; pass IATA airport codes and a "
            "departure date (YYYY-MM-DD) — if the traveler doesn't give one, call "
            "get_local_time and use the date part of its iso_time as today's date — "
            "and summarize the options you find."
        ),
        tools = [
            get_weather,
            get_local_time,
            convert_currency,
            client.get_mcp_tool(
                name=os.environ["MCP_SERVER_LABEL"],
                url=os.environ["MCP_SERVER_URL"],
                approval_mode="never_require",
            ),
        ],
        # History is managed by the hosting infrastructure, so don't store it server-side.
        default_options={"store": False},
    )

    ResponsesHostServer(agent).run()


if __name__ == "__main__":
    main()
