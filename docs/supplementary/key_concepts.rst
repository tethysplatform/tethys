************
Key Concepts
************

**Last Updated:** April 6, 2015

The purpose of this page is to provide an explanation of some of the key concepts of Tethys Platform. The concepts are only discussed briefly here to provide a basic overview. It is highly recommended that you visit the suggested resources to have a better understanding of these concepts, as developing apps in Tethys Platform relies heavily on them.

What is an App?
===============

In the most basic sense, an app is a workflow. The purpose of an app is not provide an all-in-one solution, but rather to perform a narrowly focused task or set of tasks. For example, an app that works with hydrologic models might be focused on guiding the user to change the land use layer of a model, run the modified model, and compare the result with the original model results.

In terms of implementation, an app built with Tethys Platform or a Tethys app is a web app( as opposed to a mobile app). A Tethys Platform installation provides a website called the Tethys Portal that can be used to organize and access your apps. Tethys apps are technically extensions of the Tethys Portal web page, because when you create a Tethys app you will be adding additional web pages to the Tethys Portal web site. Tethys Platform is built on the Django Python web framework, so Tethys apps are also Django web apps--though Tethys Platform streamlines many aspects of Django web development. This is why the Django documentation is referred to often in the documentation for Tethys Platform.

Web Frameworks
==============

Tethys Portal is built using the `Django <https://www.djangoproject.com>`_ web framework. Understanding the difference between a static website and a dynamic website built with a web framework is important for app developers, because apps rely on web framework concepts.

Static web development consists of creating a series of HTML files--one for every page of the website. The files are organized using the server’s file system and stored in some directory on the server that is accessible by the Internet. For a static site, the URL works very similar to how a file path works on an operating system. When a request is sent from the web browser to a server, the server locates the HTML file that the URL is requesting and returns it to the browser for the user to view.

The static method of developing web pages presents some problems for developers. For example, if a developer wants to include a consistent header and footer on every page of her website, she would end up duplicating the header and footer code many times (via copy and paste). As a result, static websites are more difficult to update and maintain, because changes need to be made wherever the code is duplicated. Developing a website in this way is error prone and can become prohibitive for large websites.

Web frameworks provide a way to develop websites using a programmatic approach. Instead of static HTML files, developers create generic reusable HTML templates. With a web framework, the developer can create one template file containing only the markup for the header and another template file for the footer. Now when the developer wants to include the header and footer in another page, she uses an import construct that references the header and footer templates. The header and footer markup is added dynamically to all the files that need it upon request by a template rendering program. Maintenance is much easier, because changes to the header and footer only need to be made in one place and the entire site will be updated. In this way, the site becomes dynamic. One type of software that makes it possible to create dynamic web pages is a web framework.

Web frameworks also handle requests differently than traditional web pages. When the user submits a request to the server, instead of looking up a file on the server at the directory implied by the URL, the request is handed to the web framework application. The web framework application processes the request and usually returns a web page that has been generated dynamically as the result. This type of web framework application is called a `Common Gateway Interface (CGI) <https://en.wikipedia.org/wiki/Common_Gateway_Interface>`_ application; or if the application is a Python web framework, it is called a `Web Server Gateway Interface (WSGI) <https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface>`_  or `Asynchronous Server Gateway Interface (ASGI) <https://asgi.readthedocs.io/en/latest>`_ application.

Model View Controller
---------------------

The dynamic templating feature is only one aspect of what web frameworks offer. Many web frameworks use a software development pattern called `Model View Controller (MVC) <https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller?oldformat=true>`_. MVC is used to organize the code that is used to develop user interfaces into conceptual components. A brief explanation of each components is provided:

Model
+++++

The model represents the code that is used to store and retrieve data that is used in the web application. Most websites use SQL databases for persistent data storage, so the model is usually made up of a database model.

View
++++

Views are used to represent the data to the end user. In a web applications views are the HTML pages that are generated. Views are typically generic, reusable, and oblivious to the origins of the data that fills them. This is possible because of templating languages that allow coders to create dynamic HTML web pages.

Controller
++++++++++

Controllers are used to orchestrate the interaction between the view and the model. They contain the logic for retrieving data from the database and transforming it into a format that is consumable by the view, because the model and the view never communicate directly. Controllers also handle the input from the user.

.. figure:: ../images/basic_mvc.png
    :align: center

    A typical collaboration of MVC components (courtesy of `Cake PHP Docs <https://book.cakephp.org/2/en/cakephp-overview/understanding-model-view-controller.html>`_)

