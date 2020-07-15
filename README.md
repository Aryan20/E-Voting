# E-Vote 

E-Vote is an online voting site made for the sake of improving the voting procedures used currently as E-voting is not only cost effective but it is also faster and could attract more voters.

## Preview
![Homepage preview](preview/home.png)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You will need to install the following programs and libraries to run the website on your local machine.

```
Python
Flask
Flask_session
javascript
```

To install requirements use command -
`pip install -r requirements.txt`

Website folder already contains files required to run javascript.

### Installing

A step by step series of examples that tell you how to get a development env running

Open the directory where you have saved this site 

Now do `SHIFT + Right Click` and then select either powershell or command prompt according to your convinience

Now in the terminal window of your choice type -

```
flask run
```

And hit enter

now you will see a bunch of text along with a IP address on your terminal window copy it and paste it onto your browser url box

![powershell preview](preview/powershell.png)

Typically it is -

```
127.0.0.1:5000/
```

After this you will see a webpage opening.

### Using The site

The home page of website is located at
```
127.0.0.1:5000/
```
On the website click sign In to login there you will have options to register as a candidate or as a normal voter

after you have successfully registered and logged in you will be redirected to - 
```
127.0.0.1:5000/vote
```

Once you have voted you will not be able to vote again until your vote status is reset before the next election. 

Once voted you will be redirected to - 
```
127.0.0.1:5000/main
```
Where you will be able to access the current status of election.



## Built With

* [Flask]() - The web framework used
* [Python](https://www.python.org/) - As Controller
* [Bootstrap](https://getbootstrap.com/) - Used to design the page
* [Javascript]() - To make website responsive
* [HTML and CSS]() - As backbone


## Authors

* **Aryan Kaushik** - *Developer and Creator* - [Aryan20](https://github.com/Aryan20)


## Acknowledgments

* CS50x course for knowledge of flask
