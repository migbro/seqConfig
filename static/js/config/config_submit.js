/**
 * Created by Dominic Fitzgerald on 10/29/15.
 */
$(document).ready(function(){
    $('#lane-count-select').select2({
        minimumResultsForSearch: Infinity
    }).change(function(){
        var numLanes = $(this).val();
        var $lanesSection = $('#lanes-section');
        $.get('/seqConfig/ajax/config/lane/' + numLanes + '/', function(data){
            $lanesSection.empty();
            $lanesSection.append($(data));
        });
    }).change();

    $('#id_runtype').select2({
        minimumResultsForSearch: Infinity
    });

    $('.btn-submit').click(function(){
        $('form').submit();
    });
});