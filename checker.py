import datetime as dt
import re
from api import RedditAPIManager
from db import DatabaseConnection
import settings as env

class RedditChecker:
    def __init__(self):        
        self.db_conn = DatabaseConnection()
        self.api_manager = RedditAPIManager()
        self.set_token()


    def set_token(self):
        # First check DB for a stored token that's still valid
        entry = self.db_conn.retrieve_token()
        if entry is None or int(dt.datetime.now().timestamp()) >= entry[1]:
            token, expiry = self.api_manager.get_token()  # Asks Reddit for one
            self.db_conn.store_token(token, expiry)
        else:
            token, expiry = entry
            self.api_manager.set_token(token, expiry)
        return (token, expiry)


    def search_posts(self):
        data = self.api_manager.get_posts()
        results = {
            "cases": None,
            "hospitalizations": None
        }
        if data is None:
            return results
            
        # cases_regex = "^([A-Z]{1}[a-z]+\s[0-9]{1,2})\s+-\s+(Edmonton\s+Cases\s+of\s+COVID-19)$"
        cases_regex = "^([A-Z]{1}[a-z]+\s[0-9]{1,2})\s+-\s+(Edmonton\s+COVID-19\s+Cases\s+&\s+Daily\s+Tests)$"
        # hospitalizations_regex = "^([A-Z]{1}[a-z]+\s[0-9]{1,2})\s+-\s+(Edmonton\s+Vaccination\s+&\s+Hospitalization\s+Cases\s+of\s+COVID-19)$"
        hospitalizations_regex = "^([A-Z]{1}[a-z]+\s[0-9]{1,2})\s+-\s+(Edmonton\s+COVID-19\s+Active\s+Cases,\s+Daily\s+Cases,\s+Hospitalization\s+&\s+Vaccinations)$"
        cases_found = False
        hospitalizations_found = False

        # Assumption: the list of posts returned by Reddit API is ordered 
        # chronologically (most recent first)
        for post in data:
            info = post["data"]
            title = info["title"]

            # Check for Cases post
            if not cases_found:
                match = re.match(cases_regex, title)
                if match:
                    date = match.group(1)
                    date += " %d" % (dt.datetime.now() - dt.timedelta(hours=24)).date().year
                    title_type = match.group(2)
                    datetime = dt.datetime.strptime(date, "%B %d %Y").date()

                    stored_date = self.db_conn.retrieve_post_date(title_type)
                    if stored_date is not None:
                        stored_datetime = dt.datetime.strptime(stored_date, "%B %d %Y").date()
                    else:
                        # Need dummy value for comparison below
                        stored_datetime = dt.datetime.strptime("July 1 1867", "%B %d %Y").date()
                    
                    # Post is new! Get relevant data and save the new date
                    if datetime > stored_datetime:
                        cases_found = True
                        self.db_conn.store_post(title_type, date)
                        url = "https://www.reddit.com" + info["permalink"]
                        img_url = info.get("url")
                        results["cases"] = {
                            "title": title,
                            "url": url,
                            "img_url": img_url 
                        }
                        continue
            # Check for Hospitalizations post
            if not hospitalizations_found:
                match = re.match(hospitalizations_regex, title)
                if match:
                    date = match.group(1)
                    date += " %d" % (dt.datetime.now() - dt.timedelta(hours=24)).date().year
                    title_type = match.group(2)
                    datetime = dt.datetime.strptime(date, "%B %d %Y").date()

                    stored_date = self.db_conn.retrieve_post_date(title_type)
                    if stored_date is not None:
                        stored_datetime = dt.datetime.strptime(stored_date, "%B %d %Y").date()
                    else:
                        # Need dummy value for comparison below
                        stored_datetime = dt.datetime.strptime("July 1 1867", "%B %d %Y").date()

                    # Post is new! Get relevant data and save the new date
                    if datetime > stored_datetime:
                        hospitalizations_found = True
                        self.db_conn.store_post(title_type, date)
                        url = "https://www.reddit.com" + info["permalink"]
                        img_url = info.get("url")
                        results["hospitalizations"] = {
                            "title": title,
                            "url": url,
                            "img_url": img_url
                        }
        return results

if __name__ == "__main__":
    checker = RedditChecker()
    print(checker.search_posts())