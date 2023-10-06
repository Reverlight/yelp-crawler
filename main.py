from requests_html import HTMLSession

YELP_DOMAIN = 'https://www.yelp.com'
UL_CONTAINER = 'list__09f24__ynIEd'


def get_data():
    session = HTMLSession()
    r = session.get(f'{YELP_DOMAIN}/search?find_desc=Auto+Repair&find_loc=San+Francisco%2C+CA')
    results = r.html.find(f'.{UL_CONTAINER}', first=True).find('li')
    items = 0
    for result in results:

        sponsored_result = result.find('.toggle__09f24__aaito', first=True)

        if sponsored_result:
            items += 1
            # span css-1egxyvc
            a = sponsored_result.find('.css-1egxyvc', first=True).find('a', first=True)
            print(YELP_DOMAIN + list(a.links)[0])
            print(a.text)

        special_offers_or_get_fast_response = result.find('.carouselContainer__09f24__OQMYU', first=True)
        if special_offers_or_get_fast_response:
            # TODO. Refactor (here we got not multiple results inside)
            items += 1
            # span css-nyjpex
            a = special_offers_or_get_fast_response.find('.css-nyjpex', first=True).find('a', first=True)
            print(YELP_DOMAIN + list(a.links)[0])
            print(a.text)

    f = open('test.txt', 'w')
    f.write(r.html.html)
    f.close()

if __name__ == '__main__':
    get_data()
