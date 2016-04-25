
# # # # #

# Import Views
AppLayout = require './views/layout'
RoombaView = require './views/roomba'

# # # # #

$(document).on 'ready', => Layout.show new RoombaView()
