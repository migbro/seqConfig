/**
 * Created by Dominic Fitzgerald on 10/29/15.
 */
$(document).ready(function(){
    $('#lane-count-select').select2({
        minimumResultsForSearch: Infinity
    }).change(function(){
        var numLanes = $(this).val();
        var $lanesSection = $('#lanes-section');
        $.get('/seq-config/ajax/config/lane/' + numLanes + '/', function(data){
            $lanesSection.empty();
            $lanesSection.append($(data));
        });
    }).change();

    $('#id_runtype').select2({
        minimumResultsForSearch: Infinity
    });

    $('.btn-submit').click(function(){
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
        $('form').submit();
    }).tooltip({
        title: 'Multiple Barcodes exist within a Lane',
        trigger: 'manual'
    });
});