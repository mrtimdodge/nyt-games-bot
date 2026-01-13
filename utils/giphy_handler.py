import asyncio
import aiohttp
from aioconsole import  aprint
from urllib import parse

class GiphyHandler:
    """
    A class to handle GIPHY API requests asynchonously. Must be started before any methods are used.

    Attributes:
        url (str): URL to look up for requests (default: http://api.giphy.com/v1/gifs/random)
        api_key (str): API key to use for requests (default: None)
        is_closed (bool): Boolean that represents when GiphyHandler is closed. (default: False)
        is_started (bool): Boolean that represents when GiphyHandler is started. (default: False)
    Methods:
        async reload(api_key):
            Close GiphyHandler temporarily, stop any current requests, input a new API key, and start it again.
        async close():
            Stop any current requests, and set GiphyHandler as closed.
        async random_request(tag, request_tries=5):
            Request a GIPHY URL with a certain tag. If a try fails, then it starts again.
        async request_handler(tag, is_last_attempt=True):
            Handle a GIPHY URL request, and process the results. If at the last attempt and it doesn't work, then it prints out the error.
        start(api_key):
            Start GiphyHandler, and input a new API key.
    
    """

    url = "http://api.giphy.com/v1/gifs/random"
    api_key = None
    is_closed = False
    is_started = False

    async def reload(self):
        """Close GiphyHandler temporarily, stop any current requests, input a new API key, and start it again."""
        assert self.is_started is True, "Giphy handler must be started first"

        await aprint("Reloading GIPHY handler...")

        self.is_closed = True
        self.is_started = False

        await asyncio.sleep(2)


        self.is_closed = False
        self.is_started = True

    async def close(self):
        """Stop any current requests, and set GiphyHandler as closed."""
        assert self.is_started is True, "Giphy handler must be started first"

        await aprint("Closing GIPHY handler...")

        self.is_closed = True
        self.is_started = False

    async def random_request(self, tag, request_tries=5):
        """Request a GIPHY URL with a certain tag. If a try fails, then it starts again."""
        assert request_tries > 0, "Number of attempts must be more than 0"
        assert self.is_started is True, "Giphy handler must be started first"

        response = None
        for attempt in range(request_tries):
            if not self.is_closed:
                is_last_attempt = True if attempt == request_tries - 1 else False # Checks if it is last attempt, for error checking purposes
                response = await self.request_handler(tag=tag, is_last_attempt=is_last_attempt)
            if response != -1:
                return response
            if self.is_closed:
                return -1
        
        return response

    async def request_handler(self, tag, is_last_attempt=True):
        """Handle a GIPHY URL request, and process the results. If at the last attempt and it doesn't work, then it prints out the error."""
        params = parse.urlencode({
            'tag': tag,
            'api_key': self.api_key,
            'limit': '1'
        })

        requested_url = ''.join((self.url, '?', params))

        async with aiohttp.ClientSession() as session:
            if not self.is_closed:
                async with session.get(requested_url) as response:
                    if not self.is_closed:
                        data = await response.json()

        if 'data' in data and data['data']: # If data is passed and there is content
            return data['data']['url']
        elif 'data' in data: # If data is passed but there is no content
            return None
        else: # If no data is passed
            if is_last_attempt and data:
                await aprint(f"Could not successfully receive \"{requested_url}\": {data['message']}")
            return -1

    def __init__(self, api_key):
        assert type(api_key) is str, "Giphy API key must be a string"
        assert len(api_key) > 0, "Giphy API key must be longer than 0"
        self.api_key = api_key

    def start(self):
        """Start GiphyHandler, and input a new API key."""

        if not self.is_started:
            print("Starting GIPHY handler...")
            self.is_started = True
            self.is_closed = False
        else:
            print("GIPHY handler is already started!")