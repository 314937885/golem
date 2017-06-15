[![Build Status](https://travis-ci.org/lucianopuccio/golem.svg?branch=master)](https://travis-ci.org/lucianopuccio/golem)

Golem - Test Automation Framework
==================================================

Intro
--------------------------------------

Golem is a test automation framework for functional tests. It has a GUI (a web application) that enables the creation of new tests in an easy an intuitive way. Implements the best practices in test automation such as keyworddriven, datadriven and Page Objects pattern. I'ts written in python and uses Selenium-Webdriver as the automation engine.


Installation
--------------------------------------

Currently Golem is only guaranteed to work with Python 3.4+, you may download and install it from here [python.org/downloads/](http://www.python.org/downloads/)


##### **1. Clone the Golem repo and install**

Create a directory anywhere in your system:

```
mkdir golemroot && cd golemroot
```

```
git clone https://github.com/lucianopuccio/Golem.git golem
```


##### **2. Using virtualenv**

It is optional but recommended to install Golem and it's dependencies in a [virtual environment](http://www.virtualenv.org/en/latest/) instead of globally.

```
virtualenv env
```

- **Windows**:

```
env\scripts\activate
```

- **Mac/Linux**:

```
source env/bin/activate
```

##### **3. Install Golem using pip **

```
pip install https://github.com/lucianopuccio/golem/archive/0.1.0a3.tar.gz
```

# QuickStart
--------------------------------------
#### **1. Create the test projects root directory**

A directory must be created to contain the projects, tests and required files. Open a console wherever you want the new directory to be.


**Create the test directory:**

```
golem-admin createdirectory <directory_name>
```

This will create a folder that will contain all subsequent projects.


##### **2. Create a new project**

Next, create a **new** project inside the test directory
```
cd <directory_name>
python golem.py createproject <project_name>
```

##### **3. Start the GUI**

To start the Golem GUI run the following command:

```
python golem.py gui
```

The GUI can be accessed at http://localhost:5000/

By default, this is the first user available: user: **admin** / password: **admin**



See the full documentation: [https://github.com/lucianopuccio/golem/wiki/Golem---Documentation](https://github.com/lucianopuccio/golem/wiki/Golem---Documentation)
