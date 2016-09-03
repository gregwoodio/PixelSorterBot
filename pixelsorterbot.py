# PixelSorterBot by Greg Wood, Sep 3 2016

import tweepy
from creds import creds
import urllib
from time import sleep
from PIL import Image
from random import randint
import requests
import shutil

def get_api():
	auth = tweepy.OAuthHandler(creds['consumer_key'], creds['consumer_secret'])
	auth.set_access_token(creds['access_token'], creds['access_token_secret'])
	api = tweepy.API(auth)
	return api

def get_latest_id():
	try:
		file = open('latest_id.txt', 'r')
		id = int(file.read())
		return id
	except IOError:
		return 0

def write_latest_id(id):
	file = open('latest_id.txt', 'w')
	file.write(str(id))
	file.close()

def sort_picture():
	im = Image.open('photo.jpg')
	pixels = list(im.getdata())

	color = randint(0,2)
	rev = bool(randint(0,1))

	pixels.sort(key=lambda tup:tup[color], reverse=rev)

	im2 = Image.new(im.mode, im.size)
	im2.putdata(pixels)
	im2.save('sorted.jpg')


def main():
	api = get_api()
	id = get_latest_id()

	if id != 0:
		mentions = api.mentions_timeline(id)
	# be careful here, if the file is missing we should just get the last tweet or something
	else:
		mentions = api.mentions_timeline()

	for mention in mentions:
		# reply could have multiple pictures
		for media in mention.extended_entities['media']:
			if media['type'] == 'photo':

				#username
				username = '@' + mention.user.screen_name

				#download the photo
				#add checks here for different photo types
				#urllib.request.urlretrieve(media['media_url_https'], 'photo.jpg')
				response = requests.get(media['media_url_https'], stream=True)
				with open('photo.jpg', 'wb') as out_file:
					shutil.copyfileobj(response.raw, out_file)
				del response

				sort_picture()

				#post picture
				api.update_with_media(filename='sorted.jpg', status=username, in_reply_to_status_id=mention.id)

				#wait a bit for rate limiting
				sleep(15)

		write_latest_id(mention.id)

if __name__ == '__main__':
	main()
