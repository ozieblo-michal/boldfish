import openai
import pandas as pd
import constants

from io import StringIO


def openai_answer(
    content: str, OPENAI_API_KEY: str, model: str = "gpt-3.5-turbo"
) -> dict:
    openai.my_api_key = OPENAI_API_KEY
    messages = [{"role": "system", "content": constants.TASK_DEFINITION}]

    if content:
        messages.append(
            {"role": "user", "content": content},
        )
        chat = openai.ChatCompletion.create(model=model, messages=messages)

    reply = chat.choices[0].message.content
    csvStringIO = StringIO(reply)
    df = pd.read_csv(csvStringIO, sep=";")

    return df.set_index("concept").to_dict()["definition"]
