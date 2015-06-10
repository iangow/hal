# HAL

HAL (Highlighting Assistant Legend) will be designed to make highlighting thousands of documents easy. HAL has a number of components:

1. Highlighter - Allow user to highlight any webpage and save the results to Annotator Store. This will include code to pull useful data out of the Annotator Store.

2. Mirror (edgar) - Make it easy to construct a local mirror of an external website. This will include code to pull pages of interest from Edgar and keep track of them in the database.

3. Learner - Built with [NLTK](http://www.nltk.org/) and [scikit-learn](http://scikit-learn.org/stable/), let's see how well we can teach a computer to highlight documents.

# Installation

Here's how I install HAL:

    git clone git@bitbucket.org:amarder/hal.git
    make install

The `Makefile` assumes the conda package manager for python is available on your machine.

# Running

If you want to create, read, update, or delete highlights a few processes need to be running:

1. [Elasticsearch](http://www.elasticsearch.org/),
2. [Annotator Store](https://github.com/openannotation/annotator-store),
3. This Django project.

To fire up all three processes, I use the following command:

    make start

And to shut everything down I use:

    make stop

# Road map for data collection process

1. Admin action to sync local database with Ian's server. Need to pull information on filings and directorships. If it's possible to use similar IDs that might help the merging process. I should look at exactly what data I should pull from his database. And how to keep things clean. It looks like using Django's support of multiple databases is the way to go to copy data from Ian's server to the local database.

https://docs.djangoproject.com/en/1.8/topics/db/multi-db/

`pull_equilar_data`

2. Page where RAs can highlight the biographies in a random filing.

3. Admin action to sync highlights from Elasticsearch into Django's database (probably PostgreSQL). Suppose there are multiple highlights tagged for the same director. How should I go about combining them into one biography? Let's go for the easiest solution and join them in the order they were created. Alternatively I could use xpaths and the html document to sort them better. Maybe set up the code so it's easy to change that decision later.

`pull_highlights`

4. Create an admin page so RAs can mark directorships. This will likely use an inline admin so they can see the text of the biography and mark which directorships are mentioned.
