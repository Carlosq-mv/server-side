#!/bin/bash
# ============================================================================
# Test script for Trucking Company API
# Tests all endpoints + every validation path, then cleans up after itself.
#
# Usage:
#   ./test_api.sh                                    # uses default URL
#   ./test_api.sh http://localhost:8000              # custom URL
#   BASE_URL=http://my-server.com:8000 ./test_api.sh # via env var
# ============================================================================

# Base URL — override by passing as first arg or setting BASE_URL env var
BASE_URL=""

# Test company name (used for create/update/delete cycle)
TEST_COMPANY="TestCompany_$(date +%s)"  # timestamp keeps it unique per run

# Counters
PASS=0
FAIL=0
TOTAL=0

# Colors (only if terminal supports them)
if [ -t 1 ]; then
    GREEN=$'\033[0;32m'
    RED=$'\033[0;31m'
    YELLOW=$'\033[1;33m'
    BLUE=$'\033[0;34m'
    BOLD=$'\033[1m'
    RESET=$'\033[0m'
else
    GREEN='' RED='' YELLOW='' BLUE='' BOLD='' RESET=''
fi

# ----------------------------------------------------------------------------
# Helper: run a test and check status code
# Usage: run_test "description" expected_status curl_args...
# ----------------------------------------------------------------------------
run_test() {
    local description="$1"
    local expected="$2"
    shift 2

    TOTAL=$((TOTAL + 1))

    # -s silent, -o /dev/null discard body, -w write status code only
    local actual
    actual=$(curl -s -o /dev/null -w "%{http_code}" "$@")

    if [ "$actual" = "$expected" ]; then
        printf "${GREEN}✓${RESET} %-55s ${GREEN}[%s]${RESET}\n" "$description" "$actual"
        PASS=$((PASS + 1))
    else
        printf "${RED}✗${RESET} %-55s ${RED}[got %s, expected %s]${RESET}\n" "$description" "$actual" "$expected"
        FAIL=$((FAIL + 1))
    fi
}

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
echo ""
echo "${BOLD}════════════════════════════════════════════════════════════${RESET}"
echo "${BOLD} Trucking API Test Suite${RESET}"
echo "${BOLD}════════════════════════════════════════════════════════════${RESET}"
echo " Target:   $BASE_URL"
echo " Test co:  $TEST_COMPANY"
echo ""

# ----------------------------------------------------------------------------
# SECTION 1: Basic GET endpoints
# ----------------------------------------------------------------------------
echo "${BLUE}${BOLD}── GET endpoints ──${RESET}"

run_test "GET / (index page)" 200 \
    "$BASE_URL/"

run_test "GET /companies (list all)" 200 \
    "$BASE_URL/companies"

run_test "GET /companies/UPS (existing)" 200 \
    "$BASE_URL/companies/UPS"

run_test "GET /companies/FakeCompany (404)" 404 \
    "$BASE_URL/companies/FakeCompany"

# ----------------------------------------------------------------------------
# SECTION 2: POST validation errors
# ----------------------------------------------------------------------------
echo ""
echo "${BLUE}${BOLD}── POST validation (all 400) ──${RESET}"

run_test "POST no body" 400 \
    -X POST "$BASE_URL/companies" \
    -H "Content-Type: application/json"

run_test "POST empty JSON object {}" 400 \
    -X POST "$BASE_URL/companies" \
    -H "Content-Type: application/json" \
    -d '{}'

run_test "POST malformed JSON" 400 \
    -X POST "$BASE_URL/companies" \
    -H "Content-Type: application/json" \
    -d '{not valid'

run_test "POST array instead of object" 400 \
    -X POST "$BASE_URL/companies" \
    -H "Content-Type: application/json" \
    -d '["a","b"]'

run_test "POST string instead of object" 400 \
    -X POST "$BASE_URL/companies" \
    -H "Content-Type: application/json" \
    -d '"hello"'

run_test "POST extra field" 400 \
    -X POST "$BASE_URL/companies" \
    -H "Content-Type: application/json" \
    -d '{"Company":"X","Services":"Y","Hubs":{"NA":"NYC"},"Revenue":"$1","HomePage":"https://x.com","Logo":"x.png","Hacker":"extra"}'

run_test "POST missing Company field" 400 \
    -X POST "$BASE_URL/companies" \
    -H "Content-Type: application/json" \
    -d '{"Services":"Y","Hubs":{"NA":"NYC"},"Revenue":"$1","HomePage":"https://x.com","Logo":"x.png"}'

run_test "POST missing multiple fields" 400 \
    -X POST "$BASE_URL/companies" \
    -H "Content-Type: application/json" \
    -d '{"Company":"X","Services":"Y"}'

run_test "POST empty string field" 400 \
    -X POST "$BASE_URL/companies" \
    -H "Content-Type: application/json" \
    -d '{"Company":"","Services":"Y","Hubs":{"NA":"NYC"},"Revenue":"$1","HomePage":"https://x.com","Logo":"x.png"}'

run_test "POST null field value" 400 \
    -X POST "$BASE_URL/companies" \
    -H "Content-Type: application/json" \
    -d '{"Company":"X","Services":null,"Hubs":{"NA":"NYC"},"Revenue":"$1","HomePage":"https://x.com","Logo":"x.png"}'

