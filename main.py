import json, urllib.request
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from google import genai
from datetime import date,timedelta
import os
from dotenv import load_dotenv

load_dotenv()

def send_mesage_to_slack(message :str):
    client = WebClient(token=os.getenv("SLACK_API_KEY"))
        
    try:
        response = client.chat_postMessage(channel="#general", text=f"{message} \n <@U08KRE919J7>")
    except SlackApiError as e:
        print(f"Error: {e.response['error']}")
        
def get_news():
   
    message = ""
    today = date.today()
    yesterday = today-timedelta(days=1)
    
    with urllib.request.urlopen(
        f'https://api-production-3ee5.up.railway.app/api/tech/{yesterday}'
    ) as response:
        data = json.load(response)

    # data['en'] = List of English tech articles
    # data['de'] = List of German tech articles
    for index,article in enumerate(data['en'],1):
        message += f"Article {index} - {article['content']} [{article['sourceUrl']}] \n"
        
    return message
        
def summarize_for_slack(message :str):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    prompt = f"""
    You are an executive assistant distilling long walls of news text into a morning brief. 
    Analyze the raw text blocks provided below and convert each topic into a single, bite-sized nugget. 

    Input Format:
    - Each raw text block follows the pattern: "Article N - [Article Content] - [sourceUrl]"
    - Treat the trailing sourceUrl as metadata only — never include it in the summary sentence itself.

    Strict Rules:
    - Output a single greeting line at the top: "*☕ Good Morning! Here is your bite-sized digest:*" but make the greeting dependant on the time of day (Good morning for before 12pm, Good afternoon for after 12 pm but before 6pm, good evening for after 6pm and before 12 am), and add to the line through your analysis of what the news is about  such as "Here is your tech news bite-sized digest:"
    - Create exactly one bullet point per raw text topic using a standard dash (-).
    - Keep each bullet point to a single, punchy sentence of 15 words or less.
    - Extract only the core update. Do not include background filler or extra context.
    - Completely strip out and ignore any mentions of news sources, sites, or publications if they exist in the text.
    - Use Slack markdown syntax: use *asterisks* to bold key metrics, numbers, or critical keywords. Do not use '#' for headers.
    - At the end of every bullet, append the sourceUrl as a Slack hyperlink using the format <sourceUrl|Read more...>, with a single space before the opening angle bracket.

    Raw News Text:
    {message}

    Morning Digest Output:
    """


    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    send_mesage_to_slack(interaction.output_text)
        
def main():
    news = get_news()
    summarize_for_slack(news)

if __name__ == "__main__":
    main()
