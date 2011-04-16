///////
//   request some overall data async from server.
//   should've remove some ui modules...but that's ok, probably.
////


$(function(){
    if( $('#pi').length == 1 ){
        $('#pi').load('/cache/pi', function(content){
            $('#pi-loading').hide();
            $('#pi').show();
        });
    }

    if( $('#hot').length == 1 ){
        $('#hot').load('/cache/nodes', function(content){
            $('#hot-loading').hide();
            $('#hot').show();
        });
    }
    
    if( $('#follower').length == 1 ){
        $('#follower').load('/cache/follower', function(content){
            $('#follower-loading').hide();
            $('#follower').show();
        });
    }
    
    if($.browser.webkit){
        $.getScript('/static/js/sticky.notes.js');
        var len = $('#navigation ul li').length;
        $('#navigation ul li:eq('+(len-2)+')').after('<li><a href="javascript:newNote()" class="white">笔记</a></li>');
    }
    
    $('#f-textarea').live('focus, click', function() {
        var o = $(this),
        expand_height = "52px";
        o.animate({height : expand_height}, 100, function() {
            o.select().focus();
        });
        $('#f-submit').fadeIn();
    });
    
    
    $('#follow-form').submit(function(){
        var text = $('#f-submit').val();

        $.post($(this).attr('action'), $(this).serialize(), function(data){
            if(data == 'ok'){
                new_msg = (text == '关注') ? '取消关注': '关注';
                $('#f-submit').val(new_msg);
                
                $.notifyBar({
                        html:'已经'+text,
                        close: true,
                        delay: 4000,
                        cls: 'success'
                    });
            }else{
                $.notifyBar({
                        html:'出现问题, 请稍后再试',
                        close: true,
                        delay: 4000,
                        cls: 'error'
                    });
            }

        });
        return false;
    });
    
    $('#like_form').submit(function(){
        var text = $('#like_op').text();
        
        $.post($(this).attr('action'), $(this).serialize(), function(data){
            if(data == 'ok'){
                new_msg = (text == '收藏') ? '取消收藏': '收藏';
                $('#like_op').text(new_msg);
                $.notifyBar({
                        html:'已经'+text,
                        close: true,
                        delay: 4000,
                        cls: 'success'
                    });
                
            }else{
                $.notifyBar({
                        html:'出现问题, 请稍后再试',
                        close: true,
                        delay: 4000,
                        cls: 'error'
                    });
            }
            return false;
        });
        
        return false;
        
    });
    
    
});


function like_it(){
    $('#like_form').submit();
}