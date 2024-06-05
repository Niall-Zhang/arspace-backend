$(document).ready(function(){ 

    $('#generate-free-ticket').on('click', function(e){
        e.preventDefault();
        let event = $('#event').val();
        let ticket = $('#ticket').val();
        let user_uuid = $(this).attr("data-uuid");
        if(event && ticket && user_uuid){
            $.ajax({
                url: generate_ticket_url,
                method: 'POST', 
                data:{"csrfmiddlewaretoken":$('input[name="csrfmiddlewaretoken"]').val(),event,ticket,user_uuid},
                success: function (data) {
                    if(data.success){
                        toastr.success(data.message);
                        $('#generate-ticket')[0].reset();
                    }else{
                        toastr.error(data.error)
                    }
                }
            });
        }else{
            toastr.error("Please choose event or ticket first.")
        }
    });
});