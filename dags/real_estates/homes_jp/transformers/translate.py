import trio
from easygoogletranslate import EasyGoogleTranslate


async def _translate(data):
    translated_data = []

    async with trio.open_nursery() as nursery:
        for item in data:
            nursery.start_soon(translate_item, item, translated_data)

    return translated_data


async def translate_item(item, translated_data):
    translator = EasyGoogleTranslate(source_language="ja", target_language="en", timeout=60)

    data = {key: translator.translate(value) for key, value in item.items()}
    translated_data.append(data)
