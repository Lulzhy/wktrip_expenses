#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import logging
import argparse
import os
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


###### CUSTOM EXCP ######
class NoHistoryForDateError(Exception):
    """Custom exception in the case there is no content for date
    in history file."""
    # Disable traceback
    sys.tracebacklimit = 0
###### CUSTOM EXCP ######


def main():
    """Main logic of the program."""
    args = get_args()
    command = args.command

    # Set path of history to script directory:
    hist_path = os.path.realpath(os.path.dirname(__file__)) \
                + '/' + args.history_name

    # Load history file with every travels in memory:
    try:
        history = get_history(hist_path)
    except IOError as error :
        exit_gracefully(UNKNOWN, error)
    except KeyError as error:
        exit_gracefully(UNKNOWN, error)

    # Switch according to command arg:
    match args.command:
        case 'add':
            try:
                add_travel(hist_path, history, args.date,
                           args.distance)
            except KeyError as error:
                exit_gracefully(UNKNOWN, error)
        case 'remove':
            if history:
                remove_travel(hist_path, history, args.date)
            else:
                exit_gracefully(
                    UNKNOWN, 'There is no history yet, can\'t remove travel')
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
    calculate = subparser.add_parser(
        'calculate',
        help='Return the travel expenses for the year')
    remove = subparser.add_parser('remove',
                                  help='Remove travel from history file')

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

    # Arguments for remove command:
    remove.add_argument(
        '--date',
        type=lambda d: datetime.strptime(d, '%d/%m/%Y').date(),
        help='Date in dd/mm/yyyy format', required=True
    )

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
    write_history(filename, history)


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


def remove_travel(filename, history, date):
    """Remove travel from history."""
    logging.debug(f'Filename: {filename}, Date: {date}')

    # Get travel for the date if exists:
    date_str = date.strftime('%d/%m/%Y')
    history_filter = list(filter(lambda travel: travel['date'] == date_str, 
                                 history['travels']))

    # From filter, delete in history:
    if history_filter:
        for date in history_filter:
            try:
                history['travels'].remove(date)
            except ValueError:
                pass
        write_history(filename, history)
    else:
        raise NoHistoryForDateError(
            f'No travel found with date {date_str}.')


def write_history(filename, content):
    """Write content to JSON history file."""
    try:
        with open(filename, 'w', encoding='utf-8') as json_pointer:
            json.dump(content, json_pointer, ensure_ascii=False, indent=4,    
                      sort_keys=True)
            logging.debug('Writing in history done.')
    except IOError:
        raise


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