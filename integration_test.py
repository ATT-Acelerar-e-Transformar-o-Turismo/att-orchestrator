#!/usr/bin/env python3
"""
Global Integration Test for ATT Orchestrator Data Flow

This test validates the complete data flow:
external_source -> data-mq -> data-collector -> services-mq -> 
resource-service -> services-mq -> indicator-service

Note: Currently, resource-service doesn't implement wrapper-to-resource translation.
This test includes a workaround to demonstrate the expected flow.
"""

import asyncio
import aiohttp
import aio_pika
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Service endpoints
RESOURCE_SERVICE_URL = "http://localhost:8003"
INDICATOR_SERVICE_URL = "http://localhost:8001"
USER_SERVICE_URL = "http://localhost:8006"

# RabbitMQ connections
DATA_MQ_URL = "amqp://user:password@localhost:5672/"
SERVICES_MQ_URL = "amqp://guest:guest@localhost:5674/"

# Test data
TEST_WRAPPER_ID = 12345
TEST_RESOURCE_ID = "test-resource-001"
TEST_INDICATOR_NAME = "Integration Test Indicator"
TEST_DOMAIN_ID = "test-domain"
TEST_SUBDOMAIN = "test-subdomain"


class IntegrationTest:
    def __init__(self):
        self.data_mq_connection = None
        self.services_mq_connection = None
        self.session = None
        
    async def setup(self):
        """Initialize connections"""
        print("Setting up connections...")
        self.session = aiohttp.ClientSession()
        self.data_mq_connection = await aio_pika.connect_robust(DATA_MQ_URL)
        self.services_mq_connection = await aio_pika.connect_robust(SERVICES_MQ_URL)
        
    async def teardown(self):
        """Clean up connections"""
        if self.session:
            await self.session.close()
        if self.data_mq_connection:
            await self.data_mq_connection.close()
        if self.services_mq_connection:
            await self.services_mq_connection.close()
            
    async def create_test_resource(self) -> str:
        """Create a test resource in resource-service"""
        print(f"\nCreating test resource with ID: {TEST_RESOURCE_ID}")
        
        resource_data = {
            "name": "Integration Test Resource",
            "startPeriod": "2024-01-01",
            "endPeriod": "2024-12-31"
        }
        
        async with self.session.post(
            f"{RESOURCE_SERVICE_URL}/resources/",
            json=resource_data
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✓ Resource created: {result}")
                return result.get("_id", TEST_RESOURCE_ID)
            else:
                print(f"✗ Failed to create resource: {response.status}")
                return TEST_RESOURCE_ID
                
    async def create_test_indicator(self) -> Optional[str]:
        """Create a test indicator and associate resource"""
        print(f"\nCreating test indicator...")
        
        # Create indicator
        indicator_data = {
            "name": TEST_INDICATOR_NAME,
            "periodicity": "daily",
            "favourites": 0,
            "governance": False,
            "description": "Indicator for integration testing"
        }
        
        async with self.session.post(
            f"{INDICATOR_SERVICE_URL}/indicators/{TEST_DOMAIN_ID}/{TEST_SUBDOMAIN}/",
            json=indicator_data
        ) as response:
            if response.status != 200:
                print(f"✗ Failed to create indicator: {response.status}")
                text = await response.text()
                print(f"Response: {text}")
                return None
                
            result = await response.json()
            indicator_id = result["_id"]
            print(f"✓ Indicator created with ID: {indicator_id}")
            
        # Associate resource with indicator
        print(f"\nAssociating resource {TEST_RESOURCE_ID} with indicator...")
        async with self.session.post(
            f"{INDICATOR_SERVICE_URL}/indicators/{indicator_id}/resources",
            json={"resource_id": TEST_RESOURCE_ID}
        ) as response:
            if response.status == 200:
                print(f"✓ Resource associated with indicator")
            else:
                print(f"✗ Failed to associate resource: {response.status}")
                
        return indicator_id
        
    async def send_data_to_data_mq(self) -> Dict[str, Any]:
        """Send test data to data-mq queue"""
        print(f"\nSending data to data-mq with wrapper_id: {TEST_WRAPPER_ID}")
        
        channel = await self.data_mq_connection.channel()
        queue = await channel.declare_queue("data_queue", durable=True)
        
        # Prepare test data
        test_data = {
            "wrapper_id": TEST_WRAPPER_ID,
            "data_segment": [
                {
                    "x": datetime.now().isoformat(),
                    "y": 42.5
                },
                {
                    "x": datetime.now().isoformat(),
                    "y": 43.7
                },
                {
                    "x": datetime.now().isoformat(), 
                    "y": 44.2
                }
            ]
        }
        
        message = aio_pika.Message(
            body=json.dumps(test_data).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        
        await channel.default_exchange.publish(
            message,
            routing_key=queue.name
        )
        
        print(f"✓ Data sent to data-mq: {len(test_data['data_segment'])} data points")
        await channel.close()
        
        return test_data
        
    async def simulate_wrapper_to_resource_translation(self):
        """
        Simulate the wrapper-to-resource translation that should happen in resource-service.
        This is a workaround since resource-service doesn't currently implement this.
        """
        print(f"\nSimulating wrapper-to-resource translation...")
        print(f"(This should be done by resource-service)")
        
        # Consume from services_queue
        channel = await self.services_mq_connection.channel()
        services_queue = await channel.declare_queue("services_queue", durable=True)
        
        # Get one message
        message = await services_queue.get(timeout=5)
        if message:
            data = json.loads(message.body.decode())
            print(f"✓ Received message from services_queue: wrapper_id={data.get('wrapper_id')}")
            
            # Transform wrapper_id to resource_id
            if data.get("wrapper_id") == TEST_WRAPPER_ID:
                transformed_data = {
                    "resource": TEST_RESOURCE_ID,
                    "data": data["data_segment"]
                }
                
                # Publish to resource_data queue
                resource_queue = await channel.declare_queue("resource_data", durable=True)
                
                transformed_message = aio_pika.Message(
                    body=json.dumps(transformed_data).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                )
                
                await channel.default_exchange.publish(
                    transformed_message,
                    routing_key=resource_queue.name
                )
                
                print(f"✓ Published transformed message to resource_data queue")
                print(f"  Wrapper ID {TEST_WRAPPER_ID} -> Resource ID {TEST_RESOURCE_ID}")
                
            await message.ack()
        else:
            print(f"✗ No message received from services_queue")
            
        await channel.close()
        
    async def verify_indicator_data(self, indicator_id: str) -> bool:
        """Verify that data reached the indicator service"""
        print(f"\nVerifying data in indicator service...")
        
        # Wait a bit for processing
        await asyncio.sleep(2)
        
        # Check indicator data endpoint
        async with self.session.get(
            f"{INDICATOR_SERVICE_URL}/indicators/{indicator_id}/data"
        ) as response:
            if response.status != 200:
                print(f"✗ Failed to get indicator data: {response.status}")
                return False
                
            result = await response.json()
            data_points = result.get("data", [])
            
            if data_points:
                print(f"✓ Data successfully received in indicator service!")
                print(f"  Found {len(data_points)} data points")
                print(f"  Sample: {data_points[0] if data_points else 'None'}")
                return True
            else:
                print(f"✗ No data found in indicator service")
                return False
                
    async def run_test(self):
        """Run the complete integration test"""
        print("=" * 60)
        print("ATT ORCHESTRATOR INTEGRATION TEST")
        print("=" * 60)
        
        try:
            await self.setup()
            
            # Step 1: Create test resource
            resource_id = await self.create_test_resource()
            
            # Step 2: Create test indicator and associate resource
            indicator_id = await self.create_test_indicator()
            if not indicator_id:
                print("\n✗ Test failed: Could not create indicator")
                return
                
            # Step 3: Send data to data-mq
            test_data = await self.send_data_to_data_mq()
            
            # Wait for data-collector to process
            print("\nWaiting for data-collector to process...")
            await asyncio.sleep(3)
            
            # Step 4: Simulate wrapper-to-resource translation
            # (This should be done automatically by resource-service)
            await self.simulate_wrapper_to_resource_translation()
            
            # Step 5: Verify data in indicator service
            success = await self.verify_indicator_data(indicator_id)
            
            print("\n" + "=" * 60)
            if success:
                print("✓ INTEGRATION TEST PASSED")
                print("\nData flow verified:")
                print("1. External source -> data-mq ✓")
                print("2. data-mq -> data-collector ✓")
                print("3. data-collector -> services-mq ✓")
                print("4. Wrapper ID -> Resource ID translation ✓ (simulated)")
                print("5. Resource data -> indicator-service ✓")
            else:
                print("✗ INTEGRATION TEST FAILED")
                print("\nData did not reach indicator service")
                
            print("=" * 60)
            
        except Exception as e:
            print(f"\n✗ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            await self.teardown()


async def main():
    test = IntegrationTest()
    await test.run_test()


if __name__ == "__main__":
    asyncio.run(main())