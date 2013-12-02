# Base URL and installation directory for development version on server.
DEV_URL = http://dev.software-carpentry.org
DEV_DIR = $(HOME)/dev.software-carpentry.org

# Base URL and installation directory for installed version on server.
INSTALL_URL = http://software-carpentry.org
INSTALL_DIR = $(HOME)/sites/software-carpentry.org

#-------------------------------------------------------------------------------

# Source files in root directory.
SRC_ROOT = $(wildcard ./*.html)

# Source files in 'contrib' directory.
SRC_CONTRIB = $(wildcard ./contrib/*.html)

# Source files of blog posts.  Does *not* include the index file so
# that our preprocessor doesn't try to harvest data from it.
SRC_BLOG = $(wildcard ./blog/????/??/*.html)

# Source files of archived bootcamp pages (used for extracting
# metadata for building the calendar page).
SRC_BOOTCAMP_PAGES = $(wildcard ./bootcamps/????-??-*/index.html)

# All bootcamp source files.
SRC_BOOTCAMP = $(SRC_BOOTCAMP_PAGES) \
./bootcamps/index.html \
./bootcamps/operations.html \
./bootcamps/pre-learner.html \
./bootcamps/post-learner.html \
./bootcamps/post-instructor.html

# Source files for badge pages.
SRC_BADGES = ./badges/index.html

# Source files for checklists.
SRC_CHECKLISTS = ./bootcamps/checklists/*.html

# Source files for Version 4 lessons.  Use wildcard to match the index
# file instead of just naming it so that SRC_V4 is empty if the 'v4'
# submodule hasn't been populated.
SRC_V4 = $(wildcard ./v4/index.html) $(wildcard ./v4/*/*.html)

# Source files for layouts.
SRC_LAYOUT = $(wildcard ./_layouts/*.html)

# Source files for included material (go two levels deep, and wish that
# the 'wildcard' function knew how to recurse).
SRC_INCLUDES = $(wildcard ./_includes/*.html) $(wildcard ./_includes/*/*.html)

# All source HTML files.
SRC_PAGES = \
    $(SRC_ROOT) \
    $(SRC_CONTRIB) \
    ./blog/index.html $(SRC_BLOG) \
    $(SRC_CHECKLISTS) \
    $(SRC_BOOTCAMP) \
    $(SRC_BADGES) \
    $(SRC_V4) \
    $(SRC_LAYOUT) \
    $(SRC_INCLUDES)

