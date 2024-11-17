from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests
from groq import Groq
import json
from typing import List, Dict, Any
import time

class WebSearcher:
    @staticmethod
    def search_web(query: str, api_key: str) -> List[Dict]:
        """Perform web search using ScraperAPI and parse HTML results."""
        url = f"https://api.scraperapi.com?api_key={api_key}&url=https://www.google.com/search?q={query}"
        try:
            response = requests.get(url)
            response.raise_for_status()

            if response.text.strip() == "":
                st.warning(f"Empty response for query: {query}")
                return []

            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract search results
            search_results = []
            # Look for search result divs (adjust selectors based on actual HTML structure)

            #change the selectors based on the actual HTML structure of the page you are looking for
            results = soup.find_all('div', class_='g')
            
            for result in results:
                try:
                    title_elem = result.find('h3')
                    link_elem = result.find('a')
                    snippet_elem = result.find('div', class_='VwiC3b')
                    
                    title = title_elem.get_text() if title_elem else 'No title'
                    link = link_elem['href'] if link_elem and 'href' in link_elem.attrs else 'No link'
                    snippet = snippet_elem.get_text() if snippet_elem else 'No snippet'
                    
                    if not link.startswith('http'):
                        continue
                        
                    search_results.append({
                        'title': title,
                        'link': link,
                        'snippet': snippet
                    })
                except Exception as e:
                    st.warning(f"Error parsing individual result: {str(e)}")
                    continue

            if not search_results:
                st.warning(f"No search results found for query: {query}")
            
            return search_results[:5]  # Return top 5 results

        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching search results: {str(e)}")
            return []
        except Exception as e:
            st.error(f"Error parsing search results: {str(e)}")
            return []

class DataLoader:
    @staticmethod
    def load_csv(uploaded_file) -> pd.DataFrame:
        """Load data from uploaded CSV file."""
        try:
            df = pd.read_csv(uploaded_file)
            return df
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(uploaded_file, encoding='latin1')
                return df
            except Exception as e:
                st.error(f"Error loading CSV: {str(e)}")
                return None

    @staticmethod
    def load_google_sheet(credentials_json: str, sheet_url: str) -> pd.DataFrame:
        """Load data from Google Sheets."""
        try:
            credentials = service_account.Credentials.from_service_account_info(
                eval(credentials_json),
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            sheet_id = sheet_url.split("/")[5]
            service = build('sheets', 'v4', credentials=credentials)
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=sheet_id, range='Sheet1').execute()
            data = result.get('values', [])
            if not data:
                st.error("No data found in Google Sheet")
                return None
            df = pd.DataFrame(data[1:], columns=data[0])
            return df
        except Exception as e:
            st.error(f"Error loading Google Sheet: {str(e)}")
            return None

class LLMProcessor:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
    
    def extract_info(self, entity: str, search_results: List[Dict], custom_prompt: str) -> str:
        """Extract information using Groq's LLM with custom prompt."""
        try:
            formatted_results = "\n".join([
                f"Title: {result.get('title', 'No title')}\n"
                f"Snippet: {result.get('snippet', 'No snippet')}\n"
                f"Link: {result.get('link', 'No link')}\n"
                for result in search_results
            ])
            
            
            prompt = f"{custom_prompt}\n\nSearch Results:\n{formatted_results}"

            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts and summarizes information from search results."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300,
                top_p=1,
                stream=False
            )
            
            extracted_info = response.choices[0].message.content.strip()
            return extracted_info if extracted_info else "No relevant information could be extracted."
            
        except Exception as e:
            error_message = f"Error with Groq API: {str(e)}"
            st.error(error_message)
            return f"Error: {error_message}"

def display_search_results(results: List[Dict]):
    """Display search results in a formatted way."""
    st.subheader("Search Results Preview")
    # for idx, result in enumerate(results, 1):
    with st.expander(f"Result {1}: {results[1]['title']}", expanded=True):
        st.write("**Title:**", results[1]['title'])
        st.write("**Snippet:**", results[1]['snippet'])
        st.write("**Link:**", results[1]['link'])
        st.markdown("---")

