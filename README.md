# software
The computer-side app of smartbench project.
A multi-platform software for data acquisition.

Installing the framework, API, widgets, etc:

Ubuntu ->
	Kivy ->
		sudo add-apt-repository ppa:kivy-team/kivy
		sudo apt update
		sudo apt install python-kivy python3-kivy
	pip  ->
		sudo apt install python-pip
	Kivy Garden ->
		pip install kivy-garden
	Kivy Garden graph ->
		garden install graph
		garden install --upgrade graph
	Kivy Garden MatPlotLib ->
		sudo apt install python-matplotlib
		garden install matplotlib
		garden install --upgrade matplotlib
    Kivy Garden Knob ->
        sudo garden install knob
        sudo garden install --upgrade knob


# Possible issues
    Error: "TypeError: register_backend() takes exactly 2 arguments (3 given)"
    The matplotlib version installed is old and has a different definition for 'register_backend()' (and maybe also for others).
    This can be solver by compiling and installing the library from source.
    - install python-dev
        sudo apt install python-dev python3-dev
    - Download the source code of matplotlib v2.0.2 from https://matplotlib.org/2.0.2/users/installing.html
    - Uncompress and run:
        python setup.py build
        sudo python setup.py install
