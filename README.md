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