When a user submits a request, the web application (dispatcher in the Figure above) looks up the controller that is mapped to the URL and executes it. The controller may perform change or lookup data from the model after which it returns this data and a template to render. This is handed off to a template rendering utility that processes the template and generates HTML. The HTML is rendered for the user's viewing pleasure in the web browser or other client. The user sends another request, and the process repeats.

URL Design and REST Paradigm
============================

The URL takes on a different meaning in dynamic websites than it does in a static website. In a static website, the URL maps to directories and files on the server. In a dynamic website, there are no static files (or at least very few) to map to. The web framework simply maps the URL to a controller and returns the result. Although the developer is free to use URL’s in whatever manner they would like, it is recommended that some type of URL pattern should be used to make the website more maintainable.

We recommend developers use some form of the Representational State Transfer (REST) abstraction for creating meaningful URLs for apps. In a REST architecture for a website, the data of the website is referred to as resources. The current state of resources is presented to the user through some representation, for example, an HTML document. The user can interact with the resources through the actions of the controller. Examples of common actions on resources are create, read (view), update (edit), and delete, often referred to as CRUD. In true REST implementations, the CRUD operations are mapped to specific HTTP methods: POST, GET, PUT, and DELETE, respectively (see `HTTP Verbs`_). In practice HTML only supports the POST and GET HTTP methods, so a pseudo-REST implementation is achieved via URL patterns.

For example, consider an app that is meant to provide information about a stream gages. In this case, the resources of the website may be stream gage records in a database. A potential URL for a page that shows a summary about a single stream gage record would be:

::

	www.example.com/gages/1/show

The number "1" in the URL represents the stream gage record ID in the database. To show a page with the representation of another stream gage, the ID number could be changed. A generalization of this URL pattern could be represented as:

::

	/gages/{id}/{action}

In this URL pattern, variables are represented using curly braces. The ``{id}`` variable in the URL represents the ID of a stream gage resource in our database and the ``{action}`` variable represents the action to perform on the stream gage resource. The ``{action}`` variable is used instead of HTTP methods to indicate which CRUD operation to perform on the resource. In the first example, the action "show" is used to perform the read operation. Often, the show action is the default action, so the URL could be shortened to:

::

	www.example.com/gages/1

Similarly, a URL for a page the represents all of the stream gages in the database in a list could be represented by omitting the ID:

::

	www.example.com/gages


URLs for each of the CRUD operations on the steram gage database could look like this:
	
::

	# Create
	www.example.com/gages/new

	# Read One
	www.example.com/gages/1

	# Read All
	www.example.com/gages

	# Update
	www.example.com/gages/1/edit

	# Delete
	www.example.com/gages/1/delete

Before you dive into writing your app, you should take some time to design the URLs for the app. Define the resources for your app and the URLs that will be used to perform the CRUD operations on the resources.

.. caution::

    The examples above used integer IDs for simplicity. However, using integer IDs in URLs is not recommended, because they are often incremented consecutively and can be easily guessed. For example, it would be very easy for an attacker to write a script that would increment through integer IDs and call the delete method on all your resources. A better option would be to use randomly assigned IDs such as a `UUID <https://en.wikipedia.org/wiki/Universally_unique_identifier?oldformat=true>`_.

HTTP Verbs
----------

Anytime you type a URL into an address bar you are performing what is called a GET request. All of the above URLs are examples of implementing REST using only GET requests. GET is an example of an HTTP verb or method. There are quite a few HTTP verbs, but the other verbs pertinent to REST are POST, PUT, and DELETE. A truely RESTful design would make use of these HTTP verbs to implement the CRUD for the resources instead of using different key word actions. Consider our example from above. To read or view a dog resource, we use a GET request as before:

::
	
	HTTP GET
	www.example.com/dogs/1

However, to implement the create action for a dog resource, now we use the POST verb with the same url that we used for the read action:

::

	HTTP POST
	www.example.com/dogs/1

Similarly, to delete the dog resource we use the same URL as before but this time use the DELETE verb and to update or edit a dog resource, we use the PUT verb. Using this pattern, the URL becomes a unique resource identifier (URI) and the HTTP verbs dictate what action we will perform on the data. Unfortunately, HTML (which is the interface of HTTP) does not implement PUT or DELETE verbs in forms. In practice many RESTful sites use the "action" pattern for interacting with resources, because not all of the HTTP verbs are supported.






