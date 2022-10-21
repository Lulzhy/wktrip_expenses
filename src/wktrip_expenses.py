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
    message = None

    # Set path of history to script directory:
    hist_path = os.path.realpath(os.path.dirname(__file__)) \
                + '/' + args.history_name
    logging.debug(f'History path: {hist_path}.')

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
                add_day(hist_path, history, args.date,
                           args.distance)
                message = 'New day successfully added in history.'
            except KeyError as error:
                exit_gracefully(UNKNOWN, error)
        case 'calculate':
            # Set path of config to script directory:
            config_path = os.path.realpath(os.path.dirname(__file__)) \
                + '/config.json'
            logging.debug(f'Config path: {config_path}.')

            try:
                config = get_config(config_path)
            except FileNotFoundError:
                exit_gracefully(UNKNOWN, 'Config file is missing.')
            except IOError as error:
                exit_gracefully(UNKNOWN, error)

            calculate(history, config, args.year, args.power)
        case 'remove':
            if history:
                remove_day(hist_path, history, args.date)
                message = 'Day successfully removed from history.'
            else:
                exit_gracefully(
                    UNKNOWN, 'There is no history yet, can\'t remove travel.')

    # End program:
    exit_gracefully(OK, message)


def get_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', help='Set verbosity level: [-v|vv|vvv].', 
                        action='count', default=0)
    parser.add_argument('--history-name', type=str,
                        help='Set history filename, default is work_trip.json',
                        default='work_trip.json',
                        dest='history_name')
    
    # Defines commands available:
    subparser = parser.add_subparsers(dest='command')
    add = subparser.add_parser(
        'add', help='Add a new day of work trip (total distance that day).')
    calculate = subparser.add_parser(
        'calculate',help='Return the amount to report to IRS for given year.')
    remove = subparser.add_parser(
        'remove', help='Remove a day recorded in history file.')

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
        help='Fiscal power of vehicle, possible values : [3, 4, 5, 6, 7]',
        required=True)

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
    logging.debug(f'Parsed argument: {args}.')

    return args


def get_history(filename):
    """Read history file and return its content
    or an empty list if doesn't exist.
    """
    logging.debug(f'Filename: {filename}.')
    
    try:
        with open(filename) as json_pointer:
            logging.info('History file loaded in memory.')
            return json.load(json_pointer)
    except FileNotFoundError:
        logging.warning('There is no history file yet.')
        return []
    except IOError:
        raise


def get_config(filename):
    """Read config file and return its content ; file is required."""
    logging.debug(f'Filename: {filename}.')

    try:
        with open(filename) as json_pointer:
            logging.info('Config file loaded in memory.')
            return json.load(json_pointer)
    except FileNotFoundError:
        logging.error('Config file is missing.')
        raise
    except IOError:
        raise


def add_day(filename, history, date, distance):
    """Add new day to history."""
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

    logging.info('Travel recorded in history.')


def calculate(history, scale, year, vehicle_power):
    """Calculate travel expenses from history for the year in argument."""
    logging.debug(f'Year: {year}, Horsepower: {vehicle_power}.')

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
            logging.error(f'There is no record for year: {year}.')

        # According to power, multiply distance by corresponding coeff.:
        if cumulation <= KM_MIN:
            index = 0
        elif KM_MIN < cumulation <= KM_MAX:
            index = 1
        else:
            index = 2
        coeff = scale[vehicle_power][index]['coeff']
        term = scale[vehicle_power][index]['term']
        logging.debug(
            f'Coefficient found: {coeff}, Term found: {term}.')
        
        expenses = (cumulation*coeff) + term
        print(f'The amount to report is {expenses}€.')
    else:
        logging.error('There is no history yet, can\'t calculate expenses.')


def remove_day(filename, history, date):
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
        logging.info('Travel removed from history.')
    else:
        raise NoHistoryForDateError(
            f'No travel found with date {date_str}.')


def write_history(filename, content):
    """Write content to JSON history file."""
    try:
        with open(filename, 'w', encoding='utf-8') as json_pointer:
            json.dump(content, json_pointer, ensure_ascii=False, indent=4,    
                      sort_keys=True)
            logging.debug('History modified.')
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