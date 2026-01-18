#!/bin/bash

# Test Async Wrapper Creation with Águas Seguras CSV
# This script tests the complete async wrapper creation flow

set -e  # Exit on any error

BASE_URL="http://localhost"
# Try direct access to resource service for testing
RESOURCE_URL="http://localhost:8080"
CSV_FILE="$HOME/Transferências/aguas_seguras.csv"

echo "🧪 Testing Async Wrapper Creation with Águas Seguras CSV"
echo "=================================================="

# Check if CSV file exists
if [ ! -f "$CSV_FILE" ]; then
    echo "❌ Error: CSV file not found at $CSV_FILE"
    exit 1
fi

echo "✅ CSV file found: $CSV_FILE"

# Step 1: Create a domain first (if it doesn't exist)
echo ""
echo "📂 Step 1: Creating Environment domain..."
DOMAIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/domains" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Environment",
    "color": "#22c55e",
    "image": "environment-icon.png",
    "subdomains": ["Water Quality", "Air Quality", "Biodiversity"]
  }' || echo '{"error": "Domain might already exist"}')

echo "Domain creation response: $DOMAIN_RESPONSE"

# Step 2: Upload the CSV file
echo ""
echo "📤 Step 2: Uploading CSV file..."
FILE_UPLOAD_RESPONSE=$(curl -s -X POST "$RESOURCE_URL/wrappers/files/upload" \
  -F "file=@$CSV_FILE")

echo "File upload response: $FILE_UPLOAD_RESPONSE"

# Extract file_id from response (assuming JSON response with file_id field)
FILE_ID=$(echo "$FILE_UPLOAD_RESPONSE" | grep -o '"file_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$FILE_ID" ]; then
    echo "❌ Error: Could not extract file_id from upload response"
    echo "Upload response: $FILE_UPLOAD_RESPONSE"
    exit 1
fi

echo "✅ File uploaded successfully with ID: $FILE_ID"

# Step 3: Create async wrapper
echo ""
echo "🚀 Step 3: Creating async wrapper..."
WRAPPER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/resources/wrappers/async/create" \
  -H "Content-Type: application/json" \
  -d "{
    \"metadata\": {
      \"name\": \"Percentage of Safe Water Supply\",
      \"domain\": \"Environment\",
      \"subdomain\": \"Water Quality\",
      \"description\": \"Annual percentage of population with access to safe water supply in Portugal\",
      \"unit\": \"%\",
      \"source\": \"INE - Instituto Nacional de Estatística\",
      \"scale\": \"National\",
      \"governance_indicator\": false,
      \"periodicity\": \"Annual\"
    },
    \"source_config\": {
      \"source_type\": \"CSV\",
      \"file_id\": \"$FILE_ID\",
      \"auth_config\": {}
    },
    \"auto_create_resource\": true
  }")

echo "Wrapper creation response: $WRAPPER_RESPONSE"

# Extract wrapper_id from response
WRAPPER_ID=$(echo "$WRAPPER_RESPONSE" | grep -o '"wrapper_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$WRAPPER_ID" ]; then
    echo "❌ Error: Could not extract wrapper_id from wrapper response"
    echo "Wrapper response: $WRAPPER_RESPONSE"
    exit 1
fi

echo "✅ Async wrapper created with ID: $WRAPPER_ID"

# Step 4: Monitor wrapper progress
echo ""
echo "⏳ Step 4: Monitoring wrapper progress..."
echo "Wrapper ID: $WRAPPER_ID"

MAX_ATTEMPTS=30
ATTEMPT=1
SLEEP_INTERVAL=5

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo ""
    echo "🔍 Attempt $ATTEMPT/$MAX_ATTEMPTS - Checking wrapper status..."
    
    STATUS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/resources/wrappers/async/status/$WRAPPER_ID")
    echo "Status response: $STATUS_RESPONSE"
    
    # Extract status from response
    STATUS=$(echo "$STATUS_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    
    echo "Current status: $STATUS"
    
    case "$STATUS" in
        "completed")
            echo "🎉 Wrapper completed successfully!"
            
            # Extract resource_id
            RESOURCE_ID=$(echo "$STATUS_RESPONSE" | grep -o '"resource_id":"[^"]*"' | cut -d'"' -f4)
            
            echo "✅ Wrapper ID: $WRAPPER_ID"
            echo "✅ Resource ID: $RESOURCE_ID"
            
            # Test getting the wrapper details
            echo ""
            echo "📋 Step 5: Getting wrapper details..."
            WRAPPER_DETAILS=$(curl -s -X GET "$BASE_URL/api/resources/wrappers/$WRAPPER_ID")
            echo "Wrapper details: $WRAPPER_DETAILS"
            
            # Test getting the resource details
            echo ""
            echo "📋 Step 6: Getting resource details..."
            RESOURCE_DETAILS=$(curl -s -X GET "$BASE_URL/api/resources/$RESOURCE_ID")
            echo "Resource details: $RESOURCE_DETAILS"
            
            echo ""
            echo "🎊 SUCCESS! Async wrapper creation completed successfully!"
            echo "=================================================="
            echo "Summary:"
            echo "- Task ID: $TASK_ID"
            echo "- Wrapper ID: $WRAPPER_ID"
            echo "- Resource ID: $RESOURCE_ID"
            echo "- CSV File: $CSV_FILE"
            echo "=================================================="
            
            exit 0
            ;;
        "error")
            echo "❌ Wrapper failed!"
            ERROR_MSG=$(echo "$STATUS_RESPONSE" | grep -o '"error_message":"[^"]*"' | cut -d'"' -f4)
            echo "Error: $ERROR_MSG"
            exit 1
            ;;
        "pending"|"generating"|"creating_resource"|"executing")
            echo "⏳ Wrapper in progress (status: $STATUS)... waiting $SLEEP_INTERVAL seconds"
            sleep $SLEEP_INTERVAL
            ;;
        *)
            echo "❓ Unknown status: $STATUS"
            ;;
    esac
    
    ATTEMPT=$((ATTEMPT + 1))
done

echo ""
echo "⏰ Timeout: Wrapper did not complete within expected time"
echo "Final status response: $STATUS_RESPONSE"
exit 1