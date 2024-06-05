$(document).ready(function () {
    let users_list_table = $(document).find('#users-list').dataTable({
        serverSide: true,
        sAjaxSource: admin_users_list,
        columns: [
            {name: "email", data: 1},
            {name: "address", data: 2},
            {
                name:"image",
                data: 3,
                render: function (data, type, row) {
                    if (type === 'display') {
                        return `<img src="${GCP_BUCKET_URL}${row[3]}" class="rounded me-3" height="48">`;
                    }
                    return data;
                }
            },
            {
                name:"type",
                data: 4,
                render: function (data, type, row) {
                    if (type === 'display') { 
                        let user = row[4] ? "Club" : "User";
                        return `<span class="badge bg-primary">${user}</span>`;
                    }
                    return data;
                }
            },
            {
                name:"status",
                data: 4,
                render: function (data, type, row) {
                    if (type === 'display') {
                        let checked;
                        if(row[5] === true){
                            checked = "checked";
                        }
                        return `<input type="checkbox" id="status_${row[0]}"  ${checked}  data-switch="bool" class="user_status" data-user_uuid="${row[0]}">
                        <label for="status_${row[0]}" data-on-label="Active" data-off-label="InActive"></label>`;
                    }
                    return data;
                }
            },
            {
                name: "created_at",
                data: 5,
                render: function (data, type, row) {
                    if (type === 'display') {
                        var date = new Date(data);
                        return date.toLocaleString();
                    }
                    return data;
                }
            },
            {
                name:"action",
                data: null,
                render: function (data, type, row) {
                    if (type === 'display') {
                        // let editable = row[4] ? row[4] : false;
                        // if(editable){
                        //     return `<a href="/admin/users/edit/${row[0]}" class="action-icon editBtn"> <i class="mdi mdi-square-edit-outline"></i></a>
                        //     <a href="javascript:void(0);" class="action-icon confirmDeletion" data-uuid="${row[0]}"> <i class="mdi mdi-delete" data-bs-toggle="modal"></i></a>`;
                        // }
                        return `<a href="users/${row[0]}" class="action-icon editBtn"> <i class="mdi mdi-eye"></i></a>
                        <a href="/admin/users/edit/${row[0]}" class="action-icon editBtn"> <i class="mdi mdi-square-edit-outline"></i></a>
                            <a href="javascript:void(0);" class="action-icon confirmDeletion" data-uuid="${row[0]}"> <i class="mdi mdi-delete" data-bs-toggle="modal"></i></a>`;
                    }
                    return data;
                }
            }
        ],
    });
    
    // Change User Status
    $(document).on("change",".user_status",function(){
        let status = false;
        if($(this).is(':checked')){status = true;}
        let user_uuid = $(this).data("user_uuid");
        $.ajax({
            url: `/admin/users/status/${user_uuid}`,  
            type: 'POST',
            data:{"csrfmiddlewaretoken":$('input[name="csrfmiddlewaretoken"]').val(),status,user_uuid},
            success: function(data) {
                if(data.success){
                    toastr.success(data.message); 
                }else{
                    toastr.error(data.error);
                }
            }  
        });
    });

    $(document).on("click",".confirmDeletion",function(){
        let uuid = $(this).attr("data-uuid");
        if(uuid){
            $(".deleteBtn").attr("data-uuid",uuid);
            $("#user-delete-alert-modal").modal('toggle');
        }
    });

    // Delete Type After Confirmation
    $(document).on('click','.deleteBtn',function(){
        let uuid = $(this).attr("data-uuid");
        $.ajax({
            url: `/admin/users/delete/${uuid}`,  
            type: 'POST',
            data:{"csrfmiddlewaretoken":$('input[name="csrfmiddlewaretoken"]').val()},
            success: function(data) {
                if(data.success){
                    users_list_table.api().ajax.reload();
                    toastr.success(data.message);
                    setTimeout(function() {
                        window.location.reload();
                    }, 1000);
                }else{
                    toastr.error(data.error);
                }
            }  
        });
    });
});