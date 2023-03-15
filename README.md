# NLP Financial Document Processor

# Abstract

Profits in market-oriented parts of the financial industry come from finding inconsistencies (mispricings, overlooked situations, and erroneous calculations), realizing the disparity between what should be, and capitalizing as the rest of the market comes to recognize and correct the discrepancy. The market itself is a voting machine, where votes are informed by all information investors consider for a given company. However, this knowledge base is often a subset of all information available for that security. Thus investors seek to gain an advantage by discovering alternative data sources or new ways of looking at existing data.

Any publicly traded company on a US exchange must file quarterly reports (with the fourth covering the quarter and the fiscal year). This requirement has created a database of millions of financial documents over the years; the underlying assumption our project makes is that, while looking at these filings on a per-security basis is common practice, exploring the documents in aggregate through Natural Language Processing (NLP) is a novel approach that may yield competitive advantages, either in efficiency, alpha generation, or both.

# Architecture: Functional

`engine.py:` Drives the program. Ties modules together to execute the user's desired functionality.

`fetch.py:` Responsible for pulling down raw text data from online files and pulling saved data from a remote database.

`interface.py:` Functions for user interaction from the command line or locally hosted web page.

`clean.py:` Scrubs raw text for undesired words, characters, phrases, etc.

`database.py:` Pushes data to remote database and pulls data from it.

# Architecture: Logistical

`nlpengine/backend/app.py:` This is a Flask Microservice REST API that allows the React front end make requests to our python backend.  
`/nlpengine/nlpapp/:` This is a Static React Front end with FormComponent as the main component. In here, HTTP Requests are made to the backend to gather and parse data.

# Implementation

The following is a high-to-medium-level description of how the components of the program piece together. For a more detailed perspective, extensive documentation can be found in the source code for every function and module.

The user is prompted on the front end to choose a mode of functionality: build a new model, edit an old model, or apply a corpus to an old model. In each, the user will be prompted to input a list of tickers and quarter codes, representing the filings they wish to build a model from, add to an existing model, or apply to an existing model. In the latter two, users will also be asked to specify the name of an existing model. After these inputs are given and upon execution, the ticker and quarter inputs are handled in the interface module:

`convert_tickers` parses the user input for a list of tickers, fetches the corresponding CIKs via `get_CIKs`, and returns a dictionary pairing the two.

`convert_quarters` parses the user input for a list of quarters, calling helper functions `handle_range` and `add_valid_qcodes`, for user convenience and consistency respectively.

For the latter two modes, fetching the existing model is handled in the database module:

`get_models` is used to display all saved models for the user to choose from; `get_model` is used to fetch and return a specific model from that list.

These functions are called from one of three driving functions in the engine module: `new_model`, `edit_model`, and `apply_model`. In each of these functions, with the corpus specified and existing model specified if needed, the databases are now accessed for company report text via the fetch module. The engine functions call one of the fetch drivers--as of this writing, it is `fetch_driver`, but it may be `fetch_multiprocessing` in future iterations.

The fetch module is the most complicated. To best describe its components, consider how the drivers that operate them work:

1. For each company and quarter pair, see if that filing has been previously accessed and is saved in the remote database via `get_from_db` in the database module.
2. For each new company and quarter pair, find all filings the company made in that quarter with `get_forms`. Assess if any of those filings were a 10-K or 10-Q via `get_10q_url`; if so, format the url to the filing's page on the SEC website with `format_url`.
3. Navigate that page to find the HTML version of the filing, then parse the filing and return the text in the relevant sections with `grab_form` (which uses `isolate_section_reports` heavily).

All drivers generally approach step 1 the same way. `fetch_driver` tackles steps 2 and 3 by pulling all unseen quarters for a given company at a time; `fetch_multiprocessing` tries to break steps 2 and 3 down by sending off each unseen company-quarter combination as a task to different processes for efficiency.

The raw data is passed back to the functions in the engine module, where it is cleaned via `clean_data`. In `new_model`, that corpus is then used in LSA via `perform_lsa` and converted into a front end-friendly format via `topicShower`. In `edit_model`, the old model is combined with this new corpus and similarly transformed via `topicShower`. In `apply_model`, the new corpus is applied to the old model and the resulting vector is displayed. In `new_model` and `edit_model`, the new model is saved in the remote database via `push_model` in the database module.

# Technology Stack

# Databases

The SEC-owned EDGAR database contains all filings from all US publicly traded companies; while it goes back further, we will only be using filings back to around 2003, when filing format became more standardized. EDGAR has a convenient indexing structure that allows us to navigate directly to a more narrowed document listing (e.g., all filings for a given company during a given quarter) or even directly to a specific document (e.g., Pfizer’s 3Q10 10-Q). In the EDGAR database, each company is given a Central Index Key (CIK) as a unique numerical identifier. Cross referencing a company’s CIK with a quarter-specific index system yields a directory of all filings published by the given company during that quarter; it is from this directory that we can pull specific documents.

Accessing these documents is a time consuming process, so to alleviate the performance slowdown, the program manages a remote database, using MongoDB, of previously-parsed filings that is supplemented on each execution of the program. Text data stored in the remote database is normalized and parsed, so on given execution of the program, only unseen filings need to be accessed and scrubbed.

# Applied NLP Concepts

Our program leverages LSA to turn a text corpus into a topic model.

