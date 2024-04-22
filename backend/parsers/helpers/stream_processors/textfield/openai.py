from openai import AzureOpenAI

from parsers.models.parser import Parser

from parsers.helpers.stream_processors.base import StreamBase

from parsers.models.stream_type import StreamType


class OpenAITextStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.open_ai_question = stream.open_ai_question
        parser = Parser.objects.select_related(
            "open_ai").get(pk=stream.rule.parser_id)
        self.resource_name = parser.open_ai.open_ai_resource_name
        self.api_key = parser.open_ai.open_ai_api_key
        self.deployment = parser.open_ai.open_ai_deployment

    def process(self, input):

        client = AzureOpenAI(
            azure_endpoint='https://' + self.resource_name + '.openai.azure.com/',
            api_key=self.api_key,
            api_version="2024-02-15-preview"
        )

        open_ai_content = self.open_ai_question + \
            "Please return in JSON format.\nInput: " + "\n".join(input["value"])
        message_text = [{"role": "system", "content": open_ai_content}]

        try:
            completion = client.chat.completions.create(
                model=self.deployment,
                messages=message_text,
                temperature=0.2,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
            )
        except Exception as e:
            raise e

        return {
            "type": StreamType.JSON.value,
            "value": completion.choices[0].message.content.replace("```json\n", "").replace("\n```", "").replace("Output:", "")
        }

