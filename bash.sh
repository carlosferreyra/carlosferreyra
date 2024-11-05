#!/bin/bash

GITHUB_TOKEN="your_github_token_here"
GITHUB_API_URL="https://api.github.com"
GITHUB_TOKEN="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"

echo "{}" > social_previews_orgs.json
repo="GestionTUP"
owner="Seminario-Integrador-2024"
query="{\"query\":\"query { repository(owner: \\\"$owner\\\", name: \\\"$repo\\\") { openGraphImageUrl } }\"}"

# Log the query for debugging
echo "Query: $query"

echo "Running query for repo: $repo"
response=$(curl -H "Authorization: bearer $GITHUB_TOKEN" -H "Content-Type: application/json" -X POST -d "$query" $GITHUB_API_URL/graphql)

# Log the response for debugging
echo "Response: $response"

# Check if the response contains errors
errors=$(echo $response | jq -r ".errors")
if [ "$errors" != "null" ]; then
  echo "Error in response: $errors"
  exit 1
fi

# Extract the image URL from the response
img_url=$(echo $response | jq -r ".data.repository.openGraphImageUrl")

# Log the image URL for debugging
echo "Image URL: $img_url"

# Check if the image URL is null or empty
if [ "$img_url" == "null" ] || [ -z "$img_url" ]; then
  echo "No image URL found for repo: $repo"
  exit 1
fi

# Update the JSON file with the image URL
jq --arg repo "$repo" --arg img_url "$img_url" '.[$repo] = $img_url' social_previews_orgs.json > tmp.json && mv tmp.json social_previews_orgs.json

# Log the final JSON content for debugging
cat social_previews_orgs.json