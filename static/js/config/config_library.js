/**
 * Created by Dominic Fitzgerald on 11/2/15.
 */
$(document).ready(function(){
    $('.barcode-select').select2({
        minimumResultsForSearch: 10,
        placeholder: 'Select Barcode'
    }).change(function(){
        var barcodeSeq = $(this).find('option:selected').data('barcodeseq');
        var $barcodeSeqCol = $(this).parent().next().first();
        $barcodeSeqCol.text(barcodeSeq);
    }).change();

    $('.bionimbus-id').off('change').change(function(){
        var $this = $(this);
        $.getJSON('/seq-config/ajax/bionimbus/project_by_bionimbus_bid/' + $(this).val().trim() + '/', function(dataJSON){
            $this.parent().next('.project-name').first()
                .removeClass('animated flipInX')
                .addClass('animated flipInX')
                .text(dataJSON.project_name);
        });
    }).change();
});