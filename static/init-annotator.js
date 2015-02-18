function init(l) {

    Annotator.Plugin.Tagger = function (element) {
        return {
            pluginInit: function () {
                var textarea = $('#annotator-field-0');
                textarea.attr('readonly', true);
                textarea.attr('placeholder', '');

                var e = $('<ol id="my-select" />')
                textarea.after(e);
                var select = $('#my-select')
    
                $.each(l, function(key, value) {   
                    select.append($('<li class="ui-widget-content" />').text(value));
                });
    
                select.selectable({
                    selected: function( event, ui ) {
                        textarea.val(ui.selected.textContent);
                    }
                });
            }
        }
    };
    
    var content = $('body').annotator();
    content.annotator('addPlugin', 'Tagger');
}