# Page configuration
st.set_page_config(
    page_title="AI Agent Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Add custom CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        margin-top: 10px;
    }
    .stProgress > div > div > div {
        background-color: #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    st.title("🤖 AI Agent Dashboard")
    
    # Initialize session state
    if 'processed_results' not in st.session_state:
        st.session_state.processed_results = None
    if 'current_search_results' not in st.session_state:
        st.session_state.current_search_results = None

    # Data Loading Section
    st.header("1. Data Input")
    data_source = st.radio("Choose Data Source:", ["Upload CSV", "Google Sheets"])
    
    df = None
    if data_source == "Upload CSV":
        uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
        if uploaded_file:
            df = DataLoader.load_csv(uploaded_file)
    else:
        with st.expander("Google Sheets Configuration"):
            credentials_json = st.text_area("Paste your Google Service Account JSON")
            sheet_url = st.text_input("Enter Google Sheet URL")
            if st.button("Connect to Google Sheets") and credentials_json and sheet_url:
                df = DataLoader.load_google_sheet(credentials_json, sheet_url)

    if df is not None:
        st.success("Data loaded successfully!")
        st.write("Preview of loaded data:")
        st.dataframe(df.head())
        
        # Configuration Section
        st.header("2. Search Configuration")
        col1, col2 = st.columns(2)
        
        with col1:
            selected_column = st.selectbox("Select Column for Query:", df.columns)
            serp_api_key = st.text_input("Enter ScraperAPI Key", type="password")
        
        with col2:
            search_prompt_template = st.text_input(
                "Enter your search prompt template (use {entity} as placeholder):",
                value="Get me information about {entity}"
            )
            groq_api_key = st.text_input("Enter Groq API Key", type="password")

        # Processing Section
        st.header("3. Process Data")
        
        # First step: Run web search
        if st.button("Run Web Search"):
            if not serp_api_key:
                st.error("Please provide ScraperAPI key")
                return

            with st.spinner("Searching web..."):
                results = []
                progress_bar = st.progress(0)
                total_entities = len(df[selected_column])
                
                for idx, entity in enumerate(df[selected_column]):
                    progress = (idx + 1) / total_entities
                    progress_bar.progress(progress)
                    
                    query = search_prompt_template.replace("{entity}", str(entity))
                    search_results = WebSearcher.search_web(query, serp_api_key)
                    
                    if search_results:
                        results.append({
                            "entity": entity,
                            "search_results": search_results
                        })
                    
                    time.sleep(0.5)

                st.session_state.current_search_results = results
                st.success("Web search completed!")

        # Display search results and get custom prompt
        if st.session_state.current_search_results:
            st.header("4. Search Results and Custom Prompt")
            
            # Display sample search results for the first entity
            first_result = st.session_state.current_search_results[0]
            st.subheader(f"Sample Results for: {first_result['entity']}")
            display_search_results(first_result['search_results'])
            
            # Get custom prompt from user
            custom_prompt = st.text_area(
                "Enter your custom prompt for analyzing these search results:",
                value="""Please analyze the search results and provide:
1. A brief summary of the entity
2. Any contact information found
3. Key relevant details

Please format the response in a clear, structured way.""",
                height=150
            )
            
            # Second step: Process with LLM
            if st.button("Process with LLM"):
                if not groq_api_key:
                    st.error("Please provide Groq API key")
                    return

                with st.spinner("Processing with LLM..."):
                    results = []
                    progress_bar = st.progress(0)
                    total_entities = len(st.session_state.current_search_results)
                    
                    llm_processor = LLMProcessor(groq_api_key)
                    
                    for idx, result in enumerate(st.session_state.current_search_results):
                        progress = (idx + 1) / total_entities
                        progress_bar.progress(progress)
                        
                        extracted_info = llm_processor.extract_info(
                            result['entity'],
                            result['search_results'],
                            custom_prompt
                        )
                        
                        results.append({
                            "entity": result['entity'],
                            "extracted_info": extracted_info
                        })
                        
                        time.sleep(0.5)

                    st.session_state.processed_results = results
                    st.success("LLM processing completed!")

        # Results Section
        if st.session_state.processed_results:
            st.header("5. Results")
            
            # Display results in table format
            st.subheader("Extracted Data Table")
            results_df = pd.DataFrame(st.session_state.processed_results)
            
            # Style the dataframe
            st.dataframe(
                results_df,
                column_config={
                    "entity": "Entity",
                    "extracted_info": "Extracted Information"
                },
                hide_index=True,
                use_container_width=True
            )
            
            st.markdown("---")
            
            # Display detailed results in expandable sections
            st.subheader("Detailed Results")
            for result in st.session_state.processed_results:
                with st.expander(f"Results for: {result['entity']}"):
                    st.markdown(result['extracted_info'])
            
            # Create download options
            results_df = pd.DataFrame(st.session_state.processed_results)
            
            # Download options
            st.header("6. Export Results")
            col1, col2 = st.columns(2)
            
            with col1:
                csv = results_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name='extracted_data.csv',
                    mime='text/csv'
                )
            
            with col2:
                if data_source == "Google Sheets" and credentials_json:
                    if st.button("Update Google Sheet"):
                        try:
                            service = build('sheets', 'v4', credentials=eval(credentials_json))
                            sheet_id = sheet_url.split("/")[5]
                            service.spreadsheets().values().append(
                                spreadsheetId=sheet_id,
                                range="Sheet1",
                                valueInputOption="RAW",
                                body={"values": results_df.values.tolist()}
                            ).execute()
                            st.success("Google Sheet Updated Successfully!")
                        except Exception as e:
                            st.error(f"Error updating Google Sheet: {str(e)}")

if __name__ == "__main__":
    main()