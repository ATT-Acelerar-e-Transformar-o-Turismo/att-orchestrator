#!/usr/bin/env python3
"""
Test script to verify MongoDB timezone handling behavior.
Tests both datetime objects and string storage/retrieval.
"""

import sys
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient
import subprocess
import time
import json

def start_mongodb_container():
    """Start MongoDB container and wait for it to be ready"""
    print("🐳 Starting MongoDB container...")
    
    # Stop any existing container
    subprocess.run(["docker", "stop", "test-mongo"], capture_output=True)
    subprocess.run(["docker", "rm", "test-mongo"], capture_output=True)
    
    # Start new container
    result = subprocess.run([
        "docker", "run", "-d", 
        "--name", "test-mongo",
        "-p", "27018:27017",
        "mongo:7"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to start MongoDB: {result.stderr}")
        return False
    
    print("⏳ Waiting for MongoDB to be ready...")
    for i in range(30):  # Wait up to 30 seconds
        try:
            client = MongoClient("mongodb://localhost:27018", serverSelectionTimeoutMS=1000)
            client.admin.command('ping')
            print("✅ MongoDB is ready!")
            client.close()
            return True
        except Exception:
            time.sleep(1)
    
    print("❌ MongoDB failed to start in time")
    return False

def stop_mongodb_container():
    """Stop and remove MongoDB container"""
    print("🛑 Stopping MongoDB container...")
    subprocess.run(["docker", "stop", "test-mongo"], capture_output=True)
    subprocess.run(["docker", "rm", "test-mongo"], capture_output=True)

def test_mongodb_timezone():
    """Test MongoDB timezone handling"""
    client = MongoClient("mongodb://localhost:27018")
    db = client.test_db
    collection = db.test_collection
    
    # Clear collection
    collection.delete_many({})
    
    print("\n🧪 Testing MongoDB timezone behavior...\n")
    
    # Test 1: Store datetime objects with different timezones
    print("1️⃣  Testing datetime objects:")
    
    utc_time = datetime(2025, 8, 27, 10, 30, 45, tzinfo=timezone.utc)
    plus1_time = datetime(2025, 8, 27, 11, 30, 45, tzinfo=timezone(timedelta(hours=1)))
    plus5_time = datetime(2025, 8, 27, 15, 30, 45, tzinfo=timezone(timedelta(hours=5)))
    naive_time = datetime(2025, 8, 27, 10, 30, 45)  # No timezone
    
    test_docs = [
        {"type": "utc_datetime", "timestamp": utc_time, "original": "UTC: 2025-08-27 10:30:45+00:00"},
        {"type": "plus1_datetime", "timestamp": plus1_time, "original": "+01:00: 2025-08-27 11:30:45+01:00"},  
        {"type": "plus5_datetime", "timestamp": plus5_time, "original": "+05:00: 2025-08-27 15:30:45+05:00"},
        {"type": "naive_datetime", "timestamp": naive_time, "original": "Naive: 2025-08-27 10:30:45"}
    ]
    
    collection.insert_many(test_docs)
    
    # Read back datetime objects
    results = list(collection.find())
    for doc in results:
        print(f"   Stored: {doc['original']}")
        print(f"   Retrieved: {doc['timestamp']} (type: {type(doc['timestamp'])})")
        print(f"   Timezone info: {doc['timestamp'].tzinfo}")
        print()
    
    # Test 2: Store timezone strings
    print("2️⃣  Testing timezone strings:")
    
    collection.delete_many({})
    
    string_docs = [
        {"type": "utc_string", "timestamp": "2025-08-27T10:30:45.123+00:00"},
        {"type": "plus1_string", "timestamp": "2025-08-27T11:30:45.123+01:00"},
        {"type": "plus5_string", "timestamp": "2025-08-27T15:30:45.123+05:00"},
        {"type": "z_string", "timestamp": "2025-08-27T10:30:45.123Z"},
        {"type": "naive_string", "timestamp": "2025-08-27T10:30:45.123"}
    ]
    
    collection.insert_many(string_docs)
    
    # Read back strings
    results = list(collection.find())
    for doc in results:
        print(f"   Stored: {doc['timestamp']}")
        print(f"   Retrieved: {doc['timestamp']} (type: {type(doc['timestamp'])})")
        print()
    
    # Test 3: Simulate data_ingestor.py conversion behavior
    print("3️⃣  Testing fromisoformat conversion (like data_ingestor.py):")
    
    collection.delete_many({})
    
    # Store string, then convert like data_ingestor does
    original_string = "2025-08-27T11:30:45.123+01:00"
    collection.insert_one({"type": "original_string", "timestamp": original_string})
    
    # Read and convert like data_ingestor.py
    doc = collection.find_one({"type": "original_string"})
    timestamp_str = doc["timestamp"]
    
    # Convert string to datetime (like data_ingestor.py line 54-55)
    converted_dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    
    print(f"   Original string: {original_string}")
    print(f"   Retrieved string: {timestamp_str}")
    print(f"   After fromisoformat(): {converted_dt} (tzinfo: {converted_dt.tzinfo})")
    
    # Now store the converted datetime
    collection.insert_one({"type": "converted_datetime", "timestamp": converted_dt})
    
    # Read it back
    converted_doc = collection.find_one({"type": "converted_datetime"})
    final_dt = converted_doc["timestamp"]
    
    print(f"   Stored datetime: {converted_dt} (tzinfo: {converted_dt.tzinfo})")  
    print(f"   Retrieved datetime: {final_dt} (tzinfo: {final_dt.tzinfo})")
    print(f"   UTC conversion happened: {converted_dt.astimezone(timezone.utc)} → {final_dt}")
    
    client.close()

def main():
    """Main test function"""
    if not start_mongodb_container():
        sys.exit(1)
    
    try:
        test_mongodb_timezone()
        print("\n✅ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        stop_mongodb_container()

if __name__ == "__main__":
    main()