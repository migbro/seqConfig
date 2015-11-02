/**
 * Created by Dominic Fitzgerald on 10/29/15.
 */
$(document).ready(function(){

    $('input.num-libs').change(function(){
        var $numLibsInput = $(this);
        var numLibsExist = $numLibsInput.data('libs-exist');
        var numLibsRequest = $numLibsInput.val();
        var lane = $numLibsInput.data('lane');

        if(numLibsRequest < 1) return;

        var $librarySection = $('#library-section' + lane);
        if(numLibsExist < numLibsRequest){ // Add libraries
            var start = parseInt(numLibsExist) + 1;
            var stop = numLibsRequest;
            $.get('/seqConfig/ajax/config/library/' + start + '/' + stop + '/' + lane + '/', function(data){
                $librarySection.append($(data));
                $numLibsInput.data('libs-exist', numLibsRequest);
            });
        }else if(numLibsExist > numLibsRequest){ // Remove libraries
            $librarySection.children().each(function(){
                if($(this).data('n') > numLibsRequest){
                    $(this).remove();
                }
            });
            $numLibsInput.data('libs-exist', numLibsRequest);
        }
    }).change();
});