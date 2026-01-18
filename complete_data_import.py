#!/usr/bin/env python3
"""
Complete Data Import Script for ATT Platform
Creates domains, indicators, and resources in the correct order with proper MongoDB ObjectIds.
"""

import json
import requests
import sys
import time
from typing import Dict, List, Optional

# Service endpoints
INDICATOR_SERVICE = 'http://localhost:8084'
RESOURCE_SERVICE = 'http://localhost:8083'
DOMAINS_FILE = './user-interface/public/domains.json'

def check_service_health() -> bool:
    """Check if the indicator service is healthy"""
    try:
        response = requests.get(f"{INDICATOR_SERVICE}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Indicator service is healthy")
            return True
    except requests.exceptions.RequestException:
        pass

    print("❌ Indicator service is not responding")
    return False

def create_domain(domain_data: Dict) -> Optional[str]:
    """Create a domain and return its ObjectId"""
    try:
        response = requests.post(
            f"{INDICATOR_SERVICE}/domains/",
            json=domain_data,
            timeout=10
        )

        if response.status_code in [200, 201]:
            domain = response.json()
            domain_id = domain.get('id')
            print(f"✅ Created domain: {domain_data['name']} (ID: {domain_id})")
            return domain_id
        else:
            print(f"❌ Failed to create domain {domain_data['name']}: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating domain {domain_data['name']}: {e}")
        return None

def get_all_indicators_with_pagination() -> List[Dict]:
    """Get all indicators using pagination"""
    all_indicators = []
    skip = 0
    limit = 50  # Maximum allowed by API

    while True:
        try:
            response = requests.get(f"{INDICATOR_SERVICE}/indicators/?skip={skip}&limit={limit}", timeout=10)
            if response.status_code == 200:
                indicators = response.json()
                if not indicators:  # No more indicators
                    break
                all_indicators.extend(indicators)
                skip += limit
                print(f"📄 Fetched {len(indicators)} indicators (total so far: {len(all_indicators)})")
            else:
                print(f"❌ Failed to get indicators: {response.status_code}")
                break
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting indicators: {e}")
            break

    return all_indicators

def get_existing_indicators() -> Dict[str, Dict]:
    """Get existing indicators and create a lookup by name"""
    indicators = get_all_indicators_with_pagination()
    existing_indicators = {}

    for indicator in indicators:
        indicator_name = indicator.get('name')
        if indicator_name:
            existing_indicators[indicator_name] = indicator

    return existing_indicators

def create_indicator(indicator_data: Dict, domain_id: str, subdomain_name: str) -> bool:
    """Create an indicator in the specified domain and subdomain"""
    try:
        response = requests.post(
            f"{INDICATOR_SERVICE}/indicators/{domain_id}/{subdomain_name}/",
            json=indicator_data,
            timeout=10
        )

        if response.status_code in [200, 201]:
            print(f"✅ Created indicator: {indicator_data['name']}")
            return True
        else:
            print(f"❌ Failed to create indicator {indicator_data['name']}: {response.status_code} - {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating indicator {indicator_data['name']}: {e}")
        return False

