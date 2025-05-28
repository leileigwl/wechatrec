#!/usr/bin/env python3
import json
from bson import ObjectId
from mongo_utils import get_db_connection

# Custom JSON encoder for MongoDB ObjectId
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)  # Convert ObjectId to string
        return super().default(obj)

def test_mongo_serialization():
    """Test MongoDB serialization with ObjectId"""
    print("Testing MongoDB ObjectId serialization...")
    
    try:
        # Create a test document with ObjectId
        test_obj = {
            "_id": ObjectId(),
            "name": "Test Object",
            "description": "This is a test object with MongoDB ObjectId"
        }
        
        print("\nOriginal object:")
        print(test_obj)
        
        # Try standard JSON serialization (will fail)
        try:
            json_str = json.dumps(test_obj)
            print("\nStandard JSON serialization (should fail):")
            print(json_str)
        except TypeError as e:
            print(f"\nExpected error with standard serialization: {e}")
        
        # Try with custom encoder
        json_str = json.dumps(test_obj, cls=MongoJSONEncoder)
        print("\nCustom encoder JSON serialization (should work):")
        print(json_str)
        
        # Get actual data from MongoDB
        db = get_db_connection()
        collection = db["logs"]
        document = collection.find_one()
        
        if document:
            print("\nActual MongoDB document:")
            try:
                print(json.dumps(document, cls=MongoJSONEncoder, indent=2))
                print("\n✓ Serialization successful with custom encoder!")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("No documents found in the logs collection")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_mongo_serialization() 