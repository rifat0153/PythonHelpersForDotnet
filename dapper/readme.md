# Dapper Class Generator

## Overview

This project is a tool for generating C# classes based on SQL Stored Procedures (SPs). It's designed to help developers working with Dapper, a simple object mapper for .NET, by automating the process of creating request and handler classes.

## Setup

To get started with this project, you'll need to have .NET Core and Python installed. Once you have those, you can clone this repository and open it in your preferred IDE.

## How It Works

### Reading Stored Procedures

The tool reads the text of a stored procedure from a SQL Server database. It parses the stored procedure to identify its input parameters and their types.

### Generating Request Classes

For each stored procedure, the tool generates a corresponding C# request class. This class includes properties for each of the stored procedure's input parameters.

### Generating Handler Classes

The tool also generates a C# handler class for each stored procedure. This class includes a method that uses Dapper to execute the stored procedure.

The generated classes can be found in the `Generated` folder.

## Running the Project

To run the project, use the following command:

```sh
python main.py
```
