# 🏌️‍♂️ Mini Golf Every Day

A dynamic website showcasing the daily mini golf adventures from the TikTok channel [@minigolfeveryday](https://www.tiktok.com/@minigolfeveryday).

## 🎯 Features

- **178+ TikTok Videos** - Complete archive of daily mini golf content
- **Dynamic Content** - Real-time video counts and statistics
- **Search & Filter** - Find videos by day or keywords
- **Mobile Responsive** - Perfect viewing on all devices
- **Auto-Updates** - Automatically fetches new videos via automation

## 🚀 Live Site

Visit: [https://minigolfevery.day](https://minigolfevery.day)

## 📱 Social Media

- **TikTok**: [@minigolfeveryday](https://www.tiktok.com/@minigolfeveryday)
- **Instagram**: [@mini.golf.every.day](https://www.instagram.com/mini.golf.every.day/)

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript, Tailwind CSS
- **Backend**: Python, Flask
- **Data**: JSON-based video database
- **Automation**: Python scripts with cron jobs
- **Hosting**: Shared hosting with WSGI support

## 📊 Project Stats

- **Days Running**: 178+ days
- **Videos Created**: 178+ TikTok videos
- **Started**: January 1, 2025
- **Database Size**: ~46KB JSON file

## 🔧 Development

### Prerequisites
- Python 3.11+
- pip package manager

### Setup
```bash
# Clone repository
git clone https://github.com/yourusername/mini_golf_every_day_site.git
cd mini_golf_every_day_site

# Install dependencies
pip install -r requirements.txt

# Run local development server
python3 flask_app.py
```

### File Structure
```
├── index.html              # Dynamic homepage
├── watch.html              # Video gallery with search
├── about.html              # About page with live stats
├── flask_app.py            # Flask API server
├── tiktok_automation.py    # Core automation logic
├── tiktok_videos.json      # Video database (178+ videos)
├── cron_update.py          # Auto-update script
├── requirements.txt        # Python dependencies
├── css/                    # Stylesheets
├── images/                 # Logos and assets
└── js/                     # JavaScript files
```

## 🤖 Automation

The site automatically updates every 6 hours via:
1. **Cron Job** runs `cron_update.py`
2. **Fetches** new TikTok videos
3. **Updates** JSON database
4. **Maintains** complete video archive

## 🎨 Design

- **Brand Colors**: Green (#059669) and Yellow (#FDE047)
- **Typography**: Fredoka (headings), Inter (body)
- **Layout**: Mobile-first responsive design
- **Icons**: Custom SVG logo and social media icons

## 📝 License

This project is personal/educational. TikTok content belongs to [@minigolfeveryday](https://www.tiktok.com/@minigolfeveryday).

## 🎉 About

Started as a New Year's resolution to play mini golf every single day in 2025. What began as a simple daily challenge has grown into a celebration of family, fun, and consistency - one putt at a time.

**Created with ❤️ for MJ**
