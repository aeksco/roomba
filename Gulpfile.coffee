# TODO - gulp_common
gulp        = require 'gulp'
livereload  = require 'gulp-livereload'
webserver   = require 'gulp-webserver'
plumber     = require 'gulp-plumber'

# Import Paths
paths = require './gulp/paths.coffee'

# Environments -> 'development' || 'production'
environment = 'development'
gulp.task 'set-production', -> environment = 'production'

# Import tasks
require './gulp/coffee.coffee'
require './gulp/copy.coffee'
require './gulp/concat.coffee'
require './gulp/sass.coffee'
require './gulp/jade.coffee'

# Webserver Task
gulp.task 'webserver', ->
  gulp.src paths.dest
    .pipe webserver
      port: 8080
      open: true

# Watch & Live Reload
gulp.task 'watch', ->
  livereload.listen
    host: 'localhost'
    port: 4000
    start: true
    reloadPage: paths.dest + 'index.html'

  gulp.watch paths.src + 'coffee/**', ['coffee']
  gulp.watch paths.src + 'coffee/**/*.jade', ['coffee']
  gulp.watch paths.src + 'stylesheets/**/*.sass', ['sass']
  gulp.watch paths.src + '**/*.jade', ['jade']

# Task declarations
gulp.task 'default', ['sass', 'jade', 'copy', 'coffee', 'concat', 'watch', 'webserver']
