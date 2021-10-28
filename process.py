import os
import pandas as pd

regions = {}
column_names = set()  # Remember to convert to list in app


# `end_date - start_date` outputs a stamp e.g `305 days 12:00:00`
# If we convert that to a string, split by spaces, get the first index
# and convert it to int, we get the number of valid days.
# This is because, e.g the 2020 data file contains extra 2021 rows which
# just messes with the whole data structure, thus with valid rows,
# we get the accurate data rows for the year.
# + 1 because end of the year date completes at the start of the year
# or just make `end_date = beginning of the year`
def valid_rows(start_date):
	year = str(start_date)[:4]
	end_date = pd.Timestamp(year + '-12-31')
	rows = int(str(end_date - start_date).split()[0]) + 1
	return rows


# Write file to csv, with specified columns
def write_csv(destination, file, df):
	if not os.path.isdir(destination):
		os.makedirs(destination)

	path = os.path.join(destination, file + '.csv')
	df.to_csv(path)


def country_wide():
	global regions

	country = None
	for region in regions:
		df = regions[region]
		# Initial stage
		if country is None:
			country = df
		else:
			put_date_aside = df['Date']

			# Drop date columns because they cannot be added, only numbers
			df = df.drop('Date', axis=1)
			country = country.drop('Date', axis=1)

			# Combine df with country dataframes
			country = country.add(df, fill_value=0)
			country.insert(0, 'Date', put_date_aside)

		country = country.dropna()
		regions[region] = regions[region].dropna()
		write_csv('dataset/processed/', region, regions[region])

	regions['Entire Country'] = country
	write_csv('dataset/processed/', 'Entire Country', regions['Entire Country'])


def region_wide(sheet, filename):
	df = pd.read_excel(filename, index_col=None, header=0, sheet_name=sheet)
	columns = df.keys()

	# Rename columns to clean names
	for c in columns:
		column = c.strip()
		column_names.add(column)
		df = df.rename(columns={c: c.strip()})

	# Trim dataframe to valid rows
	start_date = df['Date'][0]
	rows = valid_rows(start_date)
	df = df[:rows]

	if sheet in regions:
		regions[sheet] = regions[sheet].append(df, ignore_index=True)
	else:
		regions[sheet] = df


# Read the data from Excel files
def import_data(root):
	files = sorted(os.listdir(root))
	for file in files:
		# Just in case you open an excel file for viewing and never close it,
		# Excel create a temporary file starting with `~$`. Thus exclude such
		# files just in case they exist
		if file.endswith('.xlsx') and not file.startswith('~$'):
			filename = os.path.join(root, file)
			sheets = pd.read_excel(filename, sheet_name=None).keys()
			for sheet in sheets:
				# Process data into regions
				if file.startswith('2020'):  # Process all of 2020 data
					if sheet == 'Karas':
						sheet = 'Kharas'
					region_wide(sheet, filename)
				elif file.startswith('2021'):
					if sheet == 'Khomas':  # Only process one region, Khomas [2021]
						region_wide(sheet, filename)


def read_data():
	global column_names, regions
	files = os.listdir('dataset/processed/')
	for file in files:
		if file.endswith('.csv'):
			filepath = os.path.join('dataset/processed', file)
			df = pd.read_csv(filepath, index_col=0)
			df['Date'] = pd.to_datetime(df['Date'])
			column_names = df.columns.values
			regions[file.split('.')[0]] = df


def process_data():
	global column_names
	import_data('dataset/raw/')
	# Process data into country
	country_wide()
	column_names = list(column_names)
