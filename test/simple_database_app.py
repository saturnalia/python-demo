# database.py
import sys, shelve

def store_person(db):
	"""
	Query user for data and store it in the shelf object
	"""
	pid = raw_input('Enter unique ID number: ')
	person = {}
	person['name'] = raw_input('Enter name: ')
	person['age'] = raw_input('Enter age: ')
	person['phone'] = raw_input('Enter phone number: ')
	db[pid] = person


def lookup_person(db):
	"""
	Query user for ID and desired field, and fetch the corresponding data from
	the shelf object
	"""
	pid = raw_input('Enter ID number: ')
	field = raw_input('What would you like to know? (name, age, phone) ')
	field = field.strip().lower()

	print field.capitalize() + ':', \
	db[pid][field]


def print_help():
	print 'The available commands are:'
	print '\tstore : Stores information about a person'
	print '\tlookup : Looks up a person from ID number'
	print '\tquit : Save changes and exit'
	print '\t? : Prints this message'


def enter_command():
	cmd = raw_input('Enter command (? for help): ')
	cmd = cmd.strip().lower()
	return cmd


def main():
	database = shelve.open('C:\\project\\python\\test\\database.dat') # You may want to change this name
	try:
		while True:
			cmd = enter_command()
			if cmd == 'store':
				store_person(database)
			elif cmd == 'lookup':
				lookup_person(database)
			elif cmd == '?':
				print_help()
			elif cmd == 'quit':
				return
			else:
				print "unknown command"				
	finally:
		database.close()


if __name__ == '__main__': 
	main()
