## ------------------------------------------------------------------------------
## To rebuild the site locally for checking:
##     1. make clean
##     2. make site
## To rebuild intermediate files (not necessary for simple blog posts):
##     1. make sterile
##     2. make cache
##     3. make site
## There must be a file ./git-token.txt containing a GitHub API token in order
## for 'make cache' to work.
## ------------------------------------------------------------------------------

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
SRC_BLOG_POSTS = $(wildcard ./blog/????/??/*.html)

# All blog source files.
SRC_BLOG = ./blog/index.html $(SRC_BLOG_POSTS)

# All workshop source files.
SRC_WORKSHOP = $(wildcard ./workshops/*.html) $(./workshops/checklists/*.html)

# Source files for badge pages.
SRC_BADGES = $(wildcard ./badges/*.html)

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
    $(SRC_BLOG) \
    $(SRC_WORKSHOP) \
    $(SRC_BADGES) \
    $(SRC_LAYOUT) \
    $(SRC_INCLUDES)

# All source configuration files.
SRC_CONFIG = $(wildcard ./config/*.yml)

# All files generated during the build process that are removed by
# 'make sterile'.
GENERATED = \
	./_config.yml \
	./_includes/recent_blog_posts.html \
	./_workshop_cache.yml \
	./_dashboard_cache.yml

# Software Carpentry bibliography .tex file (in 'bib' directory).
SWC_BIB = software-carpentry-bibliography

#-------------------------------------------------------------------------------
## Basic commands

# By default, show the commands in the file.
all : commands

## commands     : show all commands.
# Note the double '##' in the line above: this is what's matched to produce
# the list of commands.
commands : Makefile
	@sed -n 's/^## //p' $<

## site         : build locally into _site directory for checking.
site :
	make SITE=$(PWD)/_site OUT=$(PWD)/_site build

## check        : check consistency of various things.
check :
	@python bin/check_workshop_info.py config/workshop_urls.yml config/workshops_saved.yml

## clean        : clean up.
clean :
	@rm -rf \
	_site \
	bib/*.aux bib/*.bbl bib/*.blg bib/*.log \
	$$(find . -name '*~' -print)

## ------------------------------------------------------------------------------
## Advanced commands

## archive      : collect and archive workshop information from GitHub and store in local cache.
archive :
	cp ./config/workshops_saved.yml ./_workshop_cache.yml
	@python bin/get_workshop_info.py -v -t \
	    -i ./config/workshop_urls.yml \
	    -o ./_workshop_cache.yml \
	    --archive ./config/workshops_saved.yml

## authors      : list all blog post authors.
authors :
	@python bin/list_blog_authors.py $(SRC_BLOG) | cut -d : -f 1

## biblio       : make HTML and PDF of bibliography.
# Have to cd into 'bib' because bib2xhtml expects the .bst file in
# the same directory as the .bib file.
biblio : bib/${SWC_BIB}.tex bib/software-carpentry.bib
	@cd bib && pdflatex $(SWC_BIB) && bibtex $(SWC_BIB) && pdflatex $(SWC_BIB)
	@cd bib && ../bin/bib2xhtml software-carpentry.bib ./bib.html && dos2unix ./bib.html

## categories   : list all blog category names.
categories :
	@python bin/list_blog_categories.py $(SRC_BLOG) | cut -d : -f 1

## cache        : collect information from GitHub (requires git-token.txt file).
cache :
	cp ./config/workshops_saved.yml ./_workshop_cache.yml
	@python bin/get_workshop_info.py -v -t \
	    -i ./config/workshop_urls.yml \
	    -o ./_workshop_cache.yml
	@python bin/make-dashboard.py ./git-token.txt ./_dashboard_cache.yml

## dev          : build into development directory on server.
dev :
	make SITE=$(DEV_URL) OUT=$(DEV_DIR) build

## install      : build into installation directory on server.
install :
	make SITE=$(INSTALL_URL) OUT=$(INSTALL_DIR) build

## links        : check links.
#  Depends on linklint, an HTML link-checking module from http://www.linklint.org/,
#  which has been put in bin/linklint.
links :
	bin/linklint -doc /tmp/site-links -textonly -root _site /@

## missing      : which instructors don't have biographies?
missing :
	@python bin/check_missing_instructors.py config/badges_config.yml _includes/people/*.html

## sterile      : *really* clean up.
sterile : clean
	rm -f $(GENERATED)

## valid        : check validity of HTML.
#  Depends on xmllint being installed.  Ignores entity references.
valid :
	xmllint --noout $$(find _site -name '*.html' -print) 2>&1 | python bin/unwarn.py

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
