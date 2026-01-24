import asyncio
from api.models import NLRequestBase
from nl.models import NLResolveRequest
from services.nl import NLService


nl_service = NLService(
    llm_provider="groq",
)


async def test_service():
    rsp = await nl_service.interpret_user_query(
        query="How much did I spend on fod?", query_plan={}
    )

    print(f"Intepret response: {rsp}")
    req_obj = NLRequestBase(user_id=5, query="how much did I spend on fod?")
    llm_rsp = await nl_service.resolve_user_query(
        user_id=req_obj.user_id,
        query=req_obj.query,
        parsed=rsp.delta.model_dump(),
    )

    # print(f"Resolve response: {llm_rsp}")


asyncio.run(test_service())
