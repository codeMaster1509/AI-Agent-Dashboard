# AI Agent Dashboard Documentation

## Project Summary
The AI Agent Dashboard is a Streamlit-based web application that automates the process of gathering and analyzing information from web searches using AI. The application allows users to process lists of entities (from CSV files or Google Sheets), perform web searches for each entity, and then analyze the search results using the Groq LLM API to extract structured information.

Link to the Loom's Video: https://www.loom.com/share/dbd87b43c1d34973b7841723d58f54b6?sid=fdf90e7d-6c5c-49d1-be5d-6f8c21aee372

## Key Features
- Data input flexibility (CSV or Google Sheets)
- Automated web searching using ScraperAPI
- AI-powered information extraction using Groq's LLM
- Interactive result visualization
- Export capabilities (CSV download and Google Sheets integration)
- Progress tracking for long-running operations
- Expandable search result previews

## Prerequisites
- Python 3.7+
- Required Python packages:
  - streamlit
  - pandas
  - beautifulsoup4
  - google-auth
  - google-api-python-client
  - requests
  - groq
  
## API Requirements
You'll need API keys for the following services:
1. ScraperAPI - For web scraping and search results
2. Groq API - For LLM-based information extraction
3. Google Cloud Service Account (optional) - For Google Sheets integration

## Setup Instructions

1. Install required packages:
```bash
pip install streamlit pandas beautifulsoup4 google-auth google-api-python-client requests groq
```

2. Configure API Keys:
   - Obtain a ScraperAPI key from https://www.scraperapi.com
   - Get a Groq API key from https://console.groq.com
   - (Optional) Set up a Google Cloud Service Account and enable Google Sheets API

3. Run the application:
```bash
streamlit run agent.py
```

## Usage Guide

### 1. Data Input
- **CSV Upload**:
  - Prepare a CSV file with entities you want to research
  - Upload through the file uploader interface
  
- **Google Sheets**:
  - Paste your Google Service Account JSON credentials
  - Enter the Google Sheet URL
  - Click "Connect to Google Sheets"

### 2. Search Configuration
1. Select the column containing entities to search for
2. Enter your ScraperAPI key
3. Customize the search prompt template
4. Enter your Groq API key

### 3. Processing
1. Click "Run Web Search" to gather information
2. Review sample search results
3. Customize the LLM prompt for information extraction
4. Click "Process with LLM" to analyze the search results

### 4. Results and Export
- View results in table format
- Expand detailed results for each entity
- Download results as CSV
- (Optional) Update Google Sheet with results

## Component Details

### WebSearcher
- Handles web search operations using ScraperAPI
- Parses HTML results using BeautifulSoup4
- Returns structured search results (title, link, snippet)
- Implements error handling and rate limiting

### DataLoader
- Manages data input from CSV and Google Sheets
- Handles different CSV encodings
- Implements Google Sheets API integration
- Includes error handling for data loading operations

### LLMProcessor
- Integrates with Groq's LLM API
- Processes search results using custom prompts
- Implements structured information extraction
- Includes error handling and retry logic

## Best Practices

1. **Rate Limiting**:
   - The application includes built-in delays between API calls
   - Adjust the `time.sleep()` duration based on your API limits

2. **Error Handling**:
   - All major operations include try-catch blocks
   - User-friendly error messages are displayed
   - Failed operations don't crash the application

3. **Resource Management**:
   - Search results are limited to top 5 per entity
   - LLM responses are capped at 300 tokens
   - Progress bars show processing status

## Limitations and Considerations

1. **API Costs**:
   - ScraperAPI charges per request
   - Groq API charges per token
   - Consider costs when processing large datasets

2. **Rate Limits**:
   - ScraperAPI has request limits based on your plan
   - Groq API has rate limits for requests
   - Built-in delays help manage these limits

3. **Data Privacy**:
   - No data is stored permanently
   - All processing happens in memory
   - Results need to be explicitly saved or exported

## Troubleshooting

1. **Empty Search Results**:
   - Verify ScraperAPI key is valid
   - Check search prompt template
   - Ensure entities are properly formatted

2. **LLM Processing Errors**:
   - Verify Groq API key is valid
   - Check custom prompt format
   - Ensure search results are available

3. **Google Sheets Issues**:
   - Verify service account permissions
   - Check sheet URL format
   - Ensure proper API scope is enabled
