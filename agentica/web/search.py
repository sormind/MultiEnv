import os
from typing import Optional

from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
import requests
import serpapi

from core.executable_environment import ExecutableEnvironment
from core.types import TaskOutcome, EnvironmentResponse


class SearchAction(BaseModel):
    action: str = Field("The action to take, must be one of [`search`, `visit_url`, `done`].")
    query: Optional[str] = Field("The query for a search using a search engine. Use this if you want to search for something and don't have a URL.")
    url: Optional[str] = Field("the url you of a site that you would like to visit to learn more about, use this if you want to visit a specific website and write a proper and valid url")


class SearchEnvironment(ExecutableEnvironment):
    def __init__(self, serp_api_key=None):
        self.api_key = serp_api_key or os.getenv("SERP_API_KEY")
        if not self.api_key:
            raise ValueError("No API key found. Either provide a `serp_api_key` or set the `SERP_API_KEY variable")
        self.search_results = []
        self.visited_urls = set()

    def execute(self, llm_action: BaseModel) -> EnvironmentResponse:
        action = llm_action.dict().get("action")
        if not action:
            return EnvironmentResponse(status="Error",
                                       error=f"Action not provided within the `llm_action` field, found {llm_action}")
        match action:
            case "search":
                query = llm_action.query
                search_results = self._search(query)
                return search_results
            case "visit_url":
                url = llm_action.url
                url_content = self._visit_url(url)
                return url_content
            case "done":
                return EnvironmentResponse(status="Done")
            case _:
                return EnvironmentResponse(status="Unknown Action Error",
                                           error=f"Unknown action error, got: {action}. "
                                                 f"Expected one of: [`search`, `visit_url`]"
                                           )

    def _search(self, query: str):
        try:
            search_params = {
                "q": query,
                "api_key": self.api_key
            }

            results = serpapi.search(search_params)

            if "error" in results:
                return EnvironmentResponse(status="error", error=results["error"])
            else:
                search_results = []
                organic_results = results["organic_results"]
                for result in organic_results:
                    search_results.append({
                        "title": result["title"],
                        "link": result["link"],
                        "snippet": result["snippet"]
                    })
                self.search_results.append(search_results)
                return EnvironmentResponse(status="Search Executed", return_value=search_results)
        except Exception as e:
            return EnvironmentResponse(status="error", error=str(e))

    def _visit_url(self, url: str):
        if url in self.visited_urls:
            return EnvironmentResponse(status="error", error="You have already visited this URL.")

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract relevant information from the website
            title = soup.title.string if soup.title else None
            description = soup.find("meta", attrs={"name": "description"}).get("content") if soup.find("meta", attrs={"name": "description"}) else None
            headings = [tag.get_text() for tag in soup.find_all(["h1", "h2", "h3"])]
            paragraphs = [p.get_text() for p in soup.find_all("p")]
            links = [link.get("href") for link in soup.find_all("a")]

            url_content = {
                "title": title,
                "description": description,
                "headings": headings,
                "paragraphs": paragraphs,
                "links": links
            }

            self.visited_urls.add(url)
            return EnvironmentResponse(status="URL Visited", return_value=url_content)
        except requests.exceptions.RequestException as e:
            return EnvironmentResponse(status="error", error=str(e))

    def format_action_model(self) -> BaseModel:
        return SearchAction
    
    def describe_state(self) -> str:
        return f"Search Results: {self.search_results}\nVisited URLs: {self.visited_urls}"



