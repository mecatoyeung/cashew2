from ..base import StreamBase

class CombineFirstNLinesStreamProcessor(StreamBase):

    def __init__(self, n):
        self.n = n

    def process(self, input):
        if len(input["body"]) == 0:
            return [""]
        combinedRow = [ "" for _ in range(len(input["body"][0])) ]
        for i in range(0, int(self.n)):
            for j in range(0, len(input["body"][i])):
                if (i == (int(self.n) - 1)):
                    combinedRow[j] += str(input["body"][i][j])
                else:
                    combinedRow[j] += str(input["body"][i][j]) + " "

        output_body = input["body"][int(self.n):]
        output_body.insert(0, combinedRow)

        output = {
            'header': input["header"],
            'body': output_body
        }

        return output