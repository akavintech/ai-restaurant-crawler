# AI-Powered Restaurant Menu Web Crawler

An automated system that uses AI and web crawling technologies to extract and structure menu information from restaurant websites.

## Features

- Automated web crawling of restaurant websites
- AI-powered menu information extraction
- Structured data output in JSON format
- Cross-platform compatibility (Windows, macOS, Linux)

## Prerequisites

- Python 3.x
- Google Chrome browser
- Google Gemini API key

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd [repository-name]
```

2. Create and activate a virtual environment:
```bash
python -m venv myvenv
source myvenv/bin/activate  # On Windows: myvenv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory and add:
```
GEMINI_API_KEY=your_api_key_here
```

## Usage

Run the main script:
```bash
python main.py
```

## Project Structure

- `main.py`: Main application file
- `requirements.txt`: Project dependencies
- `.env`: Environment variables (not tracked in git)

## Data Models

The project uses Pydantic models for data validation:
- `MenuItem`: Individual menu item details
- `Menu`: Collection of menu items
- `Restaurant`: Restaurant information with menu

## License

[Your chosen license]

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request 