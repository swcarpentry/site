# Base URL and installation directory for installed version on server.
INSTALL_URL = http://software-carpentry.org
INSTALL_DIR = $(HOME)/sites/software-carpentry.org

# Base URL and installation directory for development version on server.
DEV_URL = http://dev.software-carpentry.org
DEV_DIR = $(HOME)/sites/dev.software-carpentry.org

#-------------------------------------------------------------------------------

# Source files in root directory.
SRC_ROOT = $(wildcard ./*.html)

# Source files in 'pages' directory.
SRC_PAGES = $(wildcard pages/*.html)

# Source files in 'scf' directory.
SRC_SCF = $(wildcard scf/*.html)

# Source files in 'bib' directory.
SRC_BIB = $(wildcard bib/*.html)

# Source files of blog posts.  Does *not* include the index file so
# that our preprocessor doesn't try to harvest data from it.
SRC_BLOG = $(wildcard ./blog/????/??/*.html)

# All workshop source files.
SRC_WORKSHOP = $(wildcard ./workshops/*.html)

# Source files for badge pages.
SRC_BADGES = $(wildcard ./badges/*.html)

# Source files for checklists.
SRC_CHECKLISTS = ./workshops/checklists/*.html

# Source files for Version 4 lessons.
SRC_V4 = $(wildcard ./v4/index.html) $(wildcard ./v4/*/*.html)

# Source files for layouts.
SRC_LAYOUT = $(wildcard ./_layouts/*.html)

# Source files for included material (go two levels deep, and wish that
# the 'wildcard' function knew how to recurse).
SRC_INCLUDES = $(wildcard ./_includes/*.html) $(wildcard ./_includes/*/*.html)

# All source HTML files.
SRC_HTML = \
    $(SRC_ROOT) \
    $(SRC_PAGES) \
    $(SRC_SCF) \
    $(SRC_BIB) \
    ./blog/index.html $(SRC_BLOG) \
    $(SRC_CHECKLISTS) \
    $(SRC_WORKSHOP) \
    $(SRC_BADGES) \
    $(SRC_V4) \
    $(SRC_LAYOUT) \
    $(SRC_INCLUDES)

