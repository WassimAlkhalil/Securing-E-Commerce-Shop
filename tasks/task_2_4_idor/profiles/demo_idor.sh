#!/bin/bash
# Author: Wassim Alkhalil
# Demo script: IDOR vulnerability before and after fix
# Shows the scraper working on vulnerable version, then failing on fixed version

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Use Python from the virtual environment
PYTHON="${SCRIPT_DIR}/../../../.venv/bin/python3"

BASE_URL="${1:-http://localhost:5000}"
START_ID="${2:-1}"
END_ID="${3:-200}"

# Create demo directory in the project root
DEMO_DIR="${SCRIPT_DIR}/../../../idor_demo"
mkdir -p "$DEMO_DIR"

# ===== STEP 1: Demonstrate VULNERABLE version =====
echo "[1/5] Switching to VULNERABLE branch (task-2-4-vulnerable)..."
git checkout task-2-4-vulnerable
echo "✓ On vulnerable branch"
echo ""

echo "[2/5] Restarting Docker container to apply changes..."
docker-compose restart
sleep 3
echo "✓ Server restarted"
echo ""

echo "[3/5] Running scraper on VULNERABLE version..."
echo "      This should harvest user data freely (no access control)..."
"$PYTHON" "$SCRIPT_DIR/idor_scraper.py" "$BASE_URL" "$START_ID" "$END_ID" "$DEMO_DIR/vulnerable_profiles.csv"
if [ -f "$DEMO_DIR/vulnerable_profiles.csv" ]; then
    wc -l "$DEMO_DIR/vulnerable_profiles.csv"
    echo "✓ Harvested data"
    echo ""
    echo "   Sample of harvested data:"
    head -5 "$DEMO_DIR/vulnerable_profiles.csv" | sed 's/^/   /'
else
    echo "✗ No profiles harvested - check if server is running"
fi
echo ""

# ===== STEP 2: Demonstrate FIXED version =====
echo "[4/5] Switching to FIXED branch (phase-2)..."
git checkout phase-2
echo "✓ On fixed branch"
echo ""

echo "[5/5] Restarting Docker container to apply changes..."
docker-compose restart
sleep 3
echo "✓ Server restarted"
echo ""

echo "Running scraper on FIXED version..."
echo "    This should fail with 403 Forbidden (access control enforced)..."
"$PYTHON" "$SCRIPT_DIR/idor_scraper.py" "$BASE_URL" "$START_ID" "$END_ID" "$DEMO_DIR/fixed_profiles.csv"
if [ -f "$DEMO_DIR/fixed_profiles.csv" ]; then
    wc -l "$DEMO_DIR/fixed_profiles.csv"
    echo "✓ Output saved"
else
    echo "✓ No profiles harvested (access denied as expected)"
fi
echo ""

# ===== Summary =====
echo "=========================================="
echo "DEMO COMPLETE"
echo "=========================================="
echo ""
echo "Results Summary:"
echo "  Vulnerable profiles (CSV):  $DEMO_DIR/vulnerable_profiles.csv"
echo "  Fixed profiles (CSV):       $DEMO_DIR/fixed_profiles.csv"
echo ""
echo "To view the harvested data:"
echo "  cat $DEMO_DIR/vulnerable_profiles.csv"
echo "  cat $DEMO_DIR/fixed_profiles.csv"
echo ""

