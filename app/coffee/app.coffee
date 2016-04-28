
# # # # #

# Import Views
AppLayout = require './views/layout'
RoombaView = require './views/roomba'

# # # # #

$(document).on 'ready', => AppLayout.show new RoombaView()
