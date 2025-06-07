#!/bin/bash
# Build the CloudSim project using Maven management

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/CloudSim" || exit 1

mvn clean install -DskipTests
