# GOAL
The goal of this python script is to keep track of work trip (by car/motorbike) and calculate these travel expenses according to [French government scale](https://www.service-public.fr/particuliers/actualites/A14686).

# HOW-TO USE
## Functions available
- `add` total distance for a work day. Required arguments are :
    - `--date` : work day concerned, format : dd/mm/yyyy
    - `--distance` : distance in Km, decimal number
- `calculate` return for the given year the expense to declare to IRS. Required arguments are :
    - `--year`
    - `--power` : fiscal power of the vehicle, to choose in [3, 4, 5, 6, 7]
- `remove` a day from history. Required argument is :
    - - `--date` : day to remove, format : dd/mm/yyyy

## Other arguments
- `[-v|vv|vvv]` set the verbosity. Default is only error message, then WARN (`-v`)/INFO (`-vv`)/DEBUG(`-vvv`).
- `-history-name` defines the name of history file (JSON formatted). Default is `work_trip.json`.

## config.json
It is required to have this file beside the script as it used in calculate command. Within you can modify the scale in the case IRS would change its rules.

By default the configuration is for cars, you need to manually change it if you use a motorbike.

## Examples
- Get help
    ```console
    $ ./src/wktrip_expenses.py -h
    usage: wktrip_expenses.py [-h] [-v] [--history-name HISTORY_NAME] {add,calculate,remove} ...

    positional arguments:
    {add,calculate,remove}
        add                 Add a new day of work trip (total distance that day).
        calculate           Return the amount to report to IRS for given year.
        remove              Remove a day recorded in history file.

    options:
    -h, --help            show this help message and exit
    -v                    Set verbosity level: [-v|vv|vvv].
    --history-name HISTORY_NAME
                            Set history filename, default is work_trip.json

    $ ./src/wktrip_expenses.py add -h
    usage: wktrip_expenses.py add [-h] --date DATE --distance DISTANCE

    options:
    -h, --help           show this help message and exit
    --date DATE          Date in dd/mm/yyyy format
    --distance DISTANCE  Total distance traveled in Km this day
    ```
- `add` command
    ```console
    $ ./src/wktrip_expenses.py add --date 16/10/2022 --distance 41.8
    New day successfully added in history.
    ```
- `remove` command with verbose=INFO
    ```console
    $ ./src/wktrip_expenses.py -vv remove --date 16/10/2022
    2022-10-21 17:27:42,207 get_history line 151 [INFO] : History file loaded in memory.
    2022-10-21 17:27:42,210 remove_day line 254 [INFO] : Travel removed from history.
    Day successfully removed from history.
    ```
- `calculate` command
    ```console
    $ ./src/wktrip_expenses.py calculate --year 2022 --power 5
    The amount to report is XXX.X€.
    ```


# COMING CHANGE(S)
Currently it is not possible to :
- ~~remove a date in history~~ :heavy_check_mark: done in 0.2.0
- add multiple travel in one execution of the script

Also some refactoring/bug correction (calculate function especially) needed.