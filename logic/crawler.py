import uuid
from typing import List, Dict, Any

from requests_html import BaseSession

YELP_DOMAIN = 'https://www.yelp.com'


def add_link_with_duplicate_check(links_collected: List[str], new_link: str):
    """
    Yelp website contains duplicates that can be found on the same page
    and on the other
    That's because site content based on ads recommendations,
    and content can be not unique, that's why we perform this check
    """
    if new_link not in links_collected:
        links_collected.append(new_link)


def get_business_links(session: BaseSession, category_name: str, location: str) -> List[str]:
    """
    Pagination counts like this:
    every new item is + 10
    1 - 0, 2 - 10, 3 - 30
    There is no way to see the last page number, it is not on UI and not seen in API
    That's why we check error content and if present that means we reached the end
    """

    links_collected = []
    category_name = category_name.strip().replace(' ', '+')
    link = f'{YELP_DOMAIN}/search?find_desc={category_name}&find_loc={location}%2C+CA'
    pagination = 0

    while True:
        result = session.get(f'{link}&start={pagination}')
        h3 = result.html.find('.css-oxqmph', first=True)
        if h3 and h3.text == "We're sorry, the page of results you requested is unavailable.":
            # We get to the last page
            break
        business_blocks = result.html.find('.list__09f24__ynIEd', first=True).find('li')
        for business_block in business_blocks:
            sponsored_result = business_block.find('.toggle__09f24__aaito', first=True)
            if sponsored_result:
                a = sponsored_result.find('.css-1egxyvc', first=True).find('a', first=True)
                add_link_with_duplicate_check(
                    links_collected,
                    YELP_DOMAIN + list(a.links)[0]
                )
            else:
                special_offers_or_get_fast_response = business_block.find(
                    '.carouselContainer__09f24__OQMYU',
                    first=True,
                )
                if special_offers_or_get_fast_response:
                    # For this case we actually have multiple businesses inside container carousel
                    carousel_blocks = special_offers_or_get_fast_response.find('.css-nyjpex')
                    for carousel_block in carousel_blocks:
                        a = carousel_block.find('a', first=True)
                        add_link_with_duplicate_check(
                            links_collected,
                            YELP_DOMAIN + list(a.links)[0]
                        )
        pagination += 10
    return links_collected


def get_business_details(link: str, session: BaseSession) -> Dict[str, Any]:
    """
    Explanation
    In task description suggested to use API when available or HTML when not
    Here are problems with using API
    1. We have to get meta_content key
    which is used to generate API link (we get it from html),
    so HTML is requested any way
    2. Even API cannot give us all information
    (for example rating and reviews_count are absent there)
    Here I used API approach to follow task description,
    but faster solution would be only use HTML (as we are not making double requests)
    """

    html_result = session.get(link).html
    meta = html_result.find('meta[name="yelp-biz-id"]', first=True)
    # Rating of business, reviews_number is not showed in API, that's why we take it from html page
    rating = html_result.find('.css-1fdy0l5', first=True).text
    reviews_number = html_result.find(
        '.css-19v1rkv',
        first=True,
    ).text
    meta_content = meta.attrs['content']

    api_result = session.get(
        f'https://www.yelp.com/biz/{meta_content}'
        f'/props?original_request_id={uuid.uuid4()}'
    )
    data = api_result.json()['bizDetailsPageProps']
    reviews = data['reviewFeedQueryProps']['reviews'][:5]
    business_name = data['businessName']
    business_website = html_result.find('.css-1p9ibgf')[-2].text

    data = {
        'yelp_url': link,
        'rating': rating,
        'business_name': business_name,
        'reviews_count': reviews_number,
        'business_website': business_website,
        'reviews': []
    }
    for review in reviews:
        data['reviews'].append(
            {
                'username': review['user']['markupDisplayName'],
                'location': review['user']['displayLocation'],
                'date': review['localizedDate']
            }
        )
    return data
