class StreamBase:

    def __init__(self):
        pass

    def process(self, input):
        raise Exception("Stream does not implement 'process' function.")

