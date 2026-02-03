#!/bin/bash
# Script to run ratio.py with various configuration options
# Edit the parameters below to customize the analysis

# Base configuration
HIST_NAME="EventCutFlow"
GLUINO_MASS=1800
NEUTRALINO_MASS=1300
DECAY_TYPE="lightDecay"
ERA="130X_mcRun3_2023_realistic_postBPix_v2"

# Comparison parameters
CTAU1="stable"
CTAU2="10000mm"

# Plot options
LOG_SCALE="--log-scale"  # Set to "--log-scale" to enable logarithmic y-axis
Y_RANGE="3,0.1,0.01,0.001"  # Customize y-axis ticks; default matches script default
OUTPUT_NAME=""  # Leave empty for auto-generated names

echo "Running ratio.py with the following configuration:"
echo "  Histogram: $HIST_NAME"
echo "  Gluino mass: $GLUINO_MASS GeV"
echo "  Neutralino mass: $NEUTRALINO_MASS GeV"
echo "  Decay type: $DECAY_TYPE"
echo "  ctau comparison: $CTAU1 vs $CTAU2"
echo "  Log scale: $([ -z "$LOG_SCALE" ] && echo "disabled" || echo "enabled")"
echo "  Y range: ${Y_RANGE}"
echo ""

# Construct the command
CMD="python3 ratio.py"
CMD="$CMD --hist-name \"$HIST_NAME\""
CMD="$CMD --gluino-mass $GLUINO_MASS"
CMD="$CMD --neutralino-mass $NEUTRALINO_MASS"
CMD="$CMD --ctau1 \"$CTAU1\""
CMD="$CMD --ctau2 \"$CTAU2\""
CMD="$CMD --decay-type \"$DECAY_TYPE\""
CMD="$CMD --era \"$ERA\""

if [ -n "$LOG_SCALE" ]; then
    CMD="$CMD $LOG_SCALE"
fi

if [ -n "$Y_RANGE" ]; then
    CMD="$CMD --y-range \"$Y_RANGE\""
fi

if [ -n "$OUTPUT_NAME" ]; then
    CMD="$CMD --output-name \"$OUTPUT_NAME\""
fi

echo "Executing: $CMD"
echo ""

# Execute the command
eval $CMD

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "Ratio plot generation completed successfully!"
    echo "Check the plots/ directory for the output PDF."
else
    echo ""
    echo "Error: Ratio plot generation failed!"
    exit 1
fi
