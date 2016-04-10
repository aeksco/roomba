# TODO - require common?
gulp        = require 'gulp'
concat      = require 'gulp-concat'
plumber     = require 'gulp-plumber'
livereload  = require 'gulp-livereload'

# Import Paths
paths = require './paths.coffee'

# Concat
gulp.task 'concat', ->
  stream = gulp.src([
      paths.components + 'jquery/dist/jquery.js',
      paths.components + 'underscore/underscore.js',
      paths.components + 'backbone/backbone.js',
      paths.components + 'backbone.babysitter/lib/backbone.babysitter.js',
      paths.components + 'backbone.wreqr/lib/backbone.wreqr.js',
      paths.components + 'backbone.marionette/lib/core/backbone.marionette.js',
      paths.components + 'bootstrap/dist/js/bootstrap.min.js'
    ])
    .pipe plumber()
    .pipe concat("vendor.js")
    .pipe livereload()

  # TODO - Env.
  # stream.pipe uglify() if environment == 'production'
  stream.pipe gulp.dest paths.dest + 'js/'
