#!/bin/bash

# Script to run 2DHistogram.py with configurable parameters
# Author: Auto-generated script for HSCP analysis

# Default parameters
HIST_NAME="EventCutFlow"
GLUINO_MASS=1800
NEUTRALINO_MASS=1300
#CTAUS="0p1mm,1mm,10mm,100mm,1000mm,10000mm"
CTAUS="0p1mm,10000mm"
DECAY_TYPES="lightDecay"
#DECAY_TYPES="both"
ERA="130X_mcRun3_2023_realistic_postBPix_v2"
OUTPUT_NAME=""
LOG_SCALE_Z="--log-scale-z"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print usage
usage() {
    echo -e "${BLUE}Usage: $0 [options]${NC}"
    echo ""
    echo "Options:"
    echo "  -h, --hist-name HIST_NAME          Histogram name (default: $HIST_NAME)"
    echo "  -g, --gluino-mass MASS             Gluino mass in GeV (default: $GLUINO_MASS)"
    echo "  -n, --neutralino-mass MASS         Neutralino mass in GeV (default: $NEUTRALINO_MASS)"
    echo "  -c, --ctaus CTAU_LIST              Comma-separated ctau values (default: $CTAUS)"
    echo "  -d, --decay-types TYPE             Decay types: lightDecay, heavyDecay, or both (default: $DECAY_TYPES)"
    echo "  -e, --era ERA                      Data-taking era (default: $ERA)"
    echo "  -o, --output-name NAME             Custom output filename"
    echo "  -l, --linear-scale-z               Use linear scale for z-axis (default: logarithmic)"
    echo "  --help                             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                                    # Use all defaults"
    echo "  $0 -h \"HSCPDeDxInfo_mass\" -d both                    # Plot mass histogram for both decay types"
    echo "  $0 -c \"0p1mm,10mm,1000mm\" -g 2000 -n 1500           # Custom ctaus and masses"
    echo "  $0 -d both -l                                        # Both decay types with linear z-scale"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--hist-name)
            HIST_NAME="$2"
            shift 2
            ;;
        -g|--gluino-mass)
            GLUINO_MASS="$2"
            shift 2
            ;;
        -n|--neutralino-mass)
            NEUTRALINO_MASS="$2"
            shift 2
            ;;
        -c|--ctaus)
            CTAUS="$2"
            shift 2
            ;;
        -d|--decay-types)
            DECAY_TYPES="$2"
            shift 2
            ;;
        -e|--era)
            ERA="$2"
            shift 2
            ;;
        -o|--output-name)
            OUTPUT_NAME="$2"
            shift 2
            ;;
        -l|--linear-scale-z)
            LOG_SCALE_Z="--linear-scale-z"
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            usage
            exit 1
            ;;
    esac
done

# Check if Python script exists
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/2DHistogram.py"

if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo -e "${RED}Error: 2DHistogram.py not found at $PYTHON_SCRIPT${NC}"
    exit 1
fi

# Print configuration
echo -e "${BLUE}===========================================${NC}"
echo -e "${BLUE}    Running 2D Histogram Generation${NC}"
echo -e "${BLUE}===========================================${NC}"
echo -e "${YELLOW}Configuration:${NC}"
echo "  Histogram name:    $HIST_NAME"
echo "  Gluino mass:       $GLUINO_MASS GeV"
echo "  Neutralino mass:   $NEUTRALINO_MASS GeV"
echo "  Decay types:       $DECAY_TYPES"
echo "  ctau values:       $CTAUS"
echo "  Era:               $ERA"
echo "  Z-axis scale:      $(if [[ $LOG_SCALE_Z == *"log"* ]]; then echo "Logarithmic"; else echo "Linear"; fi)"
if [[ -n "$OUTPUT_NAME" ]]; then
    echo "  Output name:       $OUTPUT_NAME"
fi
echo ""

# Build command
CMD="python3 \"$PYTHON_SCRIPT\""
CMD="$CMD --hist-name \"$HIST_NAME\""
CMD="$CMD --gluino-mass $GLUINO_MASS"
CMD="$CMD --neutralino-mass $NEUTRALINO_MASS"
CMD="$CMD --ctaus \"$CTAUS\""
CMD="$CMD --decay-types \"$DECAY_TYPES\""
CMD="$CMD --era \"$ERA\""
CMD="$CMD $LOG_SCALE_Z"

if [[ -n "$OUTPUT_NAME" ]]; then
    CMD="$CMD --output-name \"$OUTPUT_NAME\""
fi

# Execute command
echo -e "${YELLOW}Running command:${NC}"
echo "$CMD"
echo ""

# Check if we're in the correct environment
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 not found. Please ensure Python 3 is installed and in your PATH.${NC}"
    exit 1
fi

# Run the command
eval $CMD
exit_code=$?

# Check execution result
if [[ $exit_code -eq 0 ]]; then
    echo ""
    echo -e "${GREEN}✓ 2D histogram generation completed successfully!${NC}"
    echo -e "${GREEN}✓ Check the plots/ directory for output files.${NC}"
else
    echo ""
    echo -e "${RED}✗ 2D histogram generation failed with exit code $exit_code${NC}"
    exit $exit_code
fi