Mining-Ministers
================

This directory provides data and scripts used for investigating data in Fred van Lieburg's corpus.

=====
Citations
=====


repertorium-original.doc contains the corpus as provided by Fred van Lieburg. If you make use of this corpus, please cite:

Van Lieburg, Fred (2014). Database Dutch Reformed Clergy 1555-2004.

=====
The paper ``Mining Ministers (1572-1815). Using semi-structured data for historical research'' 
=====

The data and scripts in this directory were used to perform the analyses in the paper  ``Mining Ministers (1572-1815). Using semi-structured data for historical research'' by Serge ter Braake, Antske Fokkens and Fred van Lieburg (currently under review). 

Disclaimer 
========
This code was written in very busy times and under deadline stress. It is ill-documented, ill-structured and contains hacks. It will be improved step by step where changes that have an impact on the outcome of the results will be reported. Please consult 'contents' for an indication of how to use the scripts and recreate results.

If you want to use the exact same versions of the scripts that were used for the paper, please go to commit 85dff8317e30bb2d035c86b6f0e0a6e4d9ed9bcd


=====
Contents
=====

Scripts:
- convertRepertorium2tsv.py
Converts the flat text data from `repertorium-rawtext.txt', extracts information and prints it to `priest_info_all_ids.tsv'
It also creates a file `alternativepreds.txt' where positions that contain the Dutch abbreviation for minister (``pred''), but are not represented in standard form.
It assumes the files `repertorium-rawtext.txt' and `geoNamesInLieburgCorpus.txt' are present in the same directory and outputs  `priest_info_all_ids.tsv' and `alternativepreds.txt'  in the same directory (overwriting files with that name that are already there). Soon these paths will no longer be hardcoded in the files.

- createLocationInformation.py
Goes through `repertorium-rawtext.txt', retrieves all potential locations and looks them up in GeoNames (stored as a .tsv file), it then creates the file `geoNamesInLieburgCorpus.txt' which lists all names of potential locations found in the repertorium followed by all geoNames entries that can be called by that name.
You need to download allCountries.zip from http://download.geonames.org/export/dump/, unzip it and change '../GeoNames/allCountries.txt' to your location of allCountries.txt inthe following line in createLocationInformation.py:

geoNamesData = open('../GeoNames/allCountries.txt','r')

Again, the code assumes that  `repertorium-rawtext.txt' is located in the same directory and prints the file `geoNamesInLieburgCorpus.txt' in this directory, overwriting existing ones.


