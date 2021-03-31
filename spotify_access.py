import json
import webbrowser
import mysql.connector
import requests
import database_talker
from tqdm import tqdm

CLIENT_ID = 'd97f7a723b6348f4b32e057abeffc131'
CLIENT_SECRET = 'Sooper Secret'
REDIRECT_URI = 'https://google.com'

API_ENDPOINT = 'https://api.spotify.com/v1'

def post(url, dict):
	out = requests.post(url, dict)
	# print("Post: " + out.text + "/n")
	return out

def get(url, params=None, headers=None):
	out = requests.get(url, params=params, headers=headers)
	# Ensure correct encoding for interpretation later
	out.encoding = "utf-8"
	# Any good status code passes the response on, otherwise raise the resposne as an error
	if out.status_code == requests.codes.ok:
		return out
	out.raise_for_status()

def get_access_keys():
	# Go here: https://accounts.spotify.com/authorize?client_id=d97f7a723b6348f4b32e057abeffc131&response_type=code&redirect_uri=https%3A%2F%2Fgoogle.com&scope=playlist-read-private+playlist-read-collaborative

	AUTH_URL = 'http://accounts.spotify.com/authorize'
	auth_response = get(AUTH_URL, params={
		'client_id': CLIENT_ID,
		'response_type': 'code',
		'redirect_uri': REDIRECT_URI,
		'scope': 'playlist-read-private playlist-read-collaborative'
	})

	print("Go to: " + auth_response.url)
	authorization_code = input("Code me: ")

	# Request access token
	ACCESS_URL = 'https://accounts.spotify.com/api/token'

	auth_response = post(ACCESS_URL, {
		'grant_type': 'authorization_code',
		'code': authorization_code,
		'redirect_uri': REDIRECT_URI,
		'client_id': CLIENT_ID,
		'client_secret': CLIENT_SECRET,
	})

	auth_response_data = auth_response.json()

	access_token = auth_response_data['access_token']
	refresh_token = auth_response_data['refresh_token']

	return (access_token, refresh_token)

def rebuild_access_table(db, access_token=None, refresh_token=None, auto=True):
	if auto is False:
		(access_token, refresh_token) = get_access_keys()
	db.modify("DROP TABLE access_data")
	db.modify( \
	"""
	CREATE TABLE IF NOT EXISTS access_data(
		access_token	TEXT,
		refresh_token	TEXT,
		client_id		TEXT,
		client_secret	TEXT,
		redirect_uri	TEXT
	);""")
	db.modify( \
	"""
	INSERT INTO access_data (access_token, refresh_token, client_id, client_secret, redirect_uri)
	VALUES (
		'{access_token}',
		'{refresh_token}',
		'{client_id}',
		'{client_secret}',
		'{redirect_uri}'
	);""".format(
			access_token=access_token,
			refresh_token=refresh_token,
			client_id=CLIENT_ID,
			client_secret=CLIENT_SECRET,
			redirect_uri=REDIRECT_URI
		))

def make_header(access_token):
	return {'Authorization': 'Bearer {token}'.format(token=access_token)}

def refresh(db=None):
	if db is None:
		db = database_talker.db_talker()
	db.execute("SELECT access_token FROM access_data;")
	access_token = db.fetchone()[0]
	db.execute("SELECT refresh_token FROM access_data;")
	refresh_token = db.fetchone()[0]
	refresh_response = post('https://accounts.spotify.com/api/token', {
		'grant_type': 'refresh_token',
		'refresh_token': refresh_token,
		'redirect_uri': REDIRECT_URI,
		'client_id': CLIENT_ID,
		'client_secret': CLIENT_SECRET
	})
	
	refresh_response_data = refresh_response.json()

	if 'access_token' in refresh_response_data:
		access_token = refresh_response_data['access_token']
	if 'refresh_token' in refresh_response_data:
		refresh_token = refresh_response_data['refresh_token']

	rebuild_access_table(db, access_token, refresh_token)

def pretty_print(json_string):
	print(json.dumps(json.loads(json_string), indent=4))

