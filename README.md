# Website Monitor Dashboard made with Claude 4

A clean, professional website uptime monitoring dashboard built with HTML, CSS, and JavaScript. Monitor multiple websites, track their uptime, response times, and get real-time status updates.

## Features

- **Real-time Monitoring**: Auto-refreshes every 30 seconds
- **Professional Interface**: Clean, modern design suitable for business environments
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Search Functionality**: Quickly find specific websites in your monitoring list
- **Export Data**: Download monitoring reports as JSON files
- **Keyboard Shortcuts**: Efficient navigation with hotkeys
- **Status Indicators**: Clear visual indicators for website status (Online, Offline, Warning)
- **Performance Metrics**: Track uptime percentage, response times, and status codes

## Demo

The dashboard includes sample data for demonstration purposes. You can see it in action immediately by opening the HTML file in your browser.

## Quick Start

1. **Download the HTML file**
2. **Open in your browser** - The demo will work immediately with sample data
3. **For live monitoring**: Configure your API endpoint (see Configuration section)

## Configuration

### Using Demo Data (Default)
The dashboard comes pre-configured with demo data. No setup required!

```javascript
const CONFIG = {
    useDemoData: true,
    refreshInterval: 30000, // 30 seconds
    searchDelay: 300 // 300ms delay for search
};
```

### Using Live API Data
To connect to your own monitoring API:

```javascript
const CONFIG = {
    apiBaseUrl: 'http://localhost:5000/api', // Your API URL
    useDemoData: false,
    refreshInterval: 30000,
    searchDelay: 300
};
```

### API Requirements
Your API should provide a `/websites` endpoint that returns JSON in this format:

```json
[
    {
        "id": 1,
        "name": "Website Name",
        "url": "https://example.com",
        "status": "up", // "up", "down", "warning", "unknown"
        "status_code": 200,
        "response_time": 0.15,
        "uptime_percentage": 99.9,
        "total_checks": 1440,
        "last_checked": "2025-08-02T10:30:00Z",
        "error_message": null
    }
]
```

## Usage

### Basic Operations
- **Refresh Data**: Click the "Refresh" button or press `Ctrl+R`
- **Search Websites**: Use the search box or press `Ctrl+F`
- **Export Report**: Click "Export" button or press `Ctrl+E`
- **Auto-refresh**: Data updates automatically every 30 seconds

### Status Indicators
- 🟢 **Online**: Website is responding normally
- 🔴 **Offline**: Website is not responding
- 🟡 **Warning**: Website responding with errors (5xx status codes)
- ⚪ **Unknown**: No monitoring data available

### Metrics Explained
- **Uptime**: Percentage of time the website was accessible
- **Response Time**: Average time to receive a response
- **Status Code**: HTTP response code from the last check
- **Total Checks**: Number of monitoring attempts
- **Last Checked**: When the website was last monitored

## Customization

### Styling
The dashboard uses clean, modern CSS that's easy to customize:
- Light theme with professional colors
- Responsive grid layouts
- Subtle hover effects and transitions
- Clean typography using system fonts

### Adding New Metrics
To add new metrics to the website cards, modify the `renderWebsites()` function:

```javascript
<div class="metric">
    <div class="metric-icon">📊</div>
    <div class="metric-value">${website.your_metric}</div>
    <div class="metric-label">Your Metric</div>
</div>
```

### Custom Status Types
Add new status types by updating:
1. CSS classes (`.status-your-status`)
2. `getStatusText()` function
3. `getStatusIcon()` function

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## File Structure

```
website-monitor/
├── index.html          # Main dashboard file (contains HTML, CSS, JS)
└── README.md          # This file
```

## Keyboard Shortcuts

- `Ctrl+R` (or `Cmd+R`): Refresh data
- `Ctrl+F` (or `Cmd+F`): Focus search box
- `Ctrl+E` (or `Cmd+E`): Export data

## Sample Data

The demo includes monitoring data for:
- Google Search
- GitHub Platform  
- Stack Overflow (with warning status)
- CloudFlare CDN

## Deployment

### Static Hosting (GitHub Pages, Netlify, etc.)
1. Upload the HTML file to your hosting service
2. Access via your provided URL
3. The demo data will work immediately

### With Backend API
1. Set up your monitoring API server
2. Update the `CONFIG.apiBaseUrl` in the HTML file
3. Set `CONFIG.useDemoData = false`
4. Deploy both frontend and backend

## API Integration Examples

### Flask/Python Backend
```python
@app.route('/api/websites')
def get_websites():
    return jsonify([
        {
            "id": 1,
            "name": "Example Site",
            "url": "https://example.com",
            "status": "up",
            "status_code": 200,
            "response_time": 0.15,
            "uptime_percentage": 99.9,
            "total_checks": 1440,
            "last_checked": datetime.utcnow().isoformat() + "Z",
            "error_message": None
        }
    ])
```

### Node.js/Express Backend
```javascript
app.get('/api/websites', (req, res) => {
    res.json([
        {
            id: 1,
            name: "Example Site",
            url: "https://example.com",
            status: "up",
            status_code: 200,
            response_time: 0.15,
            uptime_percentage: 99.9,
            total_checks: 1440,
            last_checked: new Date().toISOString(),
            error_message: null
        }
    ]);
});
```

## Contributing

Feel free to submit issues and enhancement requests!

### Development Setup
1. Clone or download the project
2. Open `index.html` in your browser
3. Make changes and refresh to see updates
4. Test with both demo data and live API data

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For questions or issues:
1. Check the demo data is working first
2. Verify your API endpoint format matches the requirements
3. Check browser console for error messages
4. Ensure your API server supports CORS if running locally

---

**Made with ❤️ for better website monitoring**
