from nl.llm_providers.factory import get_llm_provider
import asyncio

from nl.prompt import TRANSLATE_USER_INTENTION

# from nl.nl_query_processor import NLQueryResolver


async def main():
    nL_query = get_llm_provider(llm_provider="ollama", temperature=0.5)
    rsp = await nL_query.chat_with_format(
        query="are you sure?", prompt=TRANSLATE_USER_INTENTION
    )
    print(f"Response: {rsp}")
    print(f"Response type: {type(rsp)}")


if __name__ == "__main__":
    asyncio.run(main())
