import csv
import pickle

"""
    This file parses through two last.fm data sets to be able to analyze trends in the different countries for different
    years. 
    
    The first data set is a record of users and relevant information like user id, country, age, gender, etc. The second
    data set is a record of playing a track which include the user id, timestamp, artist, song, etc. 
    
    The final data set will be a set of dictionaries (a dictionary for each year in the second data set). The 
    dictionaries are 2D so that the outer dictionary contains countries as keys and the inner dictionaries as values.
    The inner dictionaries contains artist as keys and the play count (integer) as values
"""


def create_user_country_dict():
    """
        Maps a user to its country in a dictionary

        This goes through the last.fm data set about individual users and makes a dictionary of user-country as the
        key-value pairs so we can map a user to their country. It also saves the dictionary in a pickle file

        :return user_country_dict: a dictionary that maps user ids to the country they live in
        :rtype user_country_dict: dict
    """

    # ----------- Get tools to read tsv files
    file_in = open('../data/userid-profile.tsv', 'r')
    reader = csv.reader(file_in, delimiter='\t')

    # create dictionary
    user_country = dict()
    index = 0

    # --------- Iterate through tsv file
    for row in reader:
        # skipping first row with headers
        if index == 0:
            # do nothing with this row
            index += 1
            continue

        ''''
            row[0] = user id
            row[3] = country
        '''

        # make sure the country value is not empty
        if row[3] != '':
            user_country[row[0]] = row[3]

        index += 1

    # save dictionary in file and return it
    store_dict_pickle("user_country", user_country)
    return user_country


def create_plays_dict():
    """
        Maps the play number of times a user plays an artist in a specific year in a 3D dictionary

        Goes through the last.fm data set where each row is an instance of a user playing a song. This method takes the
        year, user id, and artist from each row. It will add up the number of times each artist a user listens to for a
        given year. This will be stored in a 3D dictionary so that play count for an artist can be accessed by year,
        user id then artist.

        It also saves the dictionary to a pickle file

       :return dict plays_dict: a dictionary that maps the play number of times a user plays an artist in a specific
               year in a 3D dictionary
       :rtype plays_dict: dict
       dictionary[year][user_id][artist] = artist_play_count
            year: string
            user_id: string
            artist: string
            artist_play_count: int

    """

    # ----------- Get tools to read tsv files
    file_in = open('../data/user_track.tsv', 'r', encoding="utf8")
    reader = csv.reader(file_in, delimiter='\t', quoting=csv.QUOTE_NONE)

    # create dictionary
    plays = dict()

    # ------------ Iterate Through File
    for row in reader:
        """
            Get the need values from the row
        
            row[0] = user id
            row[1] = time-stamp
            row[2] = artist id
            row[3] = artist name
        """

        user = row[0]
        timestamp = row[1]
        artist = row[3]

        """
            Get the year from the timestamp
        
            Timestamp is in the format: year-month-dayThour:minute:second
            example: 2000-03-23T13:31:432
        """
        year = timestamp.split('-')[0]

        # -------- insert values into dictionary
        # check if the year exist in the plays dictionary
        if year in plays:
            '''
                The year key exists
                Check if the user key exists 
            '''
            if user in plays[year]:
                '''
                    The user key exists for given year.
                    Check if the artist key exists for the user id in the given year
                '''
                if artist in plays[year][user]:
                    '''
                        Artist key exists within user id for given year
                        Increment play count for atist
                    '''
                    plays[year][user][artist] += 1

                else:
                    '''
                        The artist key doesn't exist
                        Initialize the artist key with a value of 1
                    '''
                    plays[year][user][artist] = 1

            else:
                """
                    The user id dictionary for given year does not exist. This means that the vlaue for the artist 
                    for this year and user id does not exist either.
                    
                    So we need to create the user id dictionary and initialize the value for the artist to 1 
                """

                plays[year][user] = dict()
                plays[year][user][artist] = 1

        else:
            """
                The year does not exist. This means that the user id and artist does not exist either. So we have to
                create the year dictionary, the user id dictionary, and the initial value of 1 for the artist plays 
                count 
            """
            plays[year] = dict()
            plays[year][user] = dict()
            plays[year][user][artist] = 1

    # store dictionary in pickle file and return it
    store_dict_pickle("plays", plays)
    return plays