class spotify_session:
	def __init__(self) -> None:
		self.db = database_talker.db_talker()
		# rebuild_access_table(self.db, auto=False)
		refresh(db=self.db)
		self.db.execute("SELECT access_token FROM access_data;")
		self.access_token = self.db.fetchone()[0]
		self.header = make_header(self.access_token)
		self.db.execute("SELECT refresh_token FROM access_data;")
		self.refresh_token = self.db.fetchone()[0]

	def db_execute(self, statement):
		self.db.execute(statement)

	def db_modify(self, statement):
		self.db.modify(statement)

	def playlists_to_file(self):
		f = open("All Playlists.txt", "w", encoding='utf8', errors='ignore')
		playlists = paging_object(API_ENDPOINT + '/me/playlists', self.access_token)
		pbar = tqdm(total=len(playlists), desc="Playlists Dumped", ncols=100)
		for playlist_elem in iter(playlists):
			try:
				playlist = playlist_object.from_json(playlist_elem, access_token=self.access_token)
				f.write(playlist.json['name'] + ": " + str(len(playlist.tracks)) + " songs\n")
				for track in iter(playlist):
					f.write("\t" + track['name'] + " - ")
					art_str = ''
					for artist in track['artists']:
						art_str = art_str + artist['name'] + ' / '
					f.write(art_str[:-3] + "\n")
				pbar.update()
			except:
				print("Failed at: " + playlist_elem['name'])
		f.close()

	def structure_db(self):
		self.db_modify('''DROP TABLE IF EXISTS tracks''')
		self.db_modify( \
			'''
			CREATE TABLE tracks (
				ID char(62) NOT NULL,
				Name varchar(256),
				Artists varchar(1024),
				Artist0 char(62),
				Artist1 char(62),
				Artist2 char(62),
				Artist3 char(62),
				Artist4 char(62),
				Artist5 char(62),
				Artist6 char(62),
				Artist7 char(62),
				Artist8 char(62),
				Artist9 char(62),
				Artist10 char(62),
				Artist11 char(62),
				Artist12 char(62),
				Artist13 char(62),
				Artist14 char(62),
				Artist15 char(62),
				PRIMARY KEY (ID)
			);
			'''
			)
		self.db_modify('''DROP TABLE IF EXISTS artists''')
		self.db_modify( \
			'''
			CREATE TABLE artists (
				ID char(62) NOT NULL,
				Name varchar(64),
				PRIMARY KEY (ID)
			);
			'''
			)
		self.db_modify('''DROP TABLE IF EXISTS playlists''')
		self.db_modify( \
			'''
			CREATE TABLE playlists (
				ID char(62) NOT NULL,
				Name varchar(128),
				PRIMARY KEY (ID)
			);
			'''
			)
		self.db_modify('''DROP TABLE IF EXISTS playlists_songs''')
		self.db_modify( \
			'''
			CREATE TABLE playlists_songs (
				PlaylistID char(62),
				SongID char(62)
			);
			'''
			)

	def store_spotify_data(self):
		playlists = paging_object(API_ENDPOINT + '/me/playlists', self.access_token)
		pbar = tqdm(total=len(playlists), desc="Playlists Added", ncols=100)
		for playlist_elem in iter(playlists):
			playlist = playlist_object.from_json(playlist_elem, access_token=self.access_token)
			self.db_modify( \
				"""
				INSERT INTO playlists (ID, Name) VALUES ('{ID}', '{name}')
				""".format(
					ID=playlist.json["id"],
					name=playlist.json['name'].replace("'", "''")
				)
				)
			for track in iter(playlist):
				# Skip unavailable tracks
				if track['id'] is None:
					continue
				# Add track to playlist_songs
				self.db_modify( \
					"""
					INSERT INTO playlists_songs (PlaylistID, SongID) VALUES ('{playlist_id}', '{song_id}')
					""".format(
						playlist_id=playlist.json['id'].replace("'", "''"),
						song_id=track['id'].replace("'", "''")
					)
					)
				# Add artists if not already in 'artists'
				for artist in track['artists']:
					self.db_execute("""SELECT * FROM artists WHERE ID=\"{artist_id}\"""".format(artist_id=artist['id']))
					if self.db.fetchone() is None:
						self.db_modify( \
							"""
							INSERT INTO artists (ID, Name) VALUES ('{artist_id}', '{name}')
							""".format(
								artist_id=artist['id'].replace("'", "''"),
								name=artist['name'].replace("'", "''")
							)
							)
				# TODO Add track if not already in 'tracks'
				self.db_execute('SELECT * FROM tracks WHERE ID=\"{id}\"'.format(id=track['id']))
				if self.db.fetchone() is None:
					it = 0
					artist_fields = ''
					artists_string = ''
					each_artist = ''
					for artist in track['artists']:
						artist_fields += ', Artist{it}'.format(it=it)
						artists_string += "{name} // ".format(name=artist['name'].replace("'", "''"))
						each_artist += ", '{artist_id}'".format(artist_id=artist['id'].replace("'", "''"))
						it += 1
					self.db_modify( \
						"""
						INSERT INTO tracks (ID, Name, Artists{artist_fields}) VALUES ('{id}', '{name}', '{artists_string}'{each_artist})
						""".format(
							artist_fields=artist_fields,
							id=track['id'].replace("'", "''"),
							name=track['name'].replace("'", "''"),
							artists_string=artists_string[:-4], # Removes the last space
							each_artist=each_artist
						)
						)
			pbar.update()

class paging_object:
	def __init__(self, url, access_token=None):
		self.access_token = access_token
		if access_token is not None:
			got = get(url, headers=make_header(access_token=access_token))
		else:
			got = get(url)
		self.json = got.json()
		self.length = self.json['total']
		self.pos = None

	def __iter__(self):
		self.pos = 0
		return self

	def __next__(self):
		if self.pos == len(self.json['items']):
			if self.json['next'] is None:
				raise StopIteration
			else:
				if self.access_token is not None:
					got = get(self.json['next'], headers=make_header(access_token=self.access_token))
				else:
					got = get(self.json['next'])
				self.json = got.json()
				self.pos = 0
		out = self.json['items'][self.pos]
		self.pos = self.pos + 1
		return out

	def __len__(self):
		return self.length

class playlist_object:
	def __init__(self, url, access_token=None):
		if access_token is not None:
			got = get(url, headers=make_header(access_token=access_token))
		else:
			got = get(url)
		json = got.json()
		self.json = json
		po = paging_object(json['tracks']['href'], access_token=access_token)
		self.tracks = []
		for track_elem in po:
			self.tracks.append(track_elem['track'])

	@classmethod
	def from_json(cls, json, access_token=None):
		if access_token is None:
			return cls(url=json['href'])
		return cls(url=json['href'], access_token=access_token)

	def __iter__(self):
		self.pos = 0
		return self

	def __next__(self):
		if self.pos == len(self.tracks):
			raise StopIteration
		out = self.tracks[self.pos]
		self.pos = self.pos + 1
		return out

	def __len__(self):
		return len(self.tracks)

def main():
	# rebuild_access_table(database_talker.db_talker(), auto=False)
	session = spotify_session()
	# playlists_to_file(session)
	session.structure_db()
	session.store_spotify_data()

if __name__=="__main__":
	main()