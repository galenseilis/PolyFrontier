import io

import pandas as pd

from app.etl.pipeline import AbstractPipelineProcess


class CSVFileLoader(AbstractPipelineProcess):

    def __init__(self, encoding: str = 'utf-8'):
        super().__init__()
        self.encoding = encoding

    async def process(self, file: bytes) -> pd.DataFrame:
        print("Receiving incoming data...")
        return pd.read_csv(io.StringIO(str(file, self.encoding)), encoding=self.encoding)
