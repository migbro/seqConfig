/**
 * Created by Dominic Fitzgerald on 10/29/15.
 */
$(document).ready(function(){
    $('#barcode-select').select2({
        minimumResultsForSearch: Infinity
    }).change(function())

    $('#id_barcode').select2({
        minimumResultsForSearch: Infinity
    });

    $('.btn-submit').click(function(){
        $('form').submit();
    });
});