def create_country_artist_dict():
    """
        Creates a dict that maps every artist play count to country for each available year

        This method uses the create_user_country_dict() and create_plays_dict() to be able to list the play count for
        an artist for each country that it is played in. The results will be stored in a dictionary where it represents
        the play count for a specific year

        It also saves each year's dictionary to a pickle file
    """

    # get the two dictionaries so we can interweave the country, user id, and artist play count
    user_dict = load_dict_pickle("user_country")
    plays_dict = load_dict_pickle("plays")

    # go through each year in the plays dict and make a dictionary for each country and the artist count
    for year in plays_dict:
        # create dictionary for the current year
        country_artist = dict()

        '''
            Go through the plays_dict to get the user_id for each user in the current year in the iteration. Then, get
            the country that user belongs to from the user_dict and make a country dict if it doesn't already exist. If
            the country dict does exist, then add the artist play count for the current user to the play count in the
            country_artist dict
        '''
        for user in plays_dict[year]:
            # get the country the user belongs to
            try:
                country = user_dict[user]
            except KeyError:
                continue

            # if there's not a country dictionary for the given year, then make one
            if country not in country_artist:
                country_artist[country] = dict()

            for artist in plays_dict[year][user]:
                # check if there's an artist dictionary for the country_artist dict
                if artist in country_artist[country]:
                    # increment count by value in plays_dict
                    country_artist[country][artist] += plays_dict[year][user][artist]
                else:
                    # initialize value to value in plays_dict
                    country_artist[country][artist] = plays_dict[year][user][artist]

        # save current years dictionary in a pickle file
        store_dict_pickle(year+"_country_artist", country_artist)


''' 
    ------------- The below functions are for saving and loading dictionaries from/to files ---------------------
    Doing this was taken from: https://stackoverflow.com/questions/19201290/how-to-save-a-dictionary-to-a-file
'''


def store_dict_pickle(file_name, dictionary):
    """
        Saves a dictionary to a pickle file

        :param file_name: the name of the file the data will be stored in
        :type file_name: str

        :param dictionary: the dictionary to be stored in the file
        :type dictionary: dict
    """

    with open('../data/dictionary/' + file_name + '.pkl', 'wb') as f:
        pickle.dump(dictionary, f, pickle.HIGHEST_PROTOCOL)


def load_dict_pickle(file_name):
    """
    Retrieves a dictionary form the specified file

    :param file_name: the name of the file to load
    :type file_name: str

    :return: the dictionary retrieved from the file
    :rtype dict
    """

    with open('../data/dictionary/' + file_name + '.pkl', 'rb') as f:
        dictionary =  pickle.load(f)
    return dictionary



def print_country_artist_dict(country_artist, dict_name):
    print(dict_name)
    for country in country_artist:
        print(country)

    print("\n\n")


# ------------ Main Section of File
# create_user_country_dict()
# create_plays_dict()
#create_country_artist_dict()

print_country_artist_dict(load_dict_pickle("2005_country_artist"), "2005_country_artist")
print_country_artist_dict(load_dict_pickle("2006_country_artist"), "2006_country_artist")
print_country_artist_dict(load_dict_pickle("2007_country_artist"), "2007_country_artist")
print_country_artist_dict(load_dict_pickle("2008_country_artist"), "2008_country_artist")
print_country_artist_dict(load_dict_pickle("2009_country_artist"), "2009_country_artist")
print_country_artist_dict(load_dict_pickle("2010_country_artist"), "2010_country_artist")
print_country_artist_dict(load_dict_pickle("2013_country_artist"), "2013_country_artist")