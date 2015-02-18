jQuery(function ($) {

Annotator.Plugin.StoreLogger = function (element) {
  return {
    pluginInit: function () {
      this.annotator
          .subscribe("annotationCreated", function (annotation) {
            console.info("The annotation: %o has just been created!", annotation)
          })
          .subscribe("annotationUpdated", function (annotation) {
            console.info("The annotation: %o has just been updated!", annotation)
          })
          .subscribe("annotationDeleted", function (annotation) {
            console.info("The annotation: %o has just been deleted!", annotation)
          });

var select = $('<ol id="my-select" />')
$('#annotator-field-0').after(select);

var selectValues = { "1": "test 1", "2": "test 2" };
$.each(selectValues, function(key, value) {   
     $('#my-select')
         .append($('<li class="ui-widget-content" />')
         .text(value)); 
});

$('#my-select').selectable();

    }
  }
};

var content = $('body').annotator();
content.annotator('addPlugin', 'StoreLogger');

});
