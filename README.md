
# FoodRescue AI

FoodRescue AI is a prototype for reducing food waste by
connecting surplus food providers with NGOs and community kitchens.

## Features

- Register surplus food
- Register NGOs and community kitchens
- Match organizations by location and capacity
- Create pickup requests
- Track pickup and delivery status
- Experimental Fetch.ai uAgents messaging agent

## Requirements

- Python 3.10 or later
- pip

## Setup

Create and activate a virtual environment.

Windows:

    python -m venv .venv
    .venv\Scripts\activate

Install packages:

    pip install -r requirements.txt

Run the application:

    streamlit run main.py

Run the messaging agent in another terminal:

    python agents.py

## Important

This is a prototype. Matching does not verify actual food
safety, NGO availability, or completed deliveries. Real
donations require confirmation and appropriate safety checks.

The uAgents messaging agent has not yet been registered
on Agentverse or integrated with ASI:One ACP.
