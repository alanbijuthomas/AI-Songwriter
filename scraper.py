from bs4 import BeautifulSoup
import requests
import time

# set headers for HTTP requests
HEADERS = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15'}

# get album title from album page
def get_title(album):
    response = requests.get(album, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('div', class_='songinalbum_title').text
    return title

# get song urls from album page
def get_songs(album):
    response = requests.get(album, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    songs = []
    for div in soup.find_all('div', class_='listalbum-item'):
        for a in div.find_all('a'):
            song = album.rsplit('/', 1)[0] + '/' + a.get('href')
            songs.append(song)
    return songs

# get lyrics from song page
def get_lyrics(songs):
    lyrics = ''
    for song in songs:
        response = requests.get(song, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        for div in soup.find_all('div', class_=None):
            lyrics += div.text
        time.sleep(7)
    return lyrics

# clean lyrics
def clean_lyrics(lyrics):
    lines = lyrics.split('\n')
    lines_with_lyrics = [line for line in lines if line.strip() != '']
    cleaned_lyrics = ''
    for line in lines_with_lyrics:
        cleaned_lyrics += line + '\n'
    return cleaned_lyrics

if __name__ == '__main__':
    # store album urls for Lou Reed
    albums = []
    albums.append('https://www.azlyrics.com/lyrics/velvetunderground/sundaymorning.html')
    albums.append('https://www.azlyrics.com/lyrics/velvetunderground/whitelightwhiteheat.html')
    albums.append('https://www.azlyrics.com/lyrics/velvetunderground/candysays.html')
    albums.append('https://www.azlyrics.com/lyrics/velvetunderground/wholovesthesun.html')
    albums.append('https://www.azlyrics.com/lyrics/velvetunderground/icantstandit.html')
    albums.append('https://www.azlyrics.com/lyrics/velvetunderground/weregonnahavearealgoodtimetogether.html')
    albums.append('https://www.azlyrics.com/lyrics/loureed/icantstandit.html')
    albums.append('https://www.azlyrics.com/lyrics/loureed/vicious.html')
    albums.append('https://www.azlyrics.com/lyrics/loureed/berlin156121.html')
    albums.append('https://www.azlyrics.com/lyrics/loureed/ridesallyride.html')
    albums.append('https://www.azlyrics.com/lyrics/loureed/crazyfeeling.html')
    albums.append('https://www.azlyrics.com/lyrics/loureed/ibelieveinlove.html')
    albums.append('https://www.azlyrics.com/lyrics/loureed/gimmiesomegoodtimes.html')
    albums.append('https://www.azlyrics.com/lyrics/loureed/stupidman.html')
    albums.append('https://www.azlyrics.com/lyrics/loureed/howdoyouspeaktoanangel.html')
    albums.append('https://www.azlyrics.com/lyrics/loureed/myhouse.html')
    albums.append('https://www.azlyrics.com/lyrics/loureed/legendaryhearts.html')
    albums.append('https://www.azlyrics.com/lyrics/loureed/iloveyousuzanne.html')
    albums.append('https://www.azlyrics.com/lyrics/loureed/mistrial.html')
    albums.append('https://www.azlyrics.com/lyrics/loureed/romeohadjuliette.html')
    albums.append('https://www.azlyrics.com/lyrics/loureed/smalltown.html')
    albums.append('https://www.azlyrics.com/lyrics/loureed/whatsgoodthethesis.html')
    albums.append('https://www.azlyrics.com/lyrics/loureed/eggcream.html')
    albums.append('https://www.azlyrics.com/lyrics/loureed/paranoiakeyofe.html')
    albums.append('https://www.azlyrics.com/lyrics/loureed/theconquerorworm.html')
    albums.append('https://www.azlyrics.com/lyrics/metallica/brandenburggate.html')

    # get lyrics
    all_lyrics = ''
    for album in albums:
        songs = get_songs(album)
        lyrics = get_lyrics(songs)
        all_lyrics += lyrics
        print('Scraped lyrics for ' + get_title(album))

    # clean lyrics
    cleaned_lyrics = clean_lyrics(all_lyrics)

    # write to file
    filename = 'dataset.txt'
    with open(filename,'w') as file:
        file.write(cleaned_lyrics)
    print('Wrote lyrics to ' + filename)
