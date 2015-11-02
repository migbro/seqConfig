/**
 * Created by Dominic Fitzgerald on 11/2/15.
 */
$(document).ready(function(){
    $('.submitter-select').select2({
        minimumResultsForSearch: Infinity
    });

    $('.barcode-select').select2({
        minimumResultsForSearch: 5
    }).change(function(){
        var barcodeSeq = $(this).find('option:selected').data('barcodeseq');
        var $barcodeSeqCol = $(this).parent().next().first();
        $barcodeSeqCol.text(barcodeSeq);
    }).change();
});