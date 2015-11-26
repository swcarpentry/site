Software Carpentry Web Site
===========================

This repository holds the source for
the [Software Carpentry](http://software-carpentry.org) web site.
Lessons are not stored in this repository:
please see [the lessons page](http://software-carpentry.org/lessons.html)
for links to their repositories.

Contributing
------------

Software Carpentry is an open source/open access project,
and we welcome contributions of all kinds.
By contributing,
you are agreeing that Software Carpentry may redistribute your work
under [these licenses](http://software-carpentry.org/license.html).

Setting Up
----------

Rebuilding the web site locally to check changes requires:

*   [Jekyll](http://jekyllrb.com/), used to compile templated HTML pages
*   [Python 3](http://python.org/), used for pre- and post-processing

We use Jekyll because it's what [GitHub](http://github.com/) uses;
we use Python because most of our volunteers speak it.
The Python packages we depend on can be installed using:

~~~
$ pip3 install -r requirements.txt
~~~

We try to use the same MarkDown interpreters as GitHub does for consistency.
On OS X, we suggest you use a recent Ruby to get access to these.
If you don't have Homebrew or MacPorts installed,
here's a quick recipe to get started using HomeBrew:

~~~
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew install ruby
gem install jekyll
gem install RedCloth
~~~

Building
--------

The commands used to rebuild the website are stored in `Makefile`.

*   Type `make` on its own to see a list of all available commands.
*   Type `make clean` to get rid of generated files.
*   Type `make cache` to rebuild cached information about workshops and repositories.
    You only need to do this once a day or so,
    since that information changes relatively infrequently,
    but you *do* need to do it at least once before you can preview the website.
    (Depending on your machine, this takes 15-30 seconds.)
*   Type `make site` to build everything in `_site` for testing.
    (Depending on your machine, this takes about 10-15 seconds.)
    You can then open `_site/index.html`
    and other pages in `_site`
    to see what your changes will look like.


**Note: You must have Jekyll 2.5 or later.** If you have an older version
installed, you can update it with:

~~~
gem update
~~~

Note: Disqus comments will *not* load properly,
since you'll be on your machine rather than our server.

Blogging
--------

The simplest way to create a new blog post is
to mail the text to [Greg Wilson](mailto:gvwilson@software-carpentry.org),
who will format it and post it for you.
If you'd like to submit your post as a pull request, then:

1.  Fork this repository on GitHub, and clone that to your desktop.

2.  Create a file `blog/YYYY/MM/post-name.html`,
    where `YYYY` is a four-digit year and `MM` is a two-digit month.
    (The directories `YYYY` and `YYYY/MM` will already exist
    unless you're the first person to blog this month or this year.)

3.  Fill in the metadata at the top of the file
    (or if you have copied an existing blog post, edit the values):
    *   `layout` *must* be `blog`.
    *   `author` must be the author's name.  (It does not need to be quoted.)
    *   `title` is the post title.
    *   `date` the date of the post (in YYYY-MM-DD format).
    *   `time` must be an HH:MM clock time, such as 09:30.
        Every post must have a unique timestamp so that posts can be ordered.
    *   `category` must be a list of category identifiers, e.g.,
        `["Euphoric State University", "Assessment"]`
        You can use an empty list if you want,
        and we'll fill in categories for you.

4.  Use HTML to write the post.
    *   Use `<!-- start excerpt -->` and `<!-- end excerpt -->`
        to mark a paragraph or two at the start
        as the excerpt to show in feed readers.
    *   If you need to refer to our email address, it is `{{page.contact}}`.
    *   If you need to refer to another post, or something else on the site, use `{{page.root}}/path/to/file`.

5.  Please add any images your blog post needs to the same blog/YYYY/MM directory as the post itself.
    Please use lower-case names without special characters for image files.

6.  When you're satisfied with your post,
    `git add path/to/post` and `git commit -m "Adding a blog post about something or other"`
    will commit it to your local copy (on your laptop).

7.  `git push origin master` will push it to your clone on GitHub
    (assuming you've added your fork on GitHub as a remote called `origin`).

8.  Go to GitHub and issue a pull request from your clone to `swcarpentry/site`,
    then assign it to `gvwilson` for proof-reading.

Adding a Workshop
-----------------

Email the workshop's URL to [the administrators](mailto:admin@software-carpentry.org)
so that they can add it to our database.
The workshop will then show up on the main website the next time it is rebuilt(which typically happens hourly).



For More Advanced Users
-----------------------

`make site` (and its partners `make dev` and `make install`) do the following:

1.  Run `bin/preprocess.py` to create the `./_config.yml` file required by Jekyll
    and the `_includes/recent_blog_posts.html` file containing excerpts of recent blog posts.
    This tool collects metadata about blog posts and workshops
    and combines it with static configuration information.

2.  Run Jekyll to build the web site.

3.  Run `bin/make_rss_feed.py` to generate the RSS feed file `feed.xml`.

4.  Run `bin/make_calendar.py` to generate the ICal calendar file `workshops.ics`.

5.  Copy `./_htaccess` to create the `.htaccess` file for the web site.

`bin/preprocess.py` needs two generated files to work properly:

*   `_workshop_cache.yml`: stores information about recent and upcoming workshops.
    This file is created by `bin/get_workshop_info.py`.

*   `_dashboard_cache.yml`: stores information about Software Carpentry's GitHub projects.
    This file is created by `bin/make-dashboard.py`.

The tool used to rebuild the dashboard cache requires credentials in order to run,
since use of GitHub's API is throttled for unauthenticated users and programs.
If you wish to regenerate these files:

1.  Get a [GitHub API token](https://github.com/blog/1509-personal-api-tokens).

2.  Save it in a file called `git-token.txt` in the root directory of this site.
    (This file is ignored by Git, since tokens should not be shared between people.)

After that,
you can run `make cache` to re-create the two files.
Please do *not* commit them.

Badges
------

Software Carpentry uses [Open Badges](http://openbadges.org/) to recognize people's skills and accomplishments.
To create badges, you must install [PyPNG](http://pythonhosted.org/pypng/index.html) module:

~~~
$ pip3 install pypng
~~~

Use `bin/badge-create.py` to create a new badge, e.g.:

~~~
$ python3 bin/badge-create.py username email instructor
~~~

To bake the badge we use `bin/badgebakery.py` which was provided by the Open Badge Team.
