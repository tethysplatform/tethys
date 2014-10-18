************
Key Concepts
************

**Last Updated:** May 20, 2014

The purpose of this page is to provide an explanation of some of the key concepts behind the Tethys Apps plugin and SDK. The concepts are only discussed briefly here to provide you with the basic overview. It is highly recommended that you visit the suggested resources to gain a deeper understanding of these concepts, as the Tethys Apps plugin relies heavily on them.

What is an App?
===============

In the most basic sense, an app is a workflow. The purpose of an app is not provide an all-in-one solution, but rather to perform a narrowly focused task or set of tasks. For example, an app that works with hydrologic models  might be focused on guiding the user to change the land use layer of a model, run the modified model, and compare the result with the original model results. 

In terms of implementation, a Tethys App is an extension of the CKAN website. In other words, a Tethys App adds additional webpages to CKAN. For example, a fundamental task in creating a Tethys App will be designing the URL patterns that will map to the different pages in your app. All of these URLs will be relative to the base URL of your CKAN instance, because your app is adding pages to the CKAN website. That being said, URL mapping is a small part of the development process and a strategy has been employed in the Tethys App plugin to ensure your app URLs won’t clash with the URLs of other apps.

CKAN Plugin
===========

The Tethys Apps plugin is a plugin for CKAN, which in turn is built on top of a Python web framework called `Pylons <http://docs.pylonsproject.org/en/latest/docs/pylons.html>`_. CKAN provides the infrastructure needed to manage datasets and their associated metadata. A dataset in CKAN is a container or package that stores one or more resources. A resource is a link to a file that contains the data (e.g.: spreadsheet, text file, model input/output files). The apps developed using the Tethys Apps plugin typically perform tasks on the datasets that are stored and managed by CKAN. Once a dataset has been registered with CKAN it can be exposed to apps.

Another key feature of CKAN is that it is extensible. The Tethys Apps plugin was developed using the interfaces that CKAN provides for extension. In fact, the way apps are developed for Tethys Apps mimics how plugins are developed for CKAN. Thus, it would be a very good idea to understand how plugins are developed for CKAN. To become more familiar with CKAN visit their website: http://ckan.org/

Web Frameworks
==============

CKAN is built using the `Pylons <http://docs.pylonsproject.org/en/latest/docs/pylons.html>`_ web framework. Understanding the difference between a static website and a dynamic website built with a web framework is important for app developers, because apps rely on web framework concepts. Static web development consists of creating a series of HTML files--one for every page of the website. The files are organized using the server’s file system and stored in some directory on the server that is accessible to the Internet. For a static site, the URL works very similar to how a file path works on an operating system. When a request is sent from the web browser to a server, the server locates the HTML file that the URL is requesting and returns it to the browser for the user to view.

The static method of developing web pages presents some problems for developers. For example, if a developer wants to include a header and footer on every page of her website, she would end up duplicating the header and footer markup many times (via copy and paste). This makes it difficult to update a static website, because changes need to be copied to every page where the code is duplicated. Developing a website in this way is error prone and can become prohibitive for large websites.

Web frameworks provide a way to develop websites using a programatic approach. Instead of static webpages, developers create generic reusable templates. Back to our header-footer example. With a web framework, the developer can create one template file containing only the markup for the header and another template file for the footer. Now when the developer wants to include the header and footer in another page, she uses an import construct that references to the header and footer templates. The header and footer markup is added to all the files that need it upon request by a template rendering program. Changes to the header and footer only need to be made in one place and the entire site will be updated. In this way, the site becomes dynamic. The software that makes it possible to create dynamic web pages are web frameworks.

Web frameworks also handle requests differently than traditional web pages. When the user submits a request to the server, instead of looking up a file on the server at the directory implied by the URL, the request is handed to the web framework application. The web framework processes the request and usually returns a page as the result (more on this in the next section).


Model View Controller
---------------------

