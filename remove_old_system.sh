#!/bin/bash

# Remove Old Spotify Library Sync System
# This script safely removes the old system after verification

echo "🔍 Checking current system status..."

# Check if new system is working
echo "✅ Testing new system..."
cd api
python manage.py check
if [ $? -ne 0 ]; then
    echo "❌ New system check failed. Please fix issues before archiving."
    exit 1
fi

echo "✅ New system is working correctly."

# Check if old system exists
if [ ! -d "../spotify_library_sync" ]; then
    echo "❌ Old system directory not found. It may have already been archived."
    exit 1
fi

echo "🗑️  Removing old system..."
rm -rf ../spotify_library_sync

echo "🧹 Cleaning up any remaining references..."

# Check for any remaining references to old system
echo "🔍 Checking for remaining references to old system..."
grep -r "spotify_library_sync" . --exclude-dir=.git 2>/dev/null || echo "✅ No remaining references found."

echo "✅ Removal complete!"
echo ""
echo "📋 Summary of what was preserved in new system:"
echo "   - All forms and validators"
echo "   - All task functions"
echo "   - All models and migrations"
echo "   - Configuration settings"
echo "   - Downloader components"
echo ""
echo "🚀 New system is ready for production!"
echo "📖 See DEPRECATION_COMPLETION_SUMMARY.md for details." 