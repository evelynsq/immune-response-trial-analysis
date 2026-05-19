Any instructions needed to run your code and reproduce the outputs (We will run your code using GitHub Codespaces).

An explanation of the schema used for the relational database, with rationale for the design and how this would scale if there were hundreds of projects, thousands of samples and various types of analytics you’d want to perform.

A brief overview of your code structure and an explanation of why you designed it the way you did.

A link to the dashboard.

# Clinical Trial Immune Cell Populations Analysis

Evelyn Quan (evelyn.quan7@gmail.com)

## Instructions to Run Code

Begin by cloning this repository and changing to the project directory:
```
git clone https://github.com/evelynsq/immune-response-trial-analysis.git
cd immune-response-trial-analysis/
```

Python version 2.5 or higher is required, as these versions contain SQLite as part of the standard library.

Python packages required include:

- dash
- matplotlib
- pandas
- scipy
- seaborn

To install all these dependencies, run the following:

```
make setup
```

To execute the entire data pipeline, run:

```
make pipeline
```

To start the interactive dashboard of the analysis results, run:

```
make dashboard
```

*Note*: If you are interested in executing a single script by itself, please run it while remaining in the project's root directory.


## Relational Database Schema: Explanation and Rationale

There are four tables used for the database `drug-response.db`:

1. *project_info*
2. *patients*
3. *samples*
4. *cell_counts*

![ER Diagram for Database](images/ER-Diagram.png)

I put *project_info* with the project_id being the sole column to consider the scale and 


## Code Structure Overview and Design




## Access the Dashboard

Please run `make dashboard` to access the interactive dashboard with the analysis results.