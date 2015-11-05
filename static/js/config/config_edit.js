/**
 * Created by Dominic Fitzgerald on 10/28/15.
 */
$(document).ready(function(){
    $('#submit_edit').click(function(){
        $('#config_edit_form').submit();
    });

    $('.approve_btn').click(function(){
        if($(this).data('clicked') === undefined){
            $('#config_approve_form').submit();
        }else{
            if($(this).data('clicked') == '0'){
                $(this).text('Click again to unapprove');
                $(this).data('clicked', '1');
            }else if($(this).data('clicked') == '1'){
                $('#config_approve_form').submit();
            }
        }
    });

    $('#submit_delete').click(function(){
        if($(this).data('clicked') == '0'){
            $(this).text('Click again to delete');
            $(this).data('clicked', '1');
        }else if($(this).data('clicked') == '1'){
            $('#config_delete_form').submit();
        }
    });

    $('#lane-count-select').select2({
        minimumResultsForSearch: Infinity
    }).change(function(){
        var $lanesSection = $('#lanes-section');
        var numLanes = $(this).val();
        if($lanesSection.data('gotlanes') == 'no'){
            var configId = $('#config_id').val();
            $.get('/seqConfig/ajax/config/lane_edit/' + numLanes + '/' + configId + '/', function(data){
                $lanesSection.empty();
                $lanesSection.append($(data));
            });
        }else{
            $.get('/seqConfig/ajax/config/lane/' + numLanes + '/', function(data){
                $lanesSection.empty();
                $lanesSection.append($(data));
            });
        }

    }).change();

    $('#id_runtype').select2({
        minimumResultsForSearch: Infinity
    });
});