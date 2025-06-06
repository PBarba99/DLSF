#!/bin/bash
# Run the DeepRL simulation with proper classpath

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/CloudSim" || exit 1

mvn dependency:build-classpath -Dmdep.outputFile=/tmp/classpath.txt

java -cp "modules/cloudsim-examples/target/classes:modules/cloudsim/target/classes:$(cat /tmp/classpath.txt)" \
  org.cloudbus.cloudsim.examples.power.DeepRL.DeepRLRunner
