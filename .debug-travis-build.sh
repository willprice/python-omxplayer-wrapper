#!/usr/bin/env bash
set -ex

: "${JOB_ID:="${1:-277217110}"}"
API_TOKEN="$(travis token --no-interactive)"

curl -s -X POST \
     -H "Content-Type: application/json" \
     -H "Accept: application/json" \
     -H "Travis-API-Version: 3" \
     -H "Authorization: token $API_TOKEN" \
     -d '{ "quiet": true }' \
     "https://api.travis-ci.org/job/${JOB_ID}/debug"