# All source configuration files.
CONFIG_DIR = ./config
SRC_CONFIG = $(wildcard $(CONFIG_DIR)/*.yml)

# All files generated during the build process.  This does *not*
# include the _bootcamp_cache.yml file: use 'make sterile' to get rid
# of that.
GENERATED = ./_config.yml ./_includes/recent_blog_posts.html

# Destination directories for manually-copied files.
DST_DIRS = $(OUT)/css $(OUT)/img $(OUT)/js

# All image files.  We don't actually expand this normally, because it slows the
# build down considerably, and because Jekyll takes care of copying image files
# for us.  However, we *do* explicitly copy image files referenced by our CSS,
# since Jekyll doesn't appear to pick those up.
# 
# SRC_IMG = $(filter-out _site/%,\
#     $(wildcard *.png) $(wildcard */*.png) $(wildcard */*/*.png) $(wildcard */*/*/*.png) \
#     $(wildcard *.jpg) $(wildcard */*.jpg) $(wildcard */*/*.jpg) $(wildcard */*/*/*.jpg) \
#     $(wildcard *.gif) $(wildcard */*.gif) $(wildcard */*/*.gif) $(wildcard */*/*/*.gif) \
#     )
#
# Destination images.
# DST_IMG = $(patsubst %,$(OUT)/%,$(SRC_IMG))

# Software Carpentry bibliography .tex file (in papers directory).
SWC_BIB = software-carpentry-bibliography

#-------------------------------------------------------------------------------

# By default, show the commands in the file.
all : commands

## commands   : show all commands.
# Note the double '##' in the line above: this is what's matched to produce
# the list of commands.
commands :
	@grep -E '^##' Makefile | sed -e 's/## //g'

## authors    : list all blog post authors.
authors :
	@python bin/list_blog_authors.py $(SRC_BLOG) | cut -d : -f 1

## cache      : collect bootcamp information from GitHub and store in local cache.
cache :
	@python bin/get_bootcamp_info.py -t -i $(CONFIG_DIR)/bootcamp_urls.yml -o ./_bootcamp_cache.yml

## cache_verb : collect bootcamp information from GitHub and store in local cache (verbose)
cache_verb :
	@python bin/get_bootcamp_info.py -v -t -i $(CONFIG_DIR)/bootcamp_urls.yml -o ./_bootcamp_cache.yml

## biblio     : make HTML and PDF of bibliography.
# Have to cd into papers because bib2xhtml expects the .bst file in
# the same directory as the .bib file.
biblio :
	@cd papers && pdflatex $(SWC_BIB) && bibtex $(SWC_BIB) && pdflatex $(SWC_BIB)
	@cd papers && ../bin/bib2xhtml software-carpentry.bib ../biblio.html && dos2unix ../biblio.html

## categories : list all blog category names.
categories :
	@python bin/list_blog_categories.py $(SRC_BLOG) | cut -d : -f 1

## check      : build locally into _site directory for checking
check :
	make SITE=$(PWD)/_site OUT=$(PWD)/_site build

## dev        : build into development directory for sharing
dev :
	make SITE=$(DEV_URL) OUT=$(DEV_DIR) build

## install    : build into installation directory for sharing
install :
	make SITE=$(INSTALL_URL) OUT=$(INSTALL_DIR) build

## links      : check links
#  Depends on linklint, an HTML link-checking module from http://www.linklint.org/,
#  which has been put in bin/linklint.
links :
	bin/linklint -doc /tmp/site-links -textonly -root _site /@

## clean      : clean up
clean :
	@rm -rf \
	$(GENERATED) \
	_site \
	papers/*.aux papers/*.bbl papers/*.blg papers/*.log \
	$$(find . -name '*~' -print)

## sterile    : *really* clean up
sterile : clean
	rm -f ./_bootcamp_cache.yml

#-------------------------------------------------------------------------------

# build : compile site into $(OUT) with $(SITE) as Software Carpentry base URL
build : $(OUT)/bootcamps.ics $(OUT)/feed.xml $(OUT)/.htaccess $(OUT)/img/main_shadow.png

# Copy the .htaccess file.
$(OUT)/.htaccess : ./_htaccess
	@mkdir -p $$(dirname $@)
	cp $< $@

# Make the bootcamp calendar file.
$(OUT)/bootcamps.ics : ./bin/make_calendar.py $(OUT)/index.html
	@mkdir -p $$(dirname $@)
	python ./bin/make_calendar.py -o $(OUT) -s $(SITE)

# Make the blog RSS feed file.
$(OUT)/feed.xml : ./bin/make_rss_feed.py $(OUT)/index.html
	@mkdir -p $$(dirname $@)
	python ./bin/make_rss_feed.py -o $(OUT) -s $(SITE)

# Make the site pages (including blog posts).
$(OUT)/index.html : _config.yml $(SRC_PAGES)
	jekyll build -d $(OUT)

# Make the Jekyll configuration file by adding harvested information to a fixed starting point.
_config.yml : ./bin/preprocess.py $(SRC_CONFIG) $(SRC_BLOG) $(SRC_BOOTCAMP_PAGES)
	python ./bin/preprocess.py -c ./config -o $(OUT) -s $(SITE)

# Copy image files.  Most of these rules shouldn't be exercised,
# because Jekyll is supposed to copy files, but some versions only
# appear to pick up images referenced by generated HTML pages, not
# ones referenced by CSS files.

$(OUT)/%.png : %.png
	@mkdir -p $$(dirname $@)
	cp $< $@

$(OUT)/%.jpg : %.jpg
	@mkdir -p $$(dirname $@)
	cp $< $@

$(OUT)/%.gif : %.gif
	@mkdir -p $$(dirname $@)
	cp $< $@
