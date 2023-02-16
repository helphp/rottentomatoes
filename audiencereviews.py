from time import sleep
from requests_html import HTMLSession

def fetch_audience_reviews(movie_url:str, number_of_reviews:int):

    session = HTMLSession()

    r = session.get(movie_url)

    # found that they have movie id and stuff stored in javascript variables
    # so we can excute this to retrieve those
    script = """
            () => {
                return RottenTomatoes.context.movieReview;
            }
        """
    # not sure if i need to render before running script
    # but it did give me a javascript error once when i didn't
    r.html.render()
    movieData = r.html.render(script=script, reload=False)

    movieID = movieData.get('movieId')
    end_cursor = movieData['pageInfo'].get('endCursor')

    # we can get movieData['title'], movieData['movieId']
    # movieData['reviewsCount'], movieData['pageInfo']['hasNextPage'], movieData['pageInfo']['hasPreviousPage']
    # movieData['pageInfo']['endCursor'], movieData['pageInfo']['startCursor'] (probably undefined will throw key error)

    # feed the endCursor variable to this URL and choose direction of 'prev' to get page 1 reviews
    reviews_api_url = f"https://www.rottentomatoes.com/napi/movie/{movieID}/reviews/user?f=null&direction=prev&endCursor={end_cursor}"
    page_one_items = session.get(reviews_api_url).json()

    # list we will add all fetched reviews to
    reviews = page_one_items['reviews']

    # using .get() so it doesn't throw error if key isn't found
    has_next_page = page_one_items['pageInfo'].get('hasNextPage')
    end_cursor = page_one_items['pageInfo'].get('endCursor')

    while has_next_page and len(reviews) < number_of_reviews:

        url = f"https://www.rottentomatoes.com/napi/movie/{movieID}/reviews/user?f=null&direction=next&endCursor={end_cursor}"

        items = session.get(url).json()

        for item in items['reviews']:
            reviews.append(item)
        
        has_next_page = items['pageInfo'].get('hasNextPage')
        end_cursor = items['pageInfo'].get('endCursor')
        
        # might be risky not sleeping between fetching? idk
        # seemed like i was taking their site down when fetching 10,000 lol
        # sleep(1)

    return reviews
    

reviews = fetch_audience_reviews('https://www.rottentomatoes.com/m/the_batman/reviews?type=user', 200)

for review in reviews:
    #sometimes name is None we can choose what those become with get()
    print(f"{review.get('displayName','N/A')} ({review.get('rating')}) - {review.get('timeFromCreation')}")
    #print(f"{review.get('review')}\n")