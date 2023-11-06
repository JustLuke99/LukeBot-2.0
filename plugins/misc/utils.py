import random

import giphy_client
from decouple import config
from giphy_client.rest import ApiException

api_instance = giphy_client.DefaultApi()
giphy_token = config("GIPHY_CLIENT")


def search_gifs(query):
    try:
        return api_instance.gifs_search_get(giphy_token, query, limit=25, rating="a")
    except ApiException as e:
        return "Exception when calling DefaultApi->gifs_search_get: %s\n" % e


def gif_response(emotion):
    gifs = search_gifs(emotion)
    lst = list(gifs.data)
    gif = random.choices(lst)
    return gif[0].url
