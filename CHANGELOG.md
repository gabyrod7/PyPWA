# Changelog
All changes important to the user will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/)

## "Unreleased"
### Added
 - Argument Parser for simple programs where a configuration file would be
   unneeded overhead for the user.
 - Numpy Data support for single arrays and pass fail files.
 - Data Plugin now has two array types, Single Array and Columned Array
### Changed
 - Plugin Loader now returns initialized objects
 - Renamed shell to progs
 - Moved all shell related items into a package called shell inside progs
 - Renamed CHANGELOG.mg to CHANGELOG.md
 - Renamed 'blank shell module' to 'blank program module'
 - Removed support for boolean and float arrays from EVIL Parser
 - Renamed internal GAMP type to Tree type
### Fixed
 - ChiSquare and Empty likelihoods are now actually usable
### Security

## [2.0.0] - 2017-6-5
### Added
 - Plugin Subsystem
 - Configurator Subsystem
 - Data Plugin
 - SV Plugin
 - EVIL Plugin
 - GAMP Plugin
 - Data Caching
 - Processing Plugin
 - iMinuit plugin
 - Nestle likelihood
 - PyFit plugin
 - Log Likelihood Plugin
 - Chi-Squared Likelihood
 - PySim plugin
 - Packaging

[2.0.0]: https://github.com/JeffersonLab/PyPWA/compare/v1.1...v2.0.0