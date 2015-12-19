.. _plot-view:

*********
Plot View
*********

**Last Updated:** August 10, 2015

Tethys Platform provides two interactive plotting engines: `D3 <http://d3js.org/>`_ and `Highcharts <http://www.highcharts.com/>`_. The Plot view options objects have been designed to be engine independent, meaning that you can configure a D3 plot using the same syntax as a Highcharts plot. This allows you to switch which plotting engine to use via configuration. This article describes each of the plot views that are available.

.. warning::

    Highcharts is free-of-charge for certain applications (see: `Highcharts JS Licensing <http://shop.highsoft.com/highcharts.html>`_). If you need a guaranteed fee-free solution, D3 is recommended.

.. note::

    D3 plotting implemented for Line Plot, Pie Plot, Bar Plot, Scatter Plot, and Timeseries Plot.

Line Plot
=========

.. autoclass:: tethys_sdk.gizmos.LinePlot

Scatter Plot
============

.. autoclass:: tethys_sdk.gizmos.ScatterPlot

Polar Plot
==========

.. autoclass:: tethys_sdk.gizmos.PolarPlot

Pie Plot
========

.. autoclass:: tethys_sdk.gizmos.PiePlot

Bar Plot
========

.. autoclass:: tethys_sdk.gizmos.BarPlot

Time Series
===========

.. autoclass:: tethys_sdk.gizmos.TimeSeries

Area Range
==========

.. autoclass:: tethys_sdk.gizmos.AreaRange

Highcharts JavaScript API
-------------------------

The Highcharts plots can be modified via JavaScript by using jQuery to select the Highcharts div and calling the ``highcharts()`` method on it. This will return the JavaScript object that represents the plot, which can be modified using the `Highcharts API <http://api.highcharts.com/highcharts>`_.

::

    var plot = $('#my-plot').highcharts();

