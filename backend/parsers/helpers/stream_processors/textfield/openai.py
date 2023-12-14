import re
import requests
import json

from parsers.models.parser import Parser

from ..base import StreamBase


class OpenAIStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.open_ai_question = stream.open_ai_question
        parser = Parser.objects.select_related(
            "open_ai").get(pk=stream.rule.parser_id)
        self.resource_name = parser.open_ai.open_ai_resource_name
        self.api_key = parser.open_ai.open_ai_api_key
        self.deployment = parser.open_ai.open_ai_deployment

    def process(self, input):

        output = []

        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        open_ai_content = self.open_ai_question + \
            "Please return in JSON format.\nInput: " + "\n".join(input)
        json_data = {
            "messages": [{"role": "user", "content": open_ai_content}],
        }

        response = requests.post('https://' + self.resource_name + '.openai.azure.com/openai/deployments/' + self.deployment + '/chat/completions?api-version=2023-05-15',
                                 data=json.dumps(json_data), headers=headers)
        response_dict = json.loads(
            response.json()["choices"][0]["message"]['content'])
        if type(response_dict) == list:
            for row in response_dict:
                for col, value in row.items():
                    output.append(str(col) + ": " + str(value))
                output.append("")
        elif "Item Table" in response_dict:
            for row in response_dict["Item Table"]:
                for col, value in row.items():
                    output.append(str(col) + ": " + str(value))
                output.append("")
        else:
            for key, value in response_dict.items():
                output.append(key + ": " + value)

        return output
