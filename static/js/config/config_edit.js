/**
 * Created by Dominic Fitzgerald on 10/28/15.
 */
$(document).ready(function(){
    $('#submit_edit').click(function(){
        var barcodesUsed = {};
        var multipleBarcodes = false;
        $('.barcode-select').each(function(){
            var lane = $(this).data('lane');
            if(barcodesUsed[lane] === undefined){
                barcodesUsed[lane] = {};
            }
            if(barcodesUsed[lane][$(this).val()] !== undefined && $(this).val() !== ''){
                multipleBarcodes = true;
            }
            barcodesUsed[lane][$(this).val()] = 0;
        });
        if(multipleBarcodes){
            var submitBtn = $(this);
            submitBtn.tooltip('show');
            window.setTimeout(function(){
                submitBtn.tooltip('hide');
            }, 3000);
            return false;
        }
        $('#config_edit_form').submit();
    }).tooltip({
        title: 'Multiple Barcodes exist within a Lane',
        trigger: 'manual'
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
    }).tooltip({
        title: 'Save Changes Before Approving',
        trigger: 'hover'
    });

    $('.release_btn').click(function(){
        $('#config_release_form').submit();
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
            $.get('/seq-config/ajax/config/lane_edit/' + numLanes + '/' + configId + '/', function(data){
                $lanesSection.empty();
                $lanesSection.append($(data));
            });
        }else{
            $.get('/seq-config/ajax/config/lane/' + numLanes + '/', function(data){
                $lanesSection.empty();
                $lanesSection.append($(data));
            });
        }
    }).change();

    $('#id_runtype').select2({
        minimumResultsForSearch: Infinity
    });
});