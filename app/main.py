"""Main entrypoint for Altostrat HR Agent."""
import asyncio
from app.agent import HRAgentOrchestrator

agent = HRAgentOrchestrator(gcp_project="junho-elevate")

async def main():
    print("Starting Altostrat HR Agent (MVP 1)...")
    res = await agent.run("What is my sick leave entitlement?", employee_id="EMP-4")
    print("Agent Response:", res["response"])

if __name__ == "__main__":
    asyncio.run(main())
