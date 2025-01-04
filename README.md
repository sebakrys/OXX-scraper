# Classified Ads Web Scraper

This project is a Python-based web scraper designed to collect product data from a popular Polish classified ads website. The scraper is tailored specifically to this website and currently works only for listings in the Opolskie voivodeship. It may not function correctly on other platforms or regions due to its reliance on the site's unique HTML structure.

> **Disclaimer:** This script is for educational purposes only. Using this scraper on websites may violate their Terms of Service. By using this code, you agree to take full responsibility for its usage and ensure compliance with the applicable rules and regulations.

---

## Features

- Fetches data with retries to handle temporary connection issues.
- Extracts details for individual product listings, including:
  - Title
  - Price
  - Description (HTML and plain text)
  - Image URLs
  - Categories
- Handles pagination to scrape data from multiple pages.
- Saves data into CSV files with headers.
- Supports splitting data into multiple CSV files if a file exceeds 2MB.
- Obfuscates sensitive data like phone numbers in product descriptions.
- Detects breadcrumbs for category extraction.

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository
   ```

2. Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

   **`requirements.txt`**:
   ```plaintext
   requests
   beautifulsoup4
   ```

3. Configure the base URL:
   Edit the `url` variable in the script to point to the desired base URL (e.g., `https://example.com/category/`).

---

## Usage

Run the script using Python:

```bash
python scraper.py
```

- The scraper will generate CSV files in the current directory.
- The filenames will include a timestamp and part number (e.g., `itemsCatalogue_home_2025.01.04_15_30_00_part0.csv`).

### Output
Each CSV file contains the following headers:

| ID   | Short Description | Images  | Title | Price  | Description NoHTML | Description | Single Category | Categories |
|------|-------------------|---------|-------|--------|--------------------|-------------|-----------------|------------|

---

## Code Overview

### Main Functions

1. **`fetch_with_retries(url, retries=3, delay=2)`**:
   - Handles HTTP requests with retry logic in case of failures.

2. **`scrapeItemList(url)`**:
   - Scrapes the main listing pages, iterates through pagination, and collects product details.

3. **`scrapeItemDetails(url)`**:
   - Fetches detailed information for individual product pages.

4. **`createFileAndAddHeaders(filename)`**:
   - Creates a new CSV file and writes the header row.

### Key Libraries

- **`requests`**: For HTTP requests.
- **`BeautifulSoup`**: For parsing and extracting HTML data.
- **`csv`**: For saving data in CSV format.

---

## Limitations

- This scraper is specifically designed for a popular Polish classified ads website and is not compatible with other platforms without modifications.
- It does not use JavaScript execution, so it may not work on websites heavily reliant on dynamic content.
- It assumes specific HTML structures for extracting data; changes to the target website may require script adjustments.

---

## Best Practices

- Use rate limiting to avoid overloading the target server (e.g., `time.sleep()` between requests).
- Respect the robots.txt file of the target website.
- Avoid scraping sensitive or personal data unless explicitly allowed by the website’s Terms of Service.

---

## Contributions

Feel free to fork this repository and contribute by submitting pull requests. Suggestions for improvement are always welcome.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Acknowledgments

This project is inspired by the need to explore data scraping techniques and demonstrate Python skills for portfolio purposes. The code and documentation are structured to highlight clean and modular programming practices.

