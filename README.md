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

# Data Collection - Next Steps

1.  Admin action to sync highlights from Elasticsearch into
    PostgreSQL. Suppose there are multiple highlights tagged for the
    same director. How should I go about combining them into one
    biography? Let's go for the easiest solution and join them in the
    order they were created.

    `pull_highlights`

2.  Create an admin page so RAs can mark whether directorships are
    mentioned. This will likely use an inline admin so they can see
    the text of the biography and mark which directorships are
    mentioned.

    `Director`     - individual
    `Directorship` - individual x filing
    `Disclosure`   - individual x filing x company x disclosed?

3.  Need to post this to Amazon Web Services.

## Backburner

Right now my random page could bring up a filing that may have been
highlighted already.

Other + none tags
Tag companies in bio segments not bios
Include director_id and equilar_id in tags

Move Postgres to Linode
Add director-id to existing entries in elastic search

Nertagger of all bio segments




 public | companies                  | table | postgres
 public | crosswalk                  | table | postgres

public | equilar_proxies            | table | postgres
public | director                   | table | postgres
 
public | matched_director_ids       | table | postgres
public | mirror_biographysegment    | table | postgres
public | mirror_filing              | table | postgres
