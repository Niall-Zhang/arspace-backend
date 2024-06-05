$(document).ready(function () {
    let tickets_list_table = $(document).find('#tickets-list').dataTable({
        serverSide: true,
        sAjaxSource: admin_tickets_list,
        columns: [
            {name: "name", data: 1},
            {name: "price", data: 2},
            {name: "left", data: 3},
            {name: "units", data: 4},
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
                        return `<a href="tickets/edit/${row[0]}" class="action-icon editBtn"> <i class="mdi mdi-square-edit-outline"></i></a>
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
            $("#ticket-delete-alert-modal").modal('toggle');
        }
    });

    // Delete
    $(document).on("click",".deleteBtn",function(){
        let uuid = $(this).attr("data-uuid");
        $.ajax({
            url: `/admin/tickets/delete/${uuid}`,  
            type: 'POST',
            data:{"csrfmiddlewaretoken":$('input[name="csrfmiddlewaretoken"]').val()},
            success: function(data) {
                if(data.success){
                    tickets_list_table.api().ajax.reload();
                    toastr.success(data.message);
                    window.location.href = admin_dashboard;
                }else{
                    toastr.error(data.error);
                }
            }  
        });
    });
});