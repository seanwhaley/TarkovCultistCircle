#!/bin/bash

# Navigate to static directory
cd ../src/static

# Install dependencies
npm install

# Build CSS
npm run build

# Notify completion
echo "Material Design dependencies installed and built successfully"