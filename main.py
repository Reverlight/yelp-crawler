from requests_html import HTMLSession

from logic.crawler import get_business_links, get_business_details
from logic.json_helper import dump_json


if __name__ == '__main__':
    category_name_input = 'Auto Repair'
    location_input = 'San Francisco'

    session = HTMLSession()
    links = get_business_links(session, category_name_input, location_input)
    businesses_details = {'businesses_details': []}

    for link in links:
        businesses_details['businesses_details'].append(
            get_business_details(
                link,
                session,
            )
        )
    dump_json('businesses_details.json', businesses_details)
