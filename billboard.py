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
        print("Retrying after: " + str(req.headers["Retry-After"]))
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

    billboard = {}
    tempDate = startDate
    tempYear = tempDate.year
    while tempDate < endDate:
        # Initialize year
        billboard[tempYear] = {}
        print("Downloading year: %s" %tempYear)
        while tempDate.year == tempYear and tempDate < endDate:
            week = tempDate.strftime("%V")
            print("Downloading week: %s" %week)
            # Initialize weeknumber and download week data
            billboard[tempDate.year][week] = downloadBillboardWeek(tempDate.strftime(dateFormat))
            # Move to next week
            tempDate += datetime.timedelta(days=7)
        # Increment year
        tempYear = tempDate.year

    return billboard

#billboard = downloadBillboard('1974-01-01', '1974-12-31')
#with open("./1974_v3.txt", "w") as file:
#            json.dump(billboard, file, sort_keys=True, indent=4)
def storeBillboardData(start, end):
    print(start)
    for i in range(start, end + 1):
        billboard = downloadBillboard(str(i) + '-01-01', str(i) + '-12-31')
        f = open('billboard/' + str(i) + ".txt", 'w')
        json.dump(billboard, f, indent=4)
        f.close()

def storeSpecificBillboardData(startDate, endDate, fileName):
    billboard = downloadBillboard(startDate, endDate)
    f = open('billboard/' + fileName + ".txt", 'w')
    json.dump(billboard, f, indent=4)
    f.close()

def patchHoles(fileName):
    f = open('billboard/' + fileName + '.txt', 'r')
    unfinishedDict = json.load(f)
    f.close()
    for year in unfinishedDict:
        for week in unfinishedDict[year]:
            if unfinishedDict[year][week] == {}:
                print("downloading missing week: {}".format(week))
                d = year + "-W" + str(int(week))
                r = datetime.datetime.strptime(d + '-1', "%Y-W%W-%w")
                y = str(r.year)
                m = str(r.month) if r.month >= 10 else "0" + str(r.month)
                day = str(r.day) if r.day >= 10 else "0" + str(r.day)
                # print(downloadBillboardWeek(y+"-"+m+"-"+day))
                unfinishedDict[year][week] = downloadBillboardWeek(y+"-"+m+"-"+day)
    f = open('billboard/' + fileName + '.txt', 'w')
    json.dump(unfinishedDict, f, indent=4)
    f.close()


# billboard = downloadBillboard()
#print(billboard)
