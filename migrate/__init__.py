from dotenv import load_dotenv
import os
load_dotenv()
global AK
AK = os.getenv('DNT_AK')