The dynamic templating feature is only one aspect of what web frameworks offer. Many web frameworks use a design pattern called Model View Controller (MVC). This is the pattern that is used when developing an app using Tethys Apps. A brief explanation of each part is provided.

Model
+++++

The model represents the code that is used to store and retrieve data that is used in the web application. Most websites use SQL databases for persistent data storage, so the model is usually made up of an Object Relational Model (ORM) or at the very least a model schema and an SQL client to access it.

View
++++

Views are used to represent the data to the end user. In a web applications views are the HTML pages that are generated. Views are typically generic, reusable, and oblivious to the origins of the data that fills them. This is possible because of templating languages that allow coders to create dynamic HTML.

Controller
++++++++++

Controllers are used to orchestrate the interaction between the view and the model. They contain the logic for retrieving data from the database and transforming it into a format that is consumable by the view. Controllers also handle the feedback from the view such as form submits. The model and the view never communicate directly. In the Pylons web frameworks, the controllers are Python classes. The methods of a controller class are called actions.

When a user submits a request, the web application looks up the controller that is mapped to the URL and executes the appropriate method/action. The return value of an action is usually the path to the view that should be rendered. This is handed off to a template rendering utility that processes the template and generates HTML.The HTML is rendered for the user's viewing pleasure, the user sends another request, and the process repeats.

URL Design and REST Paradigm
============================

The URL takes on a different meaning in dynamic websites than it does in a static website. In a static website, the URL maps to directories and files on the server. In a dynamic website, there are no static files (or at least very few) to map to. The web framework simply maps the URL to a controller and returns the result. Although the developer is free to use URL’s in whatever manner they would like, it is recommended that some type of URL pattern should be used to make the website more maintainable.

We recommend developers use some form of the Representational State Transfer (REST) abstraction for creating meaningful URLs for apps. In a REST architecture for a website, the data of the website is referred to as resources. The current state of resources is presented to the user through some representation, usually an HTML document. The user can interact with the resources through the actions of the controller. Examples of common actions on resources are create, read (view), update (edit), and delete, often referred to as CRUD. These concepts can be applied as a URL pattern for apps.

For example, consider an app that is meant to show information about a database of dogs. A potential URL for showing a page that represents a summary about a dog would be:

::

	www.example.com/dogs/1/show

The number, 1, in the URL represents the dog’s id in the database. To show a page with the representation of another dog, just change the id. In this case, the URL pattern would be:

::

	/dogs/{id}/show

Often, the show action is the default action, so the URL could be shortened to:

::

	www.example.com/dogs/1

Similarly, a URL for a page the represents all of the dogs in the database in a list could be:

::

	www.example.com/dogs


A good URL that maps to a page that allows the user to edit the attributes of a dog would be:
	
::

	www.example.com/dogs/1/edit


More generally, we can design one URL pattern to respond to all of the possible actions for the dog resource:
	
::

	www.example.com/dogs/{id}/{action}


HTTP Verbs
----------

Anytime you type a URL into an address bar you are performing what is called a GET request. All of the above URLs are examples of implementing REST using only GET requests. GET is an example of an HTTP verb or method. There are quite a few HTTP verbs, but the other verbs pertinent to REST are POST, PUT, and DELETE. A truely RESTful design would make use of these HTTP verbs to implement the CRUD for the resources instead of using different key word actions. Consider our example from above. To read or view a dog resource, we use a GET request as before:

::
	
	# Read: HTTP GET
	www.example.com/dogs/1

However, to implement the create action for a dog resource, now we use the POST verb with the same url that we used for the read action:

::

	# Create: HTTP POST
	www.example.com/dogs/1

Similarly, to delete the dog resource we use the same URL as before but this time use the DELETE verb and to update or edit a dog resource, we use the PUT verb. Using this pattern, the URL becomes a unique resource identifier (URI) and the HTTP verbs dictate what action we will perform on the data. Unfortunately, HTML (which is the interface of HTTP) does not implement PUT or DELETE verbs in forms. In practice many RESTful sites use the "action" pattern for interacting with resources, because not all of the HTTP verbs are supported.






