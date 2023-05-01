import pandas as pd
import io


async def import_from_file(file: bytes):
    c = pd.read_csv(io.StringIO(str(file, 'utf-8')), encoding='utf-8')
    print(c.head())
