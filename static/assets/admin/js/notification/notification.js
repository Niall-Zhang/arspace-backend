$(document).ready(function(){
    $('#notification-form').validate({
        rules: {
            'notification-title': {
                required: true,
                maxlength: 50
            },
            'notification-message': {
                required: true,
            }
        },
        messages: {
            'notification-title': {
                required: "Title is required.",
                maxlength: "Title cannot be more than 50 characters."
            },
            'notification-message': {
                required: "Message is required.",
            }
        }
    });

    $('#notification-button').on('click', function(event){
        event.preventDefault();

        if ($('#notification-form').valid()) {
            var notification_title = $('input[name="notification-title"]').val();
            var notification_message = $('#notification-message').val();
            var csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
            $.ajax({
                url: SEND_MESSAGE_TO_TOPIC_URL,
                method: 'POST', 
                data: {
                    'name': notification_title,
                    'message': notification_message,
                    'csrfmiddlewaretoken': csrf_token 
                },
                success: function (data) {
                    if(data.success){
                        toastr.success(data.message);
                        $('#notification-form')[0].reset();
                    }else{
                        toastr.error(data.error)
                    }
                }
            });
        }
    });
});
