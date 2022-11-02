# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Possibility to generate days in a range for recurring travels on weekdays. 
- Global vars like vehicule power and min/max km in `config.json` (persistence + flexibility if the scale changes).

## [0.2.1] - 2022-10-31
### Fixed
- Change in calculate function : the `cumulation` var was use in a case with no history for the given year. Thus the execution would raise an uncaught exception.