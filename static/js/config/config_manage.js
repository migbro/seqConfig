/**
 * Created by Dominic Fitzgerald on 11/11/15.
 */
$(document).ready(function(){
    $('.caret-down').click(function(){
        var state = $(this).data('state');
        if(state == 'down'){
            $(this).removeClass('fa-caret-down').addClass('fa-caret-up').data('state', 'up')
                .parent().parent().next('tr.seq-config-config-description').first().show();
        }else{
            $(this).removeClass('fa-caret-up').addClass('fa-caret-down').data('state', 'down')
                .parent().parent().next('tr.seq-config-config-description').first().hide();
        }
    });
});