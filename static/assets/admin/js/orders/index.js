$(document).ready(function () {
    let orders_list_table = $(document).find('#orders-list').dataTable({
        serverSide: true,
        sAjaxSource: admin_orders_list,
        columns: [
            {name: "user", data: 1},
            {name: "event", data: 2},
            {name: "total", data: 3},
            {name: "status", data: 4},
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
                        return `<a href="orders/${row[0]}" class="action-icon editBtn"> <i class="mdi mdi-eye"></i></a>`;
                    }
                    return data;
                }
            }
        ],
    });
});