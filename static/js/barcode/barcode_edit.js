/**
 * Created by Dominic Fitzgerald on 10/28/15.
 */
$(document).ready(function(){
    $('#submit_edit').click(function(){
        $('#barcode_edit_form').submit();
    });

    $('#submit_delete').click(function(){
        if($(this).data('clicked') == '0'){
            $(this).text('Click again to delete');
            $(this).data('clicked', '1');
        }else if($(this).data('clicked') == '1'){
            $('#barcode_delete_form').submit();
        }
    });
});