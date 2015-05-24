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

# All files generated for the build process.
GENERATED = \
	./_dashboard_cache.yml \
	./_workshop_cache.yml

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

## site         : build locally into _site directory for checking.
site :
	make SITE=$(PWD)/_site OUT=$(PWD)/_site build

## install      : build into installation directory on server.
install :
	make SITE=$(INSTALL_URL) OUT=$(INSTALL_DIR) build

## check        : check consistency of various things.
check :
	python3 bin/check-workshops.py config/workshops.yml config/archived.yml

## clean        : clean up.
clean :
	@rm -rf \
	_config.yml \
	$(GENERATED) \
	_site \
	bib/*.aux bib/*.bbl bib/*.blg bib/*.log \
	_includes/recent_blog_posts.html \
	$$(find . -name '*~' -print)

## dev          : build into development directory on server.
dev :
	make SITE=$(DEV_URL) OUT=$(DEV_DIR) build

## ----------------------------------------

## archive      : collect and archive workshop information from GitHub and store in local cache.
archive :
	cp $(CONFIG_DIR)/archived.yml ./_workshop_cache.yml
	python3 bin/workshops.py -v -t \
	    -i $(CONFIG_DIR)/workshops.yml \
	    -o ./_workshop_cache.yml \
	    --archive $(CONFIG_DIR)/archived.yml

## cache        : collect workshop information from GitHub and store in local cache.
cache : $(GENERATED)

./_workshop_cache.yml : config/workshops.yml
	cp $(CONFIG_DIR)/archived.yml ./_workshop_cache.yml
	python3 bin/workshops.py -v -t \
	    -i $(CONFIG_DIR)/workshops.yml \
	    -o ./_workshop_cache.yml

./_dashboard_cache.yml :
	python3 bin/make-dashboard.py ./git-token.txt ./_dashboard_cache.yml

## ----------------------------------------

## biblio       : make HTML and PDF of bibliography.
# Have to cd into 'bib' because bib2xhtml expects the .bst file in
# the same directory as the .bib file.
biblio : bib/${SWC_BIB}.tex bib/software-carpentry.bib
	cd bib && pdflatex $(SWC_BIB) && bibtex $(SWC_BIB) && pdflatex $(SWC_BIB)
	cd bib && ../bin/bib2xhtml software-carpentry.bib ./bib.html && dos2unix ./bib.html

## authors      : list all blog post authors.
authors :
	@python3 bin/list-authors.py $(SRC_BLOG) | cut -d : -f 1

## badge-dates  : list dates of all instructor badges.
badge-dates :
	@python3 bin/list-badge-dates.py badges/instructor/*.json

## categories   : list all blog category names.
categories :
	@python3 bin/list-categories.py $(SRC_BLOG) | cut -d : -f 1

categories_n :
	@python3 bin/list-categories.py -n $(SRC_BLOG)

## instructors  : list instructors from cached workshop info.
instructors : _workshop_cache.yml
	@python3 bin/list-instructors.py < _workshop_cache.yml

## urls         : list workshop URLs from cached workshop info.
urls : _workshop_cache.yml
	@python3 bin/list-urls.py < _workshop_cache.yml

## missing      : which instructors don't have biographies?
missing :
	@python3 bin/check-missing-instructors.py config/badges.yml _includes/people/*.html

## links        : check links.
#  Depends on linklint, an HTML link-checking module from http://www.linklint.org/,
#  which has been put in bin/linklint.
links :
	bin/linklint -doc /tmp/site-links -textonly -root _site /@

## valid        : check validity of HTML.
#  Depends on xmllint being installed.  Ignores entity references.
valid :
	xmllint --noout $$(find _site -name '*.html' -print) 2>&1 | python3 bin/unwarn.py

#-------------------------------------------------------------------------------

# build : compile site into $(OUT) with $(SITE) as Software Carpentry base URL
build : $(OUT)/workshops.ics $(OUT)/feed.xml $(OUT)/workshop-feed.xml $(OUT)/.htaccess $(OUT)/img/main_shadow.png

# Copy the .htaccess file.
$(OUT)/.htaccess : ./_htaccess
	@mkdir -p $$(dirname $@)
	cp $< $@

# Make the workshop calendar file.
$(OUT)/workshops.ics : ./bin/make-calendar.py $(OUT)/index.html
	@mkdir -p $$(dirname $@)
	python3 ./bin/make-calendar.py -o $(OUT) -s $(SITE)

# Make the blog RSS feed file.
$(OUT)/feed.xml : ./bin/make-rss-feed.py $(OUT)/index.html
	@mkdir -p $$(dirname $@)
	python3 ./bin/make-rss-feed.py -o $(OUT) -s $(SITE)

# Make the workshop RSS feed file.
$(OUT)/workshop-feed.xml : ./bin/make-workshop-rss-feed.py $(OUT)/index.html
	@mkdir -p $$(dirname $@)
	python3 ./bin/make-workshop-rss-feed.py -o $(OUT) -s $(SITE)

# Make the site pages (including blog posts).
$(OUT)/index.html : _config.yml $(SRC_HTML)
	jekyll build -d $(OUT)

# Make the Jekyll configuration file by adding harvested information to a fixed starting point.
_config.yml : ./bin/preprocess.py $(SRC_CONFIG) $(SRC_BLOG) $(SRC_INCLUDES) $(GENERATED)
	python3 ./bin/preprocess.py -c ./config -o $(OUT) -s $(SITE)
