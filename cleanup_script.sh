#!/bin/bash

# Comprehensive System Cleanup Script
# WARNING: This script will permanently delete many files and applications!

echo "=== Starting System Cleanup ==="
echo "Current disk usage:"
df -h /

# Function to show current disk usage
show_disk_usage() {
    echo -e "\n=== Current Disk Usage ==="
    df -h /
    echo -e "\n=== Available Space ==="
    df -h / | grep -E '/$' | awk '{print $4 " available"}'
}

# 1. SNAP PACKAGES CLEANUP
echo -e "\n=== Cleaning Snap Packages ==="
echo "Removing all snap packages..."
snap list --all | while read snapname version revision tracked developer notes; do
    if [ "$snapname" != "Snap" ] && [ "$snapname" != "Name" ]; then
        echo "Removing snap package: $snapname ($revision)"
        snap remove "$snapname" --revision="$revision" 2>/dev/null || echo "Failed to remove $snapname"
    fi
done

# Remove snap directories
echo "Removing snap directories..."
sudo rm -rf /var/lib/snapd/snaps/*
sudo rm -rf /snap/*

# 2. FLATPAK CLEANUP
echo -e "\n=== Cleaning Flatpak Packages ==="
flatpak list
echo "Removing all flatpak installations..."
flatpak uninstall --all -y 2>/dev/null || echo "No flatpak packages found"
flatpak uninstall --unused -y 2>/dev/null || echo "No unused flatpak packages"

# 3. DOCKER CLEANUP
echo -e "\n=== Docker Cleanup ==="
echo "Listing current Docker containers..."
docker ps -a

echo "Keeping only openwebui and localai containers..."
# Stop and remove all containers except openwebui and localai
docker ps -aq --filter "name=openwebui" --filter "name=localai" | xargs -r docker rm -f
docker ps -aq | grep -v "$(docker ps -aq --filter "name=openwebui" --filter "name=localai")" | xargs -r docker rm -f

echo "Pruning Docker resources..."
docker system prune -af --volumes
docker image prune -af
docker volume prune -af
docker network prune -af

# 4. TEMPORARY FILES CLEANUP
echo -e "\n=== Cleaning Temporary Files ==="
echo "Cleaning /tmp..."
sudo find /tmp -type f -atime +7 -delete 2>/dev/null || echo "No old temp files found"

echo "Cleaning system logs..."
sudo journalctl --vacuum-time=7d

echo "Cleaning package cache..."
sudo apt-get clean
sudo apt-get autoremove -y

# 5. USER CACHE CLEANUP
echo -e "\n=== Cleaning User Caches ==="
find ~/.cache -type f -size +50M -delete 2>/dev/null || echo "No large cache files found"
rm -rf ~/.cache/* 2>/dev/null || echo "Cache directory empty"

# 6. FIND AND REMOVE LARGE FILES
echo -e "\n=== Finding and Removing Large Files ==="

# Find files larger than 100MB in home directory
echo "Searching for files larger than 100MB in /home..."
find /home -type f -size +100M -exec ls -lh {} \; 2>/dev/null | sort -k5 -hr > large_files_report.txt
echo "Large files found (see large_files_report.txt for details):"
cat large_files_report.txt

# Remove common large file types that can be safely deleted
echo "Removing common large file types..."
find /home -type f \( -name "*.log" -o -name "*.tmp" -o -name "*.bak" -o -name "*.old" \) -size +10M -delete 2>/dev/null
find /home -type f \( -name "*.zip" -o -name "*.tar" -o -name "*.tar.gz" -o -name "*.rar" \) -size +50M -delete 2>/dev/null

# 7. DOWNLOADS FOLDER CLEANUP
echo -e "\n=== Cleaning Downloads Directory ==="
if [ -d "$HOME/Downloads" ]; then
    echo "Cleaning Downloads folder..."
    find "$HOME/Downloads" -type f -size +50M -exec ls -lh {} \; 2>/dev/null | sort -k5 -hr
    find "$HOME/Downloads" -type f -size +100M -delete 2>/dev/null || echo "No large downloads found"
fi

# 8. THUMBNAIL CACHE CLEANUP
echo -e "\n=== Cleaning Thumbnail Cache ==="
rm -rf ~/.cache/thumbnails/* 2>/dev/null || echo "No thumbnail cache found"

# 9. FIREFOX CACHE (if exists)
echo -e "\n=== Cleaning Firefox Cache ==="
if [ -d "$HOME/.cache/mozilla/firefox" ]; then
    find "$HOME/.cache/mozilla/firefox" -type d -name "*cache*" -exec rm -rf {} + 2>/dev/null || echo "No firefox cache found"
fi

# 10. VS CODE CACHE CLEANUP
echo -e "\n=== Cleaning VS Code Cache ==="
rm -rf ~/.vscode-server/extensions/*/server 2>/dev/null || echo "No VS Code server cache found"

# 11. FINAL DISK USAGE CHECK
show_disk_usage

echo -e "\n=== Cleanup Complete ==="
echo "Summary of actions performed:"
echo "- Removed all snap packages"
echo "- Removed all flatpak installations"
echo "- Pruned Docker resources (keeping only openwebui and localai)"
echo "- Cleaned temporary files and logs"
echo "- Removed large files (>100MB) from home directory"
echo "- Cleaned user caches"
echo "- Cleaned downloads folder"
echo "- Cleaned application caches"

echo -e "\nIMPORTANT: Please review large_files_report.txt to see what files were found."
echo "The cleanup script has completed. Your disk should now have more free space."