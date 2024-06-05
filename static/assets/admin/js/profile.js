$(document).ready(function(){
    // Validate change password form
    $(document).on('click','#updatePasswordBtn',function(){
        $("#update-password-form").validate({
            rules: {
                password: {required: true,minlength: 6},
                confirm_password: {
                    minlength: 6,
                    required: true,
                    equalTo: "#password"
                }
            },
            messages: {
                confirm_password: "Confirm password must be match with new password.",
            }
        });
    });

    // Delete User Image
    $(document).on('click','.deleteUserImage',function(){
        let uuid = $(this).attr("data-uuid");
        $.ajax({
            url: `/admin/users/delete/${uuid}/image`,  
            type: 'POST',
            data:{"csrfmiddlewaretoken":$('input[name="csrfmiddlewaretoken"]').val()},
            success: function(data) {
                if(data.success){
                    toastr.success(data.message);
                    setTimeout(function() {
                        window.location.reload();
                    }, 800);
                }else{toastr.error(data.error);}
            }  
        });
    });
});