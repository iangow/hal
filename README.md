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

1. Instead of copying Ian's data to my local server, I am going to use Ian's server as my backend database. This eliminates the need to sync data across databases. It looks like I should be able to read data out of schemas in Django, but I can't write into a schema.

http://stackoverflow.com/questions/1160598/how-to-use-schemas-in-django

2. Page where RAs can highlight the biographies in a random filing. How to select a random entry from PostgreSQL?

http://stackoverflow.com/questions/5297396/quick-random-row-selection-in-postgres

I'm going to have to do an anti-join with the filings that have already been highlighted. I don't think this will be too bad.

3. Admin action to sync highlights from Elasticsearch into Django's database (probably PostgreSQL). Suppose there are multiple highlights tagged for the same director. How should I go about combining them into one biography? Let's go for the easiest solution and join them in the order they were created. Alternatively I could use xpaths and the html document to sort them better. Maybe set up the code so it's easy to change that decision later.

`pull_highlights`

4. Create an admin page so RAs can mark whether directorships are mentioned. This will likely use an inline admin so they can see the text of the biography and mark which directorships are mentioned.

`Directorship`
`Director`
`Disclosure`
