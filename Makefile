# Base URL and installation directory for development version on server.
DEV_URL = dev.software-carpentry.org
DEV_DIR = $(HOME)/dev.software-carpentry.org

# Base URL and installation directory for installed version on server.
INSTALL_URL = software-carpentry.org
INSTALL_DIR = $(HOME)/software-carpentry.org

#-------------------------------------------------------------------------------

# Source files in root directory.
SRC_ROOT = $(wildcard ./*.html)

# Source files of blog posts.  Does *not* include the index file so
# that our preprocessor doesn't try to harvest data from it.
SRC_BLOG = $(wildcard ./blog/????/??/*.html)

# Source files of archived bootcamp pages.  Does *not* include the
# main bootcamp index file so that our preprocessor doesn't try to
# harvest data from it.
SRC_BOOTCAMP = $(wildcard ./bootcamps/????-??-*/index.html)

# Source files for badge pages.
SRC_BADGES = ./badges/index.html

# Source files for Version 3 lessons.
SRC_V3 = $(wildcard ./v3/*.html)

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
    $(SRC_ABOUT) \
    ./blog/index.html $(SRC_BLOG) \
    ./bootcamps/index.html ./bootcamps/operations.html $(SRC_BOOTCAMPS) \
    $(SRC_BADGES) \
    $(SRC_V3) \
    $(SRC_V4) \
    $(SRC_LAYOUT) \
    $(SRC_INCLUDES)

# All source configuration files.
SRC_CONFIG = standard_config.yml airports_config.yml badges_config.yml

# All files generated during the build process.
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
	@python bin/authors.py $(SRC_BLOG) | cut -d : -f 1

## categories : list all blog category names.
categories :
	@python bin/categories.py $(SRC_BLOG) | cut -d : -f 1

## check      : build locally into _site directory for checking
check :
	make SITE=$(PWD)/_site OUT=$(PWD)/_site build

## dev        : build into development directory for sharing
dev :
	make SITE=$(DEV_URL) OUT=$(DEV_DIR) build

## install    : build into installation directory for sharing
install :
	make SITE=$(INSTALL_URL) OUT=$(INSTALL_DIR) build

## clean      : clean up
clean :
	rm -rf $(GENERATED) _site $$(find . -name '*~' -print)

#-------------------------------------------------------------------------------

# build : compile site into $(OUT) with $(SITE) as Software Carpentry base URL
build : $(OUT)/bootcamps.ics $(OUT)/feed.xml $(OUT)/.htaccess $(OUT)/img/main_shadow.png

# Copy the .htaccess file.
$(OUT)/.htaccess : ./_htaccess
	@mkdir -p $$(dirname $@)
	cp $< $@

# Make the bootcamp calendar file.
$(OUT)/bootcamps.ics : ./bin/calendar.py $(OUT)/index.html
	@mkdir -p $$(dirname $@)
	python ./bin/calendar.py -o $(OUT) -s $(SITE)

# Make the blog RSS feed file.
$(OUT)/feed.xml : ./bin/feed.py $(OUT)/index.html
	@mkdir -p $$(dirname $@)
	python ./bin/feed.py -o $(OUT) -s $(SITE)

# Make the site pages (including blog posts).
$(OUT)/index.html : _config.yml $(SRC_PAGES)
	jekyll build -d $(OUT)

# Make the Jekyll configuration file by adding harvested information to a fixed starting point.
_config.yml : ./bin/preprocess.py $(SRC_CONFIG) $(SRC_BLOG) $(SRC_BOOTCAMP)
	python ./bin/preprocess.py -o $(OUT) -s $(SITE)

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
