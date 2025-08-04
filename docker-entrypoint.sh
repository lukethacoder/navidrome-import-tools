#!/bin/bash
set -e

# Create directories if they don't exist
mkdir -p "$DATA_DIR" "$OUTPUT_DIR" /app/temp

# Set proper permissions for mounted volumes
if [ -w "$DATA_DIR" ]; then
    echo "Data directory is writable: $DATA_DIR"
else
    echo "Warning: Data directory is not writable: $DATA_DIR"
fi

# Check if database exists and is accessible
if [ -f "$DATABASE_PATH" ]; then
    echo "Database found at: $DATABASE_PATH"
    if [ -r "$DATABASE_PATH" ]; then
        echo "Database is readable"
    else
        echo "Warning: Database is not readable"
    fi
else
    echo "Warning: Database not found at: $DATABASE_PATH"
    echo "Make sure to mount your Navidrome database to the data directory"
fi

# Print configuration
echo "Starting Spotify Migration Tool..."
echo "Database path: $DATABASE_PATH"
echo "Data directory: $DATA_DIR"
echo "Output directory: $OUTPUT_DIR"
echo "Redirect URI: ${REDIRECT_URI:-http://localhost:8888/callback}"

# Execute the main command
exec "$@"
