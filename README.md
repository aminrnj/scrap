# Web Scraping Price Tracker

A Flask-based web application for tracking product prices from various e-commerce websites in Iran. This application provides price monitoring, user management, and ticket system functionality.

## Features

- **Price Tracking**: Monitor product prices from multiple e-commerce sites
- **User Management**: Admin panel for user registration and management
- **Ticket System**: Support ticket system for user requests
- **Scraping Requests**: Users can request new products to be scraped
- **Excel Export**: Download price data in Excel format
- **Persian Calendar**: Support for Persian (Jalali) calendar
- **Real-time Updates**: Live price updates and notifications

## Technology Stack

- **Backend**: Flask, SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **Web Scraping**: Selenium, BeautifulSoup
- **Authentication**: Flask-Login
- **Date Handling**: jdatetime, pytz

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/aminrnj/scrap.git
   cd scrap
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Initialize database**
   ```bash
   python migrate.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

## Configuration

### Required Files

Create the following configuration files:

1. **authorized_users.json** - Admin users configuration
2. **users.json** - User permissions and settings
3. **update_lock.json** - Update lock configuration

### Chrome Driver

Download ChromeDriver and place it in the `chromedriver-win64/` directory.

## Usage

1. **Access the application**: Navigate to `http://localhost:5000`
2. **Login**: Use admin credentials to access the dashboard
3. **Monitor prices**: View real-time price data for tracked products
4. **Manage users**: Add/edit user permissions through the admin panel
5. **Handle tickets**: Respond to user support requests

## Project Structure

```
scrap/
├── app.py                 # Main Flask application
├── bot.py                 # Telegram bot integration
├── scrap.py              # Web scraping functionality
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
├── static/              # CSS, JS, and static files
├── migrations/          # Database migrations
├── db/                  # Database files
└── instance/            # Instance-specific files
```

## API Endpoints

- `GET /` - Main dashboard
- `GET /login` - Login page
- `POST /login` - Login authentication
- `GET /api/products` - Get product data
- `POST /update` - Update product data
- `GET /api/product-history/<model>` - Product price history
- `GET /api/weekly-stats` - Weekly statistics
- `GET /api/dollar-price` - Dollar price data
- `POST /scrap-request` - Submit scraping request
- `GET /view-requests` - View scraping requests
- `POST /ticket` - Submit support ticket
- `GET /view-tickets` - View tickets

## Database Models

- **User**: User accounts and permissions
- **ScrapRequest**: User scraping requests
- **Ticket**: Support tickets and responses

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please create an issue in the GitHub repository or contact the development team.

## Security Notes

- Change the default `SECRET_KEY` in production
- Use environment variables for sensitive configuration
- Regularly update dependencies
- Implement proper authentication and authorization 