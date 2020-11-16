from bs4 import BeautifulSoup
import requests, datetime, time, re, json, io

# Dictionary setup
'''
billboard = {
    'year': {
        'week': {
            'rank': {
                'title': 'song_title',
                'artist': 'artist_name' 
            }
        }
    }
}
'''

# Open session
s = requests.Session()

def downloadBillboardWeek(date):
    
    # Construct query with date
    query = "https://www.billboard.com/charts/hot-100/" + date
    # Retrieve data
    req = s.get(query)
    # Handle possible errors
    if req.status_code == 429:
        print("429: + " + date)
        # 429 Client Error: Too Many Requests for url
        time.sleep(int(req.headers["Retry-After"]))
        # Try to download again after suggested time
        return downloadBillboardWeek(date)
    elif req.status_code == 503:
        print("503: + " + date)
        time.sleep(1)
        return downloadBillboardWeek(date)
    else:
        # Raise if other type
        req.raise_for_status()
    # Extract html
    html = req.text
    # Parse as beautiful soup
    soup = BeautifulSoup(html, 'html.parser')
    # Iterate through all songs and collect info
    billboardWeek = {}

    #print("here")
    songs = soup.find_all('li', class_='chart-list__element')
    for song in songs:
        # Extract song rank
        rank_raw = song.find('span', class_='chart-element__rank__number')
        rank = int(rank_raw.text.strip())
        # Extract song title
        title_raw = song.find('span', class_='chart-element__information__song')
        title = title_raw.text.strip()
        # Extract song artist
        artist_raw = song.find('span', class_='chart-element__information__artist')
        artist = artist_raw.text.strip()
        # Add title and artist to week
        billboardWeek[rank] = {}
        billboardWeek[rank]['title'] = title
        billboardWeek[rank]['artist'] = artist
    
    return billboardWeek

def downloadBillboard(startDate, endDate):
    # Billboard Top 100 first week: 1958-08-09
    dateFormat = "%Y-%m-%d"
    startDate = datetime.datetime.strptime(startDate, dateFormat)
    endDate = datetime.datetime.strptime(endDate, dateFormat)

    #billboard = {}
    tempDate = startDate
    tempYear = tempDate.year
    while tempDate < endDate:
        # Initialize billboard and year
        billboard = {}
        billboard[tempYear] = {}
        print("Downloading year: %s" %tempYear)
        while tempDate.year == tempYear and tempDate < endDate:
            week = tempDate.strftime("%V")
            print("Week: %s" %week)
            # Initialize weeknumber and download week data
            billboard[tempDate.year][week] = downloadBillboardWeek(tempDate.strftime(dateFormat))
            # Move to next week
            tempDate += datetime.timedelta(days=7)
        # Save year to file
        path = "./billboardYears/" + str(tempYear) + ".txt"
        with open(path, "w") as file:
            json.dump(billboard, file, sort_keys=True, indent=4)
        print("Year saved: %s" %tempYear)
        # Increment year
        tempYear = tempDate.year

    #return billboard

def removeMovieRefsFromTitles(year):
    # Load year file
    path = "./billboardYears/" + str(year) + ".txt"
    billboard = eval(open(path).read())
    # Iterate through titles each week
    for w in billboard[str(year)].items():
        for r in w[1].items():
            # Remove potential movie reference styles
            title = r[1]['title'].split(' (From \\')
            if len(title) == 1:
                title = r[1]['title'].split(' (Theme From')
            if len(title) == 1:
                title = r[1]['title'].split(' (Love Theme From')
            # Update dict
            billboard[str(year)][w[0]][r[0]]['title'] = title[0]
    # Save updated dict
    with open(path, "w") as file:
        json.dump(billboard, file, sort_keys=True, indent=4)

def removeMovieRefsFromTitlesSpecific():
    for i in range(1963,1998):
        print("Removing movire references from year: {}" .format(i))
        removeMovieRefsFromTitles(i)

#removeMovieRefsFromTitlesSpecific()
#downloadBillboard('1965-01-09', '2020-11-16')
