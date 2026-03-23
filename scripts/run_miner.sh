#!/bin/bash
echo "🚀 Starting Enigma Machine Miner on SN63..."

# Make sure dependencies are installed
pip install -e . --quiet

# Run the real miner
python -m neurons.miner \
  --netuid 63 \
  --subtensor.network finney \
  --wallet.name default \
  --wallet.hotkey default \
  --axon.port 8091