LSA begins with a normalized corpus of documents to be analyzed, each pruned of punctuation and other grammatical elements that dilute the analysis. From this stripped-down text, a Term x Document matrix is created, plotting, for each document in the corpus, the counts of each of that document’s words against a master set of all the terms contained in the corpus. This master set of all words in the corpus allows comparison between documents: it is as important to note which words are not included in a given document that appears in other documents.

From the Term x Document matrix, LSA performs a Term Frequency-Inverse Document Frequency (TF-IDF) analysis. In TF-IDF, a Term x Document matrix is normalized for each document’s relative length (Term Frequency; words that make up a large percentage of a document with low count are weighted above words that have a high count but make up only a tiny percentage of the total words in the document) and the relative rarity of that word among all documents (Inverse Document Frequency; a word that only appears in one document is weighted heavier than the word “the,” for example, which will probably appear in every document of the corpus).

At this point, Singular Value Decomposition (SVD) is applied to reduce the TF-IDF matrix to k dimensions, finding a value of k (representing the number of “topics” in Latent Semantic Analysis) in which all significant singular values are preserved (i.e., k isn’t too small as to reduce the matrix too far and eliminate valuable data). However, no undue work is done (i.e., k isn’t too large to take too much time to compute).

When the final SVD has been found, it yields a Term x Topic matrix in which a positive-weighted term in a given topic column indicates that Term is associated with that topic, and a similar Topic x Document matrix, which suggests in the same way which documents are associated with which topics. The magnitude of a value positively correlates to the relevance of that Term or document to the given topic.

Latent Dirichlet Allocation (LDA) is a more computationally-intensive and new option. In this approach, rather than viewing topics as a “bag of words,” topics are considered word distributions, creating a more probabilistic topic representation. Dirichlet distributions are used as priors (beginning assumptions) for word frequency to improve accuracy. At the same time, LSA may represent a topic as a collection of words from which the topic designation may be inferred (e.g., [run, catch, throw] = sports), LDA’s probabilistic approach allows for relational definitions (e.g., [run, catch, throw] = baseball_related and football_related). LDA is a significantly more complicated algorithm that would require fine-tuning several parameters. However, the fundamental difference is that LDA provides a probabilistic output--topics consisting of distributions of words and documents comprised of distributions from topics--thereby providing a more nuanced perspective.

To improve the insightfulness of the topic model, one may wish to deploy additional NLP concepts in the future. For example, we have discussed the use of n-grams, which groups words that frequently appear consecutively, in our cleaning module, towards removing unimportant text that would not be labeled as such with less sophisticated methods.

The goal of using topic modeling in this project is to break a filing down into its most relevant topics and to identify the most pertinent terms within each topic. The hope is that, with this information, one might find a market correlation between topics, terms, and stock price movement, thereby providing a unique and advantageous investing strategy.

# User Interface

To enable a user to interact and use our program, we built a static React front-end that interacts with a Flask Microservice API to access our backend NLP Processing Engine. From the static front-end, the user can access four main functionalities: 1) Build New Model 2) Edit Saved Model 3) Apply Saved Model 4) View Saved Model.

When building a new model, a user enters a model name, a list of tickers and a range of quarters. This will return a topic model along with a word cloud that visualizes the topic model.

Editing a saved model allows the user to add additional documents to the existing corpus.

Applying a saved model returns a vector of how relevant each topic is to the new corpus of documents that is provided by the user.

Viewing a saved model returns a topic model and a word cloud given a specific model.

# Testing and Professional Input

We thoroughly tested all aspects of our project from fetching to parsing to our front-end and more. We independently tested each module and then also performed integration and end to end testing. We attempted to replicate what we thought the workflow for an average analyst would be when testing our project.

Throughout the year, we recieved input from Roshan that helped guide and shape our project. For example, we chose to go with LSA instead of LDA for our NLP analysis at Roshan's recommendation. Additionally, Roshan helped provide advice on modules and packages that could be helpful when running into roadblocks.

# Maintenence

The only change required to fully hand over the project to Fidelity is the creation of 2 new databases to store models and corupuses. These databases are currently stored in a private MongoDb account. If after the migration the Fidelity team decides to stay with MongoDb, then the only changes required are on lines 10 and 14 of `database.py`. The connection commands would have to be changed to connect with the new Fidelity databases. Apart from that, no other chagnes are required.

# Application Setup

## Initial Setup

Make sure all server-side dependencies are installed:  
`cd nlpengine/nlpapp`  
`npm install`  
Make sure the following Python packages are installed:  
`gensim  
pyldavis  
pandas  
nltk  
urllib3  
bs4  
pymongo  `

## Executing the Program

### Start the Backend

`cd nlpengine/backend`  
`python app.py`  
Starts on localhost:5000

### Launch the Frontend

In a new terminal window:
`cd nlpengine/nlpapp`  
`npm start`  
Starts on localhost:3000

## HPC Cluster:

`ssh dgrich01@login.cluster.tufts.edu`  
cd to folder containing files  
`module load python/3.5.0`  
`pip3 install --user gensim`  
You may need to install other dependencies

### Running the script

`sbatch < cluster.slurm`

### Checking the job

`squeue -u dgrich01`

### Output File

Outputs to: log_JOBID.out  
Error output to: log_JOBID.err
