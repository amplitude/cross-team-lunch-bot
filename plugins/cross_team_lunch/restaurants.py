import random


class Restaurant(object):

    def __init__(self, name, cuisine, walk_time, yelp_link):
        self.name = name
        self.cuisine = cuisine
        self.walk_time = walk_time
        self.yelp_link = yelp_link


RESTAURANTS = [
    Restaurant(
        'HRD', 'Asian Fusion', 3,
        'https://www.yelp.com/biz/hrd-san-francisco-4'
    ),
    Restaurant(
        'Zen Izakaya', 'Japanese', 9,
        'https://www.yelp.com/biz/zen-izakaya-san-francisco-3'
    ),
    Restaurant(
        'Garaje', 'Mexican', 4,
        'https://www.yelp.com/biz/garaje-san-francisco'
    ),
    Restaurant(
        'Little Skillet', 'Soul Food', 8,
        'https://www.yelp.com/biz/little-skillet-san-francisco-2'
    ),
    Restaurant(
        'Delancey Street', 'American', 8,
        'https://www.yelp.com/biz/delancey-street-restaurant-san-francisco'
    ),
    Restaurant(
        'Picnic on Third', 'American', 4,
        'https://www.yelp.com/biz/picnic-on-third-san-francisco'
    ),
    Restaurant(
        'Primo Patio', 'Caribbean', 8,
        'https://www.yelp.com/biz/primo-patio-cafe-san-francisco'
    ),
    Restaurant(
        'Red Dog', 'American', 4,
        'https://www.yelp.com/biz/red-dog-restaurant-and-bar-san-francisco'
    ),
    Restaurant(
        'Mestiza Taqueria', 'Mexican', 7,
        'https://www.yelp.com/biz/mestiza-taqueria-san-francisco'
    ),
    Restaurant(
        'DragonEats', 'Vietnamese', 8,
        'https://www.yelp.com/biz/dragoneats-san-francisco-3'
    ),
    Restaurant(
        'American Grilled Cheese', 'Sandwiches', 1,
        'https://www.yelp.com/biz/the-american-grilled-cheese-kitchen-san-francisco'
    ),
    Restaurant(
        'Sajj', 'Mediterranean', 3,
        'https://www.yelp.com/biz/sajj-mediterranean-san-francisco'
    ),
    Restaurant(
        'Slice House', 'Pizza', 3,
        'https://www.yelp.com/biz/slice-house-san-francisco-3'
    ),
    Restaurant(
        'Pazzia', 'Italian', 8,
        'https://www.yelp.com/biz/pazzia-restaurant-and-pizzeria-san-francisco'
    ),
    Restaurant(
        'Paragon', 'American', 4,
        'https://www.yelp.com/biz/paragon-san-francisco-2'
    ),
    Restaurant(
        'Crossroads Cafe', 'Sandwiches', 6,
        'https://www.yelp.com/biz/crossroads-cafe-san-francisco-7'
    ),
    Restaurant(
        'Osha Thai', 'Thai', 8,
        'https://www.yelp.com/biz/osha-thai-san-francisco-13'
    ),
    Restaurant(
        'Koh Samui & The Monkey', 'Thai', 6,
        'https://www.yelp.com/biz/koh-samui-and-the-monkey-san-francisco-2'
    ),
    Restaurant(
        'Tres', 'Mexican', 5,
        'https://www.yelp.com/biz/tres-tequila-lounge-and-mexican-kitchen-san-francisco'
    ),
    Restaurant(
        'MoMo\'s', 'American', 5,
        'https://www.yelp.com/biz/momos-san-francisco'
    ),
    Restaurant(
        'Mexico au Parc', 'Mexican', 2,
        'https://www.yelp.com/biz/mexico-au-parc-san-francisco'
    ),
    Restaurant(
        '21st Amendment', 'American', 1,
        'https://www.yelp.com/biz/21st-amendment-brewpub-san-francisco-4'
    ),
    Restaurant(
        'Darwin Cafe', 'Sandwiches/Salad', 5,
        'https://www.yelp.com/biz/darwin-cafe-san-francisco'
    ),
    Restaurant(
        'Town\'s End', 'American', 7,
        'https://www.yelp.com/biz/towns-end-restaurant-and-bakery-san-francisco-2'
    ),
    Restaurant(
        'Brickhouse Cafe', 'American', 6,
        'https://www.yelp.com/biz/brickhouse-cafe-san-francisco-2'
    ),
    Restaurant(
        'Saison :champagne:', '3 Michelin Star', 6,
        'https://www.yelp.com/biz/saison-san-francisco-2'
    ),
    Restaurant(
        'Rooster & Rice', 'Asian', 5,
        'https://www.yelp.com/biz/rooster-and-rice-san-francisco-5'
    ),
    Restaurant(
        'The Bird', 'Sandwiches', 11,
        'https://www.yelp.com/biz/the-bird-san-francisco-2'
    ),
    Restaurant(
        'Lao Table', 'Laotian', 9,
        'https://www.yelp.com/biz/lao-table-san-francisco'
    ),
    Restaurant(
        'SOMA Eats', 'Sandwiches/Salad', 8,
        'https://www.yelp.com/biz/soma-eats-san-francisco'
    )
]


def get_random_restaurants(num_restaurants):
    restaurants = []
    for i in xrange(num_restaurants):
        restaurant = random.choice(RESTAURANTS)
        while restaurant in restaurants:
            restaurant = random.choice(RESTAURANTS)
        restaurants.append(restaurant)
    return restaurants
