
class ExampleView extends Marionette.ItemView
  template: require './templates/example'

  onShow: ->
    console.log 'You can put some Javascript to run in this view.'

module.exports = ExampleView