def create_resource_in_service(indicator_name, indicator_id):
    """Create a resource in the resource-service and return the ID"""
    try:
        # Generate wrapper_id for this indicator
        wrapper_id = f"wrapper_{indicator_id}"
        
        resource_data = {
            "wrapper_id": wrapper_id,
            "name": f"Resource for {indicator_name}",
            "type": "indicator_data"
        }
        
        response = requests.post(
            f"{RESOURCE_SERVICE}/resources/",
            json=resource_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            resource = response.json()
            resource_id = resource.get('id')
            print(f"✅ Created resource in resource-service: {resource_id} for indicator {indicator_name}")
            return resource_id
        else:
            print(f"❌ Failed to create resource in resource-service for {indicator_name}: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating resource in resource-service for {indicator_name}: {e}")
        return None

def add_resource_to_indicator(indicator_id, resource_id):
    """Add a resource to an indicator using the API"""
    try:
        response = requests.post(
            f"{INDICATOR_SERVICE}/indicators/{indicator_id}/resources",
            json={"resource_id": resource_id},
            timeout=10
        )

        if response.status_code in [200, 201]:
            return True
        else:
            print(f"❌ Failed to add resource {resource_id} to indicator {indicator_id}: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error adding resource {resource_id} to indicator {indicator_id}: {e}")
        return False

def add_resources_to_all_indicators():
    """Add resources to all indicators that don't have them"""
    print("🔧 Adding resources to all indicators...")

    # Get all indicators using pagination
    indicators = get_all_indicators_with_pagination()

    if not indicators:
        print("❌ No indicators found")
        return False

    print(f"📊 Found {len(indicators)} total indicators")

    total_indicators = 0
    updated_indicators = 0
    total_resources = 0

    for indicator in indicators:
        indicator_id = indicator.get('id')
        indicator_name = indicator.get('name')
        periodicity = indicator.get('periodicity', 'annual')
        existing_resources = indicator.get('resources', [])

        total_indicators += 1

        # Skip if already has real resources (check if resource exists in resource-service)
        if existing_resources and len(existing_resources) > 0:
            # Check if the resource actually exists in resource-service
            should_create_new = False
            
            if len(existing_resources) == 1 and existing_resources[0] == "string":
                should_create_new = True
                print(f"🔧 Creating resource for indicator: {indicator_name} (replacing dummy 'string' resource)")
            elif len(existing_resources) == 1 and existing_resources[0].endswith('_resource'):
                should_create_new = True
                print(f"🔧 Creating resource for indicator: {indicator_name} (replacing generated resource ID)")
            else:
                # Check if resource exists in resource-service
                existing_resource_id = existing_resources[0]
                try:
                    check_response = requests.get(f"{RESOURCE_SERVICE}/resources/", timeout=5)
                    if check_response.status_code == 200:
                        resources_list = check_response.json()
                        resource_exists = any(r.get('id') == existing_resource_id for r in resources_list)
                        if not resource_exists:
                            should_create_new = True
                            print(f"🔧 Creating resource for indicator: {indicator_name} (resource {existing_resource_id} not found in resource-service)")
                        else:
                            print(f"⏭️  Skipping indicator {indicator_name} (resource {existing_resource_id} exists in resource-service)")
                            continue
                    else:
                        should_create_new = True
                        print(f"🔧 Creating resource for indicator: {indicator_name} (cannot verify resource existence)")
                except:
                    should_create_new = True
                    print(f"🔧 Creating resource for indicator: {indicator_name} (error checking resource-service)")
            
            if not should_create_new:
                continue

        print(f"🔧 Creating resource for indicator: {indicator_name}")

        # Create resource in resource-service first
        resource_id = create_resource_in_service(indicator_name, indicator_id)

        if resource_id:
            # Add the resource to the indicator in indicator-service
            if add_resource_to_indicator(indicator_id, resource_id):
                updated_indicators += 1
                total_resources += 1
                print(f"✅ Added resource {resource_id} to indicator {indicator_name}")
            else:
                print(f"⚠️  Failed to link resource {resource_id} to indicator {indicator_name}")
        else:
            print(f"⚠️  No resource created for indicator {indicator_name}")

        time.sleep(0.2)  # Small delay to avoid overwhelming the service

    print("\n📊 Resource Addition Summary:")
    print(f"   Total indicators processed: {total_indicators}")
    print(f"   Updated indicators: {updated_indicators}")
    print(f"   Total resources created: {total_resources}")

    return updated_indicators > 0

def get_existing_domains() -> List[Dict]:
    """Get existing domains from the API"""
    try:
        response = requests.get(f"{INDICATOR_SERVICE}/domains/", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get domains: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting domains: {e}")
        return []

def import_complete_data() -> bool:
    """Import domains and indicators based on the JSON structure"""

    # Load the domains data
    try:
        with open(DOMAINS_FILE, 'r', encoding='utf-8') as f:
            domains_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error loading domains.json: {e}")
        return False

    if 'domains' not in domains_data:
        print("❌ Invalid domains data structure")
        return False

    # Check existing domains first
    print("\n🔍 Checking existing domains...")
    existing_domains = get_existing_domains()
    existing_domain_names = {domain.get('name') for domain in existing_domains}

    domain_id_map = {}
    for domain in existing_domains:
        domain_id_map[domain.get('name')] = domain.get('id')
        print(f"📋 Found existing domain: {domain.get('name')} (ID: {domain.get('id')})")

    # Create domains
    print("\n🏗️  Creating/processing domains...")
    for domain_json in domains_data['domains']:
        domain_name = domain_json['name']

        if domain_name in existing_domain_names:
            print(f"⏭️  Skipping existing domain: {domain_name}")
            continue

        # Extract subdomains list
        subdomains = [subdomain['name'] for subdomain in domain_json.get('subdomains', [])]

        domain_data = {
            "name": domain_name,
            "color": domain_json.get('DomainColor', '#000000'),
            "image": domain_json.get('DomainImage', ''),
            "subdomains": subdomains
        }

        domain_id = create_domain(domain_data)
        if domain_id:
            domain_id_map[domain_name] = domain_id

        time.sleep(0.2)  # Small delay

    # Get existing indicators to avoid duplicates
    print("\n🔍 Checking existing indicators...")
    existing_indicators = get_existing_indicators()
    print(f"📋 Found {len(existing_indicators)} existing indicators")

    # Create indicators
    print("\n🔄 Creating indicators...")
    total_indicators = 0
    created_indicators = 0
    skipped_indicators = 0

    for domain_json in domains_data['domains']:
        domain_name = domain_json['name']
        domain_id = domain_id_map.get(domain_name)

        if not domain_id:
            print(f"⚠️  Skipping indicators for domain {domain_name} (no domain ID)")
            continue

        print(f"\n📂 Processing domain: {domain_name}")

        for subdomain in domain_json.get('subdomains', []):
            subdomain_name = subdomain['name']
            print(f"  📁 Processing subdomain: {subdomain_name}")

            for indicator_json in subdomain.get('indicators', []):
                total_indicators += 1
                indicator_name = indicator_json['name']

                # Check if indicator already exists
                if indicator_name in existing_indicators:
                    print(f"⏭️  Skipping existing indicator: {indicator_name}")
                    skipped_indicators += 1
                    continue

                # Map JSON structure to API expected format
                indicator_data = {
                    "name": indicator_name,
                    "periodicity": indicator_json['characteristics']['periodicity'],
                    "favourites": indicator_json.get('id', 0) % 5,  # Simulate some favorites
                    "governance": "baseline" in indicator_json.get('categorization', '').lower() or "required" in indicator_json.get('categorization', '').lower(),
                    "description": f"Indicator {indicator_name} from domain {subdomain_name}",
                    "font": indicator_json['characteristics']['source'],
                    "scale": indicator_json['characteristics']['scale']
                }

                if create_indicator(indicator_data, domain_id, subdomain_name):
                    created_indicators += 1

                time.sleep(0.1)  # Small delay to avoid overwhelming the service

    print("\n📊 Import Summary:")
    print(f"   Domains processed: {len(domains_data['domains'])}")
    print(f"   Total indicators processed: {total_indicators}")
    print(f"   Successfully created indicators: {created_indicators}")
    print(f"   Skipped existing indicators: {skipped_indicators}")
    print(f"   Failed indicators: {total_indicators - created_indicators - skipped_indicators}")

    return created_indicators > 0

def test_api_endpoints():
    """Test the various API endpoints after import"""
    print("\n🧪 Testing API endpoints...")

    try:
        # Test general indicators endpoint
        response = requests.get(f"{INDICATOR_SERVICE}/indicators/?limit=5")
        if response.status_code == 200:
            indicators = response.json()
            print(f"✅ General indicators API - Found {len(indicators)} indicators")

        # Test domains endpoint
        response = requests.get(f"{INDICATOR_SERVICE}/domains/")
        if response.status_code == 200:
            domains = response.json()
            print(f"✅ Domains API - Found {len(domains)} domains")

            # Test domain-specific indicators
            if domains:
                first_domain = domains[0]
                domain_id = first_domain.get('id')
                domain_name = first_domain.get('name')

                response = requests.get(f"{INDICATOR_SERVICE}/indicators/domain/{domain_id}?limit=3")
                if response.status_code == 200:
                    domain_indicators = response.json()
                    print(f"✅ Domain-specific API ({domain_name}) - Found {len(domain_indicators)} indicators")

        # Test total indicators count
        all_indicators = get_all_indicators_with_pagination()
        print(f"✅ Total indicators in system: {len(all_indicators)}")

    except Exception as e:
        print(f"❌ API test error: {e}")

def main():
    """Main function to orchestrate the complete data import"""
    print("🚀 Starting Complete ATT Platform Data Import with Resources")
    print("=" * 70)

    # Check service health
    print("\n🔍 Checking service health...")
    if not check_service_health():
        print("❌ Services are not available. Please ensure Docker services are running.")
        sys.exit(1)

    # Import all data
    if import_complete_data():
        print("\n✅ Data import completed successfully!")

        # Add resources to all indicators
        if add_resources_to_all_indicators():
            print("\n✅ Resource addition completed successfully!")
        else:
            print("\n⚠️  Resource addition had issues")

        test_api_endpoints()
        print("\n💡 You can now run the data producer to generate data!")
        print("🌐 Navigate to:")
        print("   - http://localhost/environment")
        print("   - http://localhost/economy")
        print("   - http://localhost/sociaty")
        print("   - http://localhost/favorites")
    else:
        print("\n❌ Data import failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
