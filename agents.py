
from uagents import Agent, Context, Protocol, Model


class FoodQuery(Model):
    message: str


class FoodReply(Model):
    response: str


agent = Agent(
    name="food_rescue_agent",
    seed="food_rescue_demo_agent_seed_change_this",
    port=8001,
    endpoint=["http://127.0.0.1:8001/submit"]
)

protocol = Protocol(name="food-rescue-protocol")


@protocol.on_message(model=FoodQuery, replies=FoodReply)
async def handle_food_query(
    ctx: Context,
    sender: str,
    msg: FoodQuery
):
    text = msg.message.lower()

    if "waste" in text or "surplus" in text:
        response = (
            "Please register the surplus food, quantity, "
            "location and safe pickup deadline in FoodRescue. "
            "The application can then match it with registered "
            "community kitchens."
        )
    elif "ngo" in text or "donate" in text:
        response = (
            "Register an NGO with its location, food capacity "
            "and contact details to find suitable food donations."
        )
    else:
        response = (
            "I am FoodRescue Agent. I help coordinate surplus "
            "food listings, NGO matching and pickup requests."
        )

    await ctx.send(sender, FoodReply(response=response))


agent.include(protocol)


if __name__ == "__main__":
    agent.run()
