from riotwatcher import RiotWatcher

w = RiotWatcher('<your-api-key>')

# check if we have API calls remaining
print(w.can_make_request())

me = w.get_summoner(name='pseudonym117')
print(me)

# takes list of summoner ids as argument, supports up to 40 at a time
# (limit enforced on riot's side, no warning from code)
my_mastery_pages = w.get_mastery_pages([me['id'], ])[str(me['id'])]
# returns a dictionary, mapping from summoner_id to mastery pages
# unfortunately, this dictionary can only have strings as keys,
# so must convert id from a long to a string
print(my_mastery_pages)

my_ranked_stats = w.get_ranked_stats(me['id'])
print(my_ranked_stats)

my_ranked_stats_last_season = w.get_ranked_stats(me['id'], season=3)
print(my_ranked_stats_last_season)

# all static methods are prefaced with 'static'
# static requests do not count against your request limit
# but at the same time, they don't change often....
static_champ_list = w.static_get_champion_list()
print(static_champ_list)

# import new region code
from riotwatcher import EUROPE_WEST

# request data from EUW
froggen = w.get_summoner(name='froggen', region=EUROPE_WEST)
print(froggen)

# create watcher with EUW as its default region
euw = RiotWatcher('<your-api-key>', default_region=EUROPE_WEST)

# proper way to send names with spaces is to remove them, still works with spaces though
xpeke = w.get_summoner(name='fnaticxmid')
print(xpeke)

# Error checking requires importing LoLException as well as any errors you wish to check for.
#
# For Riot's API, the 404 status code indicates that the requested data wasn't found and
# should be expected to occur in normal operation, as in the case of a an invalid summoner name,
# match ID, etc.
#
# The 429 status code indicates that the user has sent too many requests
# in a given amount of time ("rate limiting").

from riotwatcher import LoLException, error_404, error_429

try:
    response = rw.get_summoner('voyboy')
except LoLException as e:
    if e == error_429:
        print('We should retry in {} seconds.'.format(e.headers['Retry-After']))
    elif e == error_404:
        print('Summoner not found.')