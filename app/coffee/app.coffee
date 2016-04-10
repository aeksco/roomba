
# Configuration
Layout = require './config/layout'

# # # # #

# Import Views
ExampleView = require './views/example'

# # # # #

$(document).on 'ready', =>
  console.log 'Document Ready'

  Layout.show new ExampleView()
