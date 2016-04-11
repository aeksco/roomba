# # # # #

class Roomba extends Backbone.Model
  urlRoot: 'roomba'

  sendAction: (action) ->
    @fetch({ data: { action: action } })

# # # # #

class RoombaController extends Marionette.ItemView
  template: require './templates/example'

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

  invokeAction: (e) ->
    e.preventDefault()
    el = @$(e.currentTarget)
    action = @$(e.currentTarget).data().action
    @model.sendAction(action)

# # # # #

module.exports = RoombaController
