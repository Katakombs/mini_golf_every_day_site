# Mini Golf Every Day - Video Update Automation

## Overview

This project uses GitHub Actions to automatically update TikTok videos, NOT server-side automation. The server reads from a local JSON file that is updated by GitHub Actions.

## Video Update Workflow

### 1. GitHub Actions (Recommended)
- **File**: `.github/workflows/update_tiktok_videos.yml`
- **Trigger**: Runs daily at 2 AM UTC
- **Process**:
  1. Installs yt-dlp in the GitHub Actions environment
  2. Fetches latest TikTok videos from @minigolfeveryday
  3. Updates `tiktok_videos.json` with new video metadata
  4. Commits and pushes changes back to the repository

### 2. Server Operation
- **File**: `server.py` (Flask app)
- **Video Source**: Reads from local `tiktok_videos.json` file
- **API Endpoint**: `/api/videos` returns videos from the JSON file
- **No yt-dlp required**: Server never installs or runs yt-dlp

## Files and Their Roles

### Production Files (on server):
- `server.py` - Flask app with video API
- `tiktok_videos.json` - Local video data (updated by GitHub Actions)
- `requirements_blog.txt` - Python dependencies (no yt-dlp)

### Development/GitHub Files:
- `.github/workflows/update_tiktok_videos.yml` - GitHub Actions workflow
- `tiktok_automation.py` - Video fetching logic (GitHub Actions only)
- `fetch_all_videos.py` - Manual video update script
- `add_video.py` - Add single video script

## Important Notes

1. **No Server-Side yt-dlp**: The server never installs or runs yt-dlp
2. **GitHub Actions Handle Updates**: All video metadata is fetched via GitHub Actions
3. **Local JSON File**: Server reads from `tiktok_videos.json` that gets updated by GitHub
4. **Automatic Deployment**: When GitHub Actions updates the JSON file, it automatically deploys to the server

## Troubleshooting

### Videos Not Updating
1. Check GitHub Actions logs in the repository
2. Verify the workflow file exists and is enabled
3. Check if `tiktok_videos.json` was recently updated in the repository

### Server Issues
1. Ensure `tiktok_videos.json` exists on the server
2. Check Flask app logs for JSON reading errors
3. Verify the file permissions allow reading

## Manual Updates (if needed)

If you need to manually update videos:
1. Run `python fetch_all_videos.py` locally (with yt-dlp installed)
2. Commit and push the updated `tiktok_videos.json`
3. Deploy to server (the new JSON file will be used)

## Migration from Server-Side Updates

If you previously had server-side video updates:
1. Remove any cron jobs that run video update scripts
2. Ensure yt-dlp is not installed on the server
3. Verify GitHub Actions workflow is enabled
4. Check that `tiktok_videos.json` is being updated by GitHub Actions