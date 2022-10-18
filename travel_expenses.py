#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import logging
import argparse
import json
import sys

from datetime import datetime
from datetime import date


###### GLOBAL VARS ######
OK = 0
UNKNOWN = 1
MAX_DISTANCE = 40
KM_MIN = 5000
KM_MAX = 20000
#########################


def main():
    """Main logic of the program."""
    args = get_args()
    command = args.command

    # Load history file with every travels in memory:
    try:
        history = get_history(args.history_name)
    except IOError as error :
        exit_gracefully(UNKNOWN, error)
    except KeyError as error:
        exit_gracefully(UNKNOWN, error)

    # Switch according to command arg:
    match args.command:
        case 'add':
            try:
                add_travel(args.history_name, history, args.date,
                           args.distance)
            except KeyError as error:
                exit_gracefully(UNKNOWN, error)
        case 'remove':
            pass
        case 'calculate':
            calculate(history, args.year, args.power)

    # End program:
    exit_gracefully(OK, None)


def get_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', help='Set verbosity level: [-v|vv|vvv] ', 
                        action='count', default=0)
    parser.add_argument('--history_name', type=str,
                        help='Set history filename',
                        default='travel_expenses.json')
    
    # Defines commands available:
    subparser = parser.add_subparsers(dest='command')
    add = subparser.add_parser('add', help='Add travel to history file')
    remove = subparser.add_parser('remove',
                                  help='Remove travel from history file')
    calculate = subparser.add_parser(
        'calculate',
        help='Return the travel expenses for the year')

    # Arguments for add command:
    add.add_argument(
        '--date',
        type=lambda d: datetime.strptime(d, '%d/%m/%Y').date(),
        help='Date in dd/mm/yyyy format', required=True)
    add.add_argument('--distance', type=float,
                     help='Total distance traveled in Km this day',
                     required=True)

    # Arguments for calculate command:
    current_year = date.today().year
    calculate.add_argument(
        '--year', 
        type=lambda d: datetime.strptime(d, '%Y').date().year,
        help='Year in yyyy format', required=True)
    calculate.add_argument(
        '--power',
        type=str, 
        choices=['3', '4', '5', '6', '7'],
        help='Vehicle power [3, 4, 5, 6, 7]', required=True)

    args = parser.parse_args()

    # Set verbosity and display args:
    logging.getLogger().setLevel([logging.ERROR, logging.WARN,
                                  logging.INFO, logging.DEBUG][args.v])
    logging.debug(f'Parsed argument: {args}')

    return args


def get_history(filename):
    """Read history file and return its content
    or an empty list if doesn't exist.
    """
    logging.debug(f'Filename: {filename}')
    
    try:
        with open(filename) as json_pointer:
            return json.load(json_pointer)
    except FileNotFoundError:
        logging.debug('There is no history file yet.')
        return []
    except IOError:
        raise


def add_travel(filename, history, date, distance):
    """Add new travel to history."""
    logging.debug(f'Filename: {filename}, Date: {date}, Distance: {distance}.')

    date_str = date.strftime('%d/%m/%Y')
    if history:
        # Control if there is no travel already recorded for the date:
        history_filter = filter(lambda travel: travel['date'] == date_str, 
                                history['travels'])
        if list(history_filter):
            raise KeyError('There already is a record for the same date.')
    else:
        history = {'travels': []}

    # Add travel to list and write history file:
    new_travel = {'date': date.strftime('%d/%m/%Y'), 'distance': distance}
    history['travels'].append(new_travel)
    try:
        with open(filename, 'w', encoding='utf-8') as json_pointer:
            json.dump(history, json_pointer, ensure_ascii=False, indent=4,    
                      sort_keys=True)
            logging.debug('Adding travel in history done.')
    except IOError:
        raise


def calculate(history, year, vehicle_power):
    """Calculate travel expenses from history for the year in argument."""
    logging.debug(f'Year: {year}.')

    if history:
        # Get every expenses for the year from history file:
        travels_year = list(filter(lambda travel: str(year) in travel['date'],
                                   history['travels']))
        
        # Cumulate distance for each travel in the year:
        if travels_year:
            cumulation = 0
            for index, dic in enumerate(travels_year):
                distance = travels_year[index]['distance']
                if distance > MAX_DISTANCE:
                    cumulation += MAX_DISTANCE
                else:
                    cumulation += distance
            logging.debug(f'Cumulation: {cumulation}km in {year}.')
        else:
            logging.warning(f'There is no record for year: {year}.')

        # According to power, multiply distance by corresponding coeff.:
        if cumulation <= KM_MIN:
            index = 0
        elif KM_MIN < cumulation <= KM_MAX:
            index = 1
        else:
            index = 2
        coeff = history[vehicle_power][index]['coeff']
        term = history[vehicle_power][index]['term']
        logging.debug(
            f'Coefficient found: {coeff} (for power: {vehicle_power} index {index}).')
        logging.debug(
            f'Term found: {term} (identical keys).')
        
        expenses = (cumulation*coeff) + term
        print(f'The amount of travel expenses to declare is {expenses}€.')
    else:
        logging.warning('There is no history yet, can\'t calculate expenses.')


def exit_gracefully(exitcode, message=None):
    """Exit program with rcode and message (optionnal)."""
    logging.debug(f'Exiting with code {exitcode}, message: {message}.')

    if message:
        print(message)
    sys.exit(exitcode)


if __name__ == '__main__':
    # Configure logging before hitting main (DEBUG):
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(funcName)s line %(lineno)d [%(levelname)s] : %(message)s')
        
    main()