# All source configuration files.
CONFIG_DIR = ./config
SRC_CONFIG = $(wildcard $(CONFIG_DIR)/*.yml)

# All files generated during the build process that are removed by
# 'make clean'.  This does *not* include the _workshop_cache.yml file:
# use 'make sterile' to get rid of that.
GENERATED = ./_config.yml ./_includes/recent_blog_posts.html

# Destination directories for manually-copied files.
DST_DIRS = $(OUT)/css $(OUT)/img $(OUT)/js

# Software Carpentry bibliography .tex file (in 'bib' directory).
SWC_BIB = software-carpentry-bibliography

#-------------------------------------------------------------------------------

# By default, show the commands in the file.
all : commands

## commands     : show all commands.
# Note the double '##' in the line above: this is what's matched to produce
# the list of commands.
commands : Makefile
	@sed -n 's/^## //p' $<

## authors      : list all blog post authors.
authors :
	@python bin/list_blog_authors.py $(SRC_BLOG) | cut -d : -f 1

## archive      : collect and archive workshop information from GitHub and store in local cache.
archive :
	cp $(CONFIG_DIR)/workshops_saved.yml ./_workshop_cache.yml
	@python bin/get_workshop_info.py -v -t \
	    -i $(CONFIG_DIR)/workshop_urls.yml \
	    -o ./_workshop_cache.yml \
	    --archive $(CONFIG_DIR)/workshops_saved.yml

## cache        : collect workshop information from GitHub and store in local cache.
cache :
	cp $(CONFIG_DIR)/workshops_saved.yml ./_workshop_cache.yml
	@python bin/get_workshop_info.py -v -t \
	    -i $(CONFIG_DIR)/workshop_urls.yml \
	    -o ./_workshop_cache.yml
	@python bin/make-dashboard.py -t ./git-token.txt -o ./_dashboard_cache.yml

## biblio       : make HTML and PDF of bibliography.
# Have to cd into 'bib' because bib2xhtml expects the .bst file in
# the same directory as the .bib file.
biblio : bib/${SWC_BIB}.tex bib/software-carpentry.bib
	@cd bib && pdflatex $(SWC_BIB) && bibtex $(SWC_BIB) && pdflatex $(SWC_BIB)
	@cd bib && ../bin/bib2xhtml software-carpentry.bib ./bib.html && dos2unix ./bib.html

## categories   : list all blog category names.
categories :
	@python bin/list_blog_categories.py $(SRC_BLOG) | cut -d : -f 1

categories_n :
	@python bin/list_blog_categories.py -n $(SRC_BLOG)

## site         : build locally into _site directory for checking.
site :
	make SITE=$(PWD)/_site OUT=$(PWD)/_site build

## dev          : build into development directory on server.
dev :
	make SITE=$(DEV_URL) OUT=$(DEV_DIR) build

## install      : build into installation directory on server.
install :
	make SITE=$(INSTALL_URL) OUT=$(INSTALL_DIR) build

## check        : check consistency of various things.
check :
	@python bin/check_workshop_info.py config/workshop_urls.yml config/workshops_saved.yml

## missing      : which instructors don't have biographies?
missing :
	@python bin/check_missing_instructors.py config/badges_config.yml _includes/people/*.html

## links        : check links.
#  Depends on linklint, an HTML link-checking module from http://www.linklint.org/,
#  which has been put in bin/linklint.
links :
	bin/linklint -doc /tmp/site-links -textonly -root _site /@

## valid        : check validity of HTML.
#  Depends on xmllint being installed.  Ignores entity references.
valid :
	xmllint --noout $$(find _site -name '*.html' -print) 2>&1 | python bin/unwarn.py

## clean        : clean up.
clean :
	@rm -rf \
	$(GENERATED) \
	_site \
	bib/*.aux bib/*.bbl bib/*.blg bib/*.log \
	$$(find . -name '*~' -print)

## sterile      : *really* clean up.
sterile : clean
	rm -f ./_workshop_cache.yml ./_dashboard_cache.yml

#-------------------------------------------------------------------------------

# build : compile site into $(OUT) with $(SITE) as Software Carpentry base URL
build : $(OUT)/workshops.ics $(OUT)/feed.xml $(OUT)/workshop-feed.xml $(OUT)/.htaccess $(OUT)/img/main_shadow.png

# Copy the .htaccess file.
$(OUT)/.htaccess : ./_htaccess
	@mkdir -p $$(dirname $@)
	cp $< $@

# Make the workshop calendar file.
$(OUT)/workshops.ics : ./bin/make_calendar.py $(OUT)/index.html
	@mkdir -p $$(dirname $@)
	python ./bin/make_calendar.py -o $(OUT) -s $(SITE)

# Make the blog RSS feed file.
$(OUT)/feed.xml : ./bin/make_rss_feed.py $(OUT)/index.html
	@mkdir -p $$(dirname $@)
	python ./bin/make_rss_feed.py -o $(OUT) -s $(SITE)

# Make the workshop RSS feed file.
$(OUT)/workshop-feed.xml : ./bin/make_workshop_rss_feed.py $(OUT)/index.html
	@mkdir -p $$(dirname $@)
	python ./bin/make_workshop_rss_feed.py -o $(OUT) -s $(SITE)

# Make the site pages (including blog posts).
$(OUT)/index.html : _config.yml $(SRC_HTML)
	jekyll build -d $(OUT)

# Make the Jekyll configuration file by adding harvested information to a fixed starting point.
_config.yml : ./bin/preprocess.py $(SRC_CONFIG) $(SRC_BLOG)
	python ./bin/preprocess.py -c ./config -o $(OUT) -s $(SITE)
