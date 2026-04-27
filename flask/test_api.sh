#!/bin/bash

BASE_URL="http://ec2-3-238-190-24.compute-1.amazonaws.com:8000"

echo "========================================="
echo "1. Test root route (expect 200)"
echo "========================================="
curl -w "\nHTTP Status: %{http_code}\n" "$BASE_URL/"

echo ""
echo "========================================="
echo "2. GET all companies (expect 200)"
echo "========================================="
curl -w "\nHTTP Status: %{http_code}\n" "$BASE_URL/companies"

echo ""
echo "========================================="
echo "3. GET a specific company - UPS (expect 200)"
echo "========================================="
curl -w "\nHTTP Status: %{http_code}\n" "$BASE_URL/companies/UPS"

echo ""
echo "========================================="
echo "4. GET company that doesn't exist (expect 404)"
echo "========================================="
curl -w "\nHTTP Status: %{http_code}\n" "$BASE_URL/companies/FakeCompany"

echo ""
echo "========================================="
echo "5. POST a new company (expect 201)"
echo "========================================="
curl -w "\nHTTP Status: %{http_code}\n" -X POST "$BASE_URL/companies" \
     -H "Content-Type: application/json" \
     -d '{"Company": "QuickHaul", "Services": "LTL, Freight", "Hubs": {"Hub": ["Dallas", "Chicago"]}, "Revenue": "$12,000", "HomePage": "https://quickhaul.com", "Logo": "quickhaul.png"}'

echo ""
echo "========================================="
echo "6. POST duplicate company (expect 400)"
echo "========================================="
curl -w "\nHTTP Status: %{http_code}\n" -X POST "$BASE_URL/companies" \
     -H "Content-Type: application/json" \
     -d '{"Company": "QuickHaul", "Services": "LTL"}'

echo ""
echo "========================================="
echo "7. POST with no body (expect 400)"
echo "========================================="
curl -w "\nHTTP Status: %{http_code}\n" -X POST "$BASE_URL/companies" \
     -H "Content-Type: application/json"

echo ""
echo "========================================="
echo "8. PUT update a company (expect 200)"
echo "========================================="
curl -w "\nHTTP Status: %{http_code}\n" -X PUT "$BASE_URL/companies/QuickHaul" \
     -H "Content-Type: application/json" \
     -d '{"Revenue": "$50,000"}'

echo ""
echo "========================================="
echo "9. PUT company that doesn't exist (expect 404)"
echo "========================================="
curl -w "\nHTTP Status: %{http_code}\n" -X PUT "$BASE_URL/companies/FakeCompany" \
     -H "Content-Type: application/json" \
     -d '{"Revenue": "$1"}'

echo ""
echo "========================================="
echo "10. DELETE a company (expect 200)"
echo "========================================="
curl -w "\nHTTP Status: %{http_code}\n" -X DELETE "$BASE_URL/companies/QuickHaul"

echo ""
echo "========================================="
echo "11. DELETE company that doesn't exist (expect 404)"
echo "========================================="
curl -w "\n%{http_code}\n" -X DELETE "$BASE_URL/companies/QuickHaul"

echo ""
echo "========================================="
echo "12. POST with no Company field (expect 400)"
echo "========================================="
curl -w "\n%{http_code}\n" -X POST "$BASE_URL/companies" \
     -H "Content-Type: application/json" \
     -d '{"Services": "LTL, Freight", "Hubs": {"Hub": ["Dallas", "Chicago"]}, "Revenue": "$12,000", "HomePage": "https://quickhaul.com", "Logo": "quickhaul.png"}'
    
echo "========================================="
echo "All tests complete."
echo "========================================="
