$(function(){
    $('input').click(function(){
        var model = $('#model').val();
        $.ajax({
            url: '/model',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response){
                console.log(response);
            },
            error: function(error){
                console.log(error);
            }
        });
    });
});