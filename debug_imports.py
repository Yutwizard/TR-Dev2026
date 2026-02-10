import sys
import os
sys.path.insert(0, os.path.abspath('src/backend'))

try:
    print("Importing InterbankService...")
    from app.services.interbank_service import InterbankService
    print("Success!")
except Exception as e:
    print(f"Failed: {e}")
    import traceback
    traceback.print_exc()
