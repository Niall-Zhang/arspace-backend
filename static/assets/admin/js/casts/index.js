$(document).ready(function () {
    let clubs_list_table = $(document).find('#casts-list').dataTable({
        serverSide: true,
        sAjaxSource: admin_clubs_list,
        columns: [
            {name: "name", data: 1},
            {
                name:"image",
                data: 2,
                render: function (data, type, row) {
                    if (type === 'display') {
                        return `<img src="${GCP_BUCKET_URL}${row[2]}" class="rounded me-3" height="48">`;
                    }
                    return data;
                }
            },
            {name: "description", data: 3},
            {
                name: "created_at",
                data: 4,
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
                        return `<a href="casts/edit/${row[0]}" class="action-icon editBtn"> <i class="mdi mdi-square-edit-outline"></i></a>
                        <a href="javascript:void(0);" class="action-icon confirmDeletion" data-uuid="${row[0]}"> <i class="mdi mdi-delete" data-bs-toggle="modal"></i></a>`;
                    }
                    return data;
                }
            }
        ],
    });    

    // Open Confirm Delete Modal
    $(document).on("click",".confirmDeletion",function(){
        let uuid = $(this).attr("data-uuid");
        if(uuid){
            $(".deleteBtn").attr("data-uuid",uuid);
            $("#cast-delete-alert-modal").modal('toggle');
        }
    });

    // Delete
    $(document).on("click",".deleteBtn",function(){
        let uuid = $(this).attr("data-uuid");
        $.ajax({
            url: `/admin/casts/delete/${uuid}`,  
            type: 'POST',
            data:{"csrfmiddlewaretoken":$('input[name="csrfmiddlewaretoken"]').val()},
            success: function(data) {
                if(data.success){
                    clubs_list_table.api().ajax.reload();
                    toastr.success(data.message);
                    window.location.href = admin_dashboard;
                }else{
                    toastr.error(data.error);
                }
            }  
        });
    });
});