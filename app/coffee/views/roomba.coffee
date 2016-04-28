# # # # #

# class SerialPort extends Backbone.Model

# class SerialPorts extends Backbone.Collection
#   model: SerialPort
#   url: '/serial_ports'

# # # # #

class Roomba extends Backbone.Model
  urlRoot: 'roomba'

  sendAction: (action) ->
    @fetch({ data: { action: action } })

# # # # #

class RoombaView extends Marionette.LayoutView
  template: require './templates/roomba'

  ui:
    action: '[data-click=action]'

  events:
    'click @ui.action': 'invokeAction'

  modelEvents:
    'sync':   'onSync'
    'error':  'onError'

  onSync: ->
    # console.log 'SYNCED'

  onError: ->
    # console.log 'ON ERROR'

  initialize: ->
    @model = new Roomba()
    # @collection = new SerialPorts()
    # @collection.fetch()

  invokeAction: (e) ->
    e.preventDefault()
    el = @$(e.currentTarget)
    action = @$(e.currentTarget).data().action
    @model.sendAction(action)

# # # # #

module.exports = RoombaView
