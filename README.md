# lcd_lms.py
A python script to glue the Logitech Media Server CLI to LCDd.  
It is based on the perl script lcd_lms.pl (https://github.com/jscrane/lcd_lms).

The main reasons for porting the Perl script to Python were:
* the inbuilt unicode support
* no need to build/install CPAN modules
* my limited Perl skills ;)
## Installation
1. Install piCoreplayer (https://www.picoreplayer.org/) and the python3 extension  
   (may work on other platforms / distros as well)
2. Install and configure LCDproc (https://github.com/lcdproc/lcdproc)  
   (instructions: https://vonzeppelin.net/viewtopic.php?p=10&sid=9bf3a4ac3de374c30e86ee74d661d893#p10)
3. Configure/run script

## Usage
Type

    lcd_lms.py --help

to get a list of the available options.

To start the script automatically: Put it into the User Commands section of piCorePlayer. Maybe, you want to use the '-c' option along with a configuration file.
## ToDo
A lot...
