# Engine comparison
Allows comparison between validation engines by displaying the myPlant data and other calculated values of different engines in one plot.  
After initial setup a custom set of plots can be created easily and stored in a html file.


## Recommended usage

For every validation to be monitored create a new subfolder.

Copy the Excel file and either the Python file (.py) file or the Jupyter Notebook (.ipynb) into each subfolder.

Modify the Excel input to your liking:
* Pass the validation engines in 'Engines'
* Define the desired plots in 'Pltcfg'
* Adjust other settings in 'Variables'

Run the code in each subfolder seperatly (Excel file has to be closed) -> the generated html-file is stored in each subfolder respectivly

__Adding calculated values__
To add calculated values, search for "Add custom value" in the code and add code according the instructions at the two places.  
Then these values can be accessed like any other value from the Excel sheet.  
Feel free to make a pull request/ issue with your calculations.

## Release History

-  1.0: First released version (01.06.21)
-  1.1: Bugfixes
-  1.2: Added statistics tab (01.07.21)


