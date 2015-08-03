__author__ = 'bobo'

white_list = [
        "laptopuri",
        "telefoane",
        "tablete",
        "monitoare",
        "desktop",
        "router",
        "televizoare",
        "home-cinema",
        "audio",
        "mediaplayer",
        "foto",
        "obiective",
        "blitzuri",
        "dsrl",
        "camere",
        "console-",
        "genti",
        "mouse",
        "tastaturi",
        "espressor",
        "casti",
        "boxe",
        "ipod",
        "ebook",
        "memorii",
        "placi_baza",
        "placi_video",
        "ssd",
        "nas",
        "spalat",
        "fiare",
        "frigorifice",
        "anvelope-auto",
        "receiver",
        "electrocasnice",
        "incorporabile",
        "cuptoare",
        "conditionat",
        "espressor",
]

black_list = [
    "blog",
    "contact",
]


def filter_links(links, method='all'):

    accepted_links = None

    if method == 'white':
        accepted_links = filter_white_list(links)
    elif method == 'black':
        accepted_links = filter_black_list(links)
    else:
        accepted_links = filter_black_list(links)
        accepted_links = filter_white_list(accepted_links)

    return accepted_links


def filter_white_list(links):
    accepted_links = []

    #Filter links based on interest
    for link in links:
        for current_filter in white_list:
            if current_filter in link.url:
                accepted_links.append(link)

    return accepted_links


def filter_black_list(links):

    # Filter black listed urls
    for block in black_list:
        for link in links:
            if block in link.url:
                links.remove(link)

    return links