run_test "POST empty Hubs dict" 400 \
    -X POST "$BASE_URL/companies" \
    -H "Content-Type: application/json" \
    -d '{"Company":"X","Services":"Y","Hubs":{},"Revenue":"$1","HomePage":"https://x.com","Logo":"x.png"}'

run_test "POST Hubs as string (not dict)" 400 \
    -X POST "$BASE_URL/companies" \
    -H "Content-Type: application/json" \
    -d '{"Company":"X","Services":"Y","Hubs":"NYC","Revenue":"$1","HomePage":"https://x.com","Logo":"x.png"}'

run_test "POST Hubs as array (not dict)" 400 \
    -X POST "$BASE_URL/companies" \
    -H "Content-Type: application/json" \
    -d '{"Company":"X","Services":"Y","Hubs":["NYC","LA"],"Revenue":"$1","HomePage":"https://x.com","Logo":"x.png"}'

# ----------------------------------------------------------------------------
# SECTION 3: POST success + duplicate detection
# ----------------------------------------------------------------------------
echo ""
echo "${BLUE}${BOLD}── POST create + duplicate ──${RESET}"

VALID_PAYLOAD=$(cat <<EOF
{
  "Company": "$TEST_COMPANY",
  "Services": "LTL, Freight",
  "Hubs": {"Hub": ["Dallas", "Chicago"]},
  "Revenue": "\$12,000",
  "HomePage": "https://test.com",
  "Logo": "test.png"
}
EOF
)

run_test "POST valid payload (201)" 201 \
    -X POST "$BASE_URL/companies" \
    -H "Content-Type: application/json" \
    -d "$VALID_PAYLOAD"

run_test "POST duplicate (now actually duplicate)" 400 \
    -X POST "$BASE_URL/companies" \
    -H "Content-Type: application/json" \
    -d "$VALID_PAYLOAD"

run_test "GET newly created company" 200 \
    "$BASE_URL/companies/$TEST_COMPANY"

# ----------------------------------------------------------------------------
# SECTION 4: PUT validation + success
# ----------------------------------------------------------------------------
echo ""
echo "${BLUE}${BOLD}── PUT update ──${RESET}"

run_test "PUT no body" 400 \
    -X PUT "$BASE_URL/companies/$TEST_COMPANY" \
    -H "Content-Type: application/json"

run_test "PUT empty {}" 400 \
    -X PUT "$BASE_URL/companies/$TEST_COMPANY" \
    -H "Content-Type: application/json" \
    -d '{}'

run_test "PUT array body" 400 \
    -X PUT "$BASE_URL/companies/$TEST_COMPANY" \
    -H "Content-Type: application/json" \
    -d '["a","b"]'

run_test "PUT empty value" 400 \
    -X PUT "$BASE_URL/companies/$TEST_COMPANY" \
    -H "Content-Type: application/json" \
    -d '{"Services":""}'

run_test "PUT Hubs as string" 400 \
    -X PUT "$BASE_URL/companies/$TEST_COMPANY" \
    -H "Content-Type: application/json" \
    -d '{"Hubs":"NYC"}'

run_test "PUT nonexistent company (404)" 404 \
    -X PUT "$BASE_URL/companies/FakeCompany_99999" \
    -H "Content-Type: application/json" \
    -d '{"Revenue":"100"}'

run_test "PUT valid partial update" 200 \
    -X PUT "$BASE_URL/companies/$TEST_COMPANY" \
    -H "Content-Type: application/json" \
    -d '{"Revenue":"$50,000"}'

# ----------------------------------------------------------------------------
# SECTION 5: DELETE
# ----------------------------------------------------------------------------
echo ""
echo "${BLUE}${BOLD}── DELETE ──${RESET}"

run_test "DELETE nonexistent company (404)" 404 \
    -X DELETE "$BASE_URL/companies/FakeCompany_99999"

run_test "DELETE created test company (cleanup)" 200 \
    -X DELETE "$BASE_URL/companies/$TEST_COMPANY"

run_test "GET deleted company should now 404" 404 \
    "$BASE_URL/companies/$TEST_COMPANY"

run_test "DELETE same company again (now 404)" 404 \
    -X DELETE "$BASE_URL/companies/$TEST_COMPANY"

# ----------------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------------
echo ""
echo "${BOLD}════════════════════════════════════════════════════════════${RESET}"
if [ "$FAIL" -eq 0 ]; then
    echo "${GREEN}${BOLD} All $TOTAL tests passed${RESET}"
else
    echo "${BOLD} Results: ${GREEN}$PASS passed${RESET}${BOLD}, ${RED}$FAIL failed${RESET}${BOLD} (out of $TOTAL)${RESET}"
fi
echo "${BOLD}════════════════════════════════════════════════════════════${RESET}"
echo ""

# ----------------------------------------------------------------------------
# Final cleanup safety net — make sure test company is gone even if a test
# above failed mid-way. Silent: this is just insurance.
# ----------------------------------------------------------------------------
curl -s -o /dev/null -X DELETE "$BASE_URL/companies/$TEST_COMPANY" 2>/dev/null

# Exit non-zero if any tests failed (useful for CI)
[ "$FAIL" -eq 0 ]
