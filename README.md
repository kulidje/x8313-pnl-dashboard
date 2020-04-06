# X8313 P&L Dashboard
Showcasing key functionality from X8313 Inc: P&L data-vis dashboard built on Plotly for tracking daily betting with custom dates and strategy filtering

![](gif_pnl_dashboard.gif)

**Key Features**

* Man vs. Machine Tracking (what is the error in our Simulator(), if any, from true p&l reports)
* Strategy Selection

**Instructions**<br>
_Please note the app requires Python Version 3.6_

1. `git clone` this repository
1. run `pip install virtualenv` to install virutalenv if you don't have it installed already
1. `which python3.6` and copy the output to the clipboard - let's call it {output}
1. `cd x8313-pnl-dashboard` so that you are in the repo and run `virtualenv --python={output} env_pnl_dashboard` to create a virtual environment
1. run `source env_pnl_dashboard/bin/activate` to activate the virtual environment
1. run `pip install -r requirements.txt` to install all package requirements
1. run `python application.py` inside of the directory to start the app
1. in any browser, go to http://127.0.0.1:8080/
