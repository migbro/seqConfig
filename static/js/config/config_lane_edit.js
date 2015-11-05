/**
 * Created by Dominic Fitzgerald on 10/29/15.
 */
$(document).ready(function(){

    $('.lanetab').each(function(){
        var $lanesSection = $('#lanes-section');
        if($lanesSection.data('gotlanes') == 'yes'){
            $('input.num-libs').change();
            return;
        }
        var laneId = $(this).data('laneid');
        var laneNum = $(this).data('lanenum');
        var numLibs = $(this).data('numlibs');
        var $librarySection = $('#library-section' + laneNum);
        var $numLibsInput = $(this).find('input.num-libs').first();
        $.get('/seqConfig/ajax/config/library_edit/' + laneId + '/', function(data){
            $librarySection.append($(data));
            $numLibsInput.attr('data-libs-exist', numLibs);
            $lanesSection.data('gotlanes', 'yes');
        });
    });

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
